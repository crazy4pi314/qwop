# -*- coding: utf-8 -*-
"""
====
Qiskit exporter
====

Implements a CircuitLikeExporter for a QIR block to the Qiskit framework.
"""
from qwop._optional_deps import qiskit as qk
from qwop.exporters.interface import CircuitLikeExporter

__all__ = ["QiskitExporter"] if qk is not None else []

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
        