# -*- coding: utf-8 -*-
"""
====
QuTiP exporter
====

Implements a CircuitLikeExporter for a QIR block to the QuTiP framework.
"""
from types import MappingProxyType
from typing import Any, Callable, Dict, List, TypeVar
import pyqir_parser as pqp
TOutput = TypeVar('TOutput')

from qwop._optional_deps import qutip as qt
from qwop.exporters.interface import CircuitLikeExporter, _resolve

__all__ = ["QuTiPExporter"] if qt is not None else []
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

    def __init__(self, block : pqp.QirBlock):
        self.actions = []
        self.qubits = {}
        self.results = {}
        self.block = block

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
        