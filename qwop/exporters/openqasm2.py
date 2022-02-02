# -*- coding: utf-8 -*-
"""
====
OpenQASM2.0 exporter
====

Implements a CircuitLikeExporter for a QIR block to the OpenQASM2.0 specification.
"""
from typing import List, Any, Dict, Optional
import pyqir_parser as pqp

from qwop.exporters.interface import CircuitLikeExporter, _resolve_id
__all__ = ["OpenQasm20Exporter"]

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
