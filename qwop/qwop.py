"""
qwop module provides utilities for working with QIR programs in Python.
"""

from abc import ABCMeta, abstractmethod
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Literal, Optional, Set, Union, Generic, TypeVar, overload
TOutput = TypeVar('TOutput')

import pyqir_parser as pqp

# Check if various frameworks are installed.
try:
    import qiskit as qk
except ImportError:
    qk = None

try:
    import qutip as qt
    import qutip.qip.circuit
    import qutip.qip.operations
except ImportError:
    qt = None

try:
    import cirq as cirq
except ImportError:
    cirq = None

# General utility functions
def _resolve_id(value: Any, default: str = "unsupported") -> Union[int, str]:
    if hasattr(value, "id"):
        return value.id
    return default

def _resolve(value, in_):
    id = _resolve_id(value)
    if id not in in_:
        in_[id] = len(in_)
    return in_[id]

def is_circuit_like(block : pqp.QirBlock) -> bool:
    return all(
        isinstance(instruction, (pqp.QirQisCallInstr, pqp.QirQirCallInstr))
        for instruction in block.instructions
    )

class CircuitLikeExporter(Generic[TOutput], metaclass=ABCMeta):
    @abstractmethod
    def on_simple_gate(self, name, *qubits) -> None:
        pass

    @abstractmethod
    def on_measure(self, qubit, result) -> None:
        pass

    @abstractmethod
    def on_comment(self, text) -> None:
        pass

    @abstractmethod
    def export(self) -> TOutput:
        pass

    @abstractmethod
    def qubit_as_expr(self, qubit) -> str:
        pass

    @abstractmethod
    def result_as_expr(self, result) -> str:
        pass

@overload
def export_block(block: pqp.QirBlock, to: CircuitLikeExporter[TOutput]) -> Union[None, TOutput]: ...
@overload
def export_block(block: pqp.QirBlock, to: Literal["openqasm2"]) -> Union[None, str]: ...
if qk is not None:
    @overload
    def export_block(block: pqp.QirBlock, to: Literal["qiskit"]) -> Union[None, qk.Circuit]: ...
if cirq is not None:
    @overload
    def export_block(block: pqp.QirBlock, to: Literal["cirq"]) -> Union[None, cirq.Circuit]: ...
if qt is not None:
    @overload
    def export_block(block: pqp.QirBlock, to: Literal["qutip"]) -> Union[None, qt.qip.circuit.QubitCircuit]: ...

def export_block(block, to):
    if to == "openqasm2":
        exporter = OpenQasm20Exporter
    if qk is not None and to == "qiskit":
        exporter = QiskitExporter
    if cirq is not None and to == "cirq":
        exporter = CirqExporter
    if qt is not None and to == "qutip":
        exporter = QuTiPExporter
    else:
        # Assume to is an exporter
        exporter = to
    return exporter(block).export()

