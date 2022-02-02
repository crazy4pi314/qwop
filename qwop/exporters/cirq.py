# -*- coding: utf-8 -*-
"""
====
Circ exporter
====

Implements a CircuitLikeExporter for a QIR block to the Circ framework.
"""
from typing import Any, Callable, Dict, List, Optional
import pyqir_parser as pqp
from qwop._optional_deps import cirq as cq
import qwop.exporters.interface as interface

__all__ = ["CirqExporter"] if cq is not None else []

        
def _qubit_from_id(qubit) -> cq.LineQubit:
    return cq.LineQubit(interface._resolve_id(qubit))

class CirqExporter(interface.CircuitLikeExporter["cq.Circuit"]):
    operations : List[Callable[["cq.ops"], None]]

    qubits: Dict[Any, Optional[int]]

    qis_gate_mappings = {
        '__quantum__qis__x__body': cq.X,
        '__quantum__qis__y__body': cq.Y,
        '__quantum__qis__z__body': cq.Z,
        '__quantum__qis__h__body': cq.H,
        '__quantum__qis__cnot__body': cq.CNOT,
        '__quantum__qis__reset__body': cq.reset
    }

    def __init__(self, block : pqp.QirBlock):
        self.block = block
        self._export_ops()

    def on_simple_gate(self, name, *qubits) -> None:
        qubit_args = [_qubit_from_id(qubit) for qubit in qubits]
        self.operations.append(self.qis_gate_mappings[name](*qubit_args))

    def on_measure(self, qubit) -> None:
        self.operations.append(cq.measure(_qubit_from_id(qubit)))
   
    def _export_ops(self) -> None:
        for inst in self.block.instructions:
            if inst.func_name in self.qis_gate_mappings:
                self.on_simple_gate(inst.func_name, *inst.func_args)

            elif inst.func_name == "__quantum__qis__mz__body":
                target, result = inst.func_args
                self.on_measure(target)

            # Handle special cases of QIR functions as needed.
            elif inst.func_name == "__quantum__qir__read_result":
                print("A __quantum__qir__read_result was called, which is not supported in the circuit model for Cirq.")

            else:
                print("Unsupported QIS operation:")
                print(f"{inst.func_name} {', '.join(map(str, inst.func_args))}")
        
    def export(self) -> str:
        circuit = cq.Circuit()
        for operation in self.operations:
            circuit.append(operation())
        return circuit