class OpenQasm20Exporter(CircuitLikeExporter[str]):
    header: List[str]
    lines: List[str]

    qubits: Dict[Any, Optional[int]]
    results: Dict[Any, Optional[int]]

    qreg = "q"
    creg = "c"
    qis_gate_mappings = {
        '__quantum__qis__x__body': 'x',
        '__quantum__qis__y__body': 'y',
        '__quantum__qis__z__body': 'z',
        '__quantum__qis__h__body': 'h',
        '__quantum__qis__cnot__body': 'CX'
    }

    def __init__(self, block : pqp.QirBlock):
        self.lines = []
        self.header = [
            f"// Generated from QIR block {block.name}.",
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
            ""
        ]
        self.qubits = dict()
        self.results = dict()
        self.block = block
        self._export_lines()

    def qubit_as_expr(self, qubit) -> str:
        id_qubit = _resolve_id(qubit)
        if id_qubit not in self.qubits:
            self.qubits[id_qubit] = len(self.qubits)
        return f"{self.qreg}[{self.qubits[id_qubit]}]"

    def result_as_expr(self, result) -> str:
        id_result = _resolve_id(result)
        if id_result not in self.results:
            self.results[id_result] = len(self.results)
        return f"{self.creg}[{self.results[id_result]}]"
    
    def on_comment(self, text) -> None:
        # TODO: split text into lines first.
        self.lines.append(f"// {text}")

    def on_simple_gate(self, name, *qubits) -> None:
        qubit_args = [self.qubit_as_expr(qubit) for qubit in qubits]
        self.lines.append(f"{name} {', '.join(map(str, qubit_args))};")

    def on_measure(self, qubit, result) -> None:
        self.lines.append(f"measure {self.qubit_as_expr(qubit)} -> {self.result_as_expr(result)};")
   
    def _export_lines(self) -> None:
        for inst in self.block.instructions:
            if inst.func_name in self.qis_gate_mappings:
                self.on_simple_gate(self.qis_gate_mappings[inst.func_name], *inst.func_args)

            # Reset requires nonstandard support.
            elif inst.func_name == "__quantum__qis__reset__body":
                self.on_comment("Requires nonstandard reset gate:")
                self.on_simple_gate("reset", *inst.func_args)

            # Measurements are special in OpenQASM 2.0, so handle them here.
            elif inst.func_name == "__quantum__qis__mz__body":
                target, result = inst.func_args
                self.on_measure(target, result)

            # Handle special cases of QIR functions as needed.
            elif inst.func_name == "__quantum__qir__read_result":
                self.on_comment(f"%{inst.output_name} = {self.result_as_expr(inst.func_args[0])}")

            else:
                self.on_comment("// Unsupported QIS operation:")
                self.on_comment(f"// {inst.func_name} {', '.join(map(str, inst.func_args))}")
        
    def export(self) -> str:
        declarations = []
        if self.qubits:
            declarations.append(
                f"qreg {self.qreg}[{len(self.qubits)}];"
            )
        if self.results:
            declarations.append(
                f"creg {self.creg}[{len(self.results)}];"
            )

        return "\n".join(
            self.header + declarations + self.lines
        )


#TODO: make a direct exporter, not through openqasm2
class QiskitExporter(CircuitLikeExporter["qk.QuantumCircuit"]):
    def __init__(self, block : pqp.QirBlock):
        self.oq2_exporter = OpenQasm20Exporter(block)
    def qubit_as_expr(self, qubit) -> str:
        return self.oq2_exporter.qubit_as_expr(qubit)
    def result_as_expr(self, result) -> str:
        return self.oq2_exporter.result_as_expr(result)
    def on_comment(self, text) -> None:
        return self.oq2_exporter.on_comment(text)
    def on_measure(self, qubit, result) -> None:
        return self.oq2_exporter.on_measure(qubit, result)
    def on_simple_gate(self, name, *qubits) -> None:
        return self.oq2_exporter.on_simple_gate(name, *qubits)
    def export(self) -> "qk.QuantumCircuit":
        return qk.QuantumCircuit.from_qasm_str(self.oq2_exporter.export())

class CirqExporter(CircuitLikeExporter["cirq.Circuit"]):
    pass

class QuTiPExporter(CircuitLikeExporter["qt.qip.circuit.QubitCircuit"]):
    actions: List[Callable[["qt.qip.circuit.QubitCircuit"], None]]

    qubits: Dict[Any, int]
    results: Dict[Any, int]

    gate_names = MappingProxyType({
        'x': 'X',
        'y': 'Y',
        'z': 'Z',
        'reset': 'reset'
    })

    def __init__(self):
        self.actions = []
        self.qubits = {}
        self.results = {}

    def export(self) -> TOutput:
        circuit = qt.qip.circuit.QubitCircuit(N=len(self.qubits), num_cbits=len(self.results))
        for action in self.actions:
            action(circuit)
        return circuit

    def qubit_as_expr(self, qubit) -> str:
        return repr(_resolve(qubit, self.qubits))

    def result_as_expr(self, result) -> str:
        return repr(_resolve(result, self.results))

    def on_simple_gate(self, name, *qubits) -> None:
        targets = [_resolve(qubit, self.qubits) for qubit in qubits]
        self.actions.append(lambda circuit:
            circuit.add_gate(
                self.gate_names[name],
                targets=targets
            )
        )

    def on_measure(self, qubit, result) -> None:
        targets = [_resolve(qubit, self.qubits)]
        classical_store = _resolve(result, self.results)
        self.actions.append(lambda circuit:
            circuit.add_measurement(
                "MZ",
                targets=targets,
                classical_store=classical_store
            )
        )

    def on_comment(self, text) -> None:
        print(f"# {text}")
