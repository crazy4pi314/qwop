# qwop : tools to help you get running with QIR in Python

_EXPERIMENTAL_

The point of the project is to help you not need this project 😅

This package is intended to be a collection of tools/utilities that allow
developers to work with [QIR](https://github.com/qir-alliance/qir-spec) in Python and add functionality to their own projects.
The hope is that with this sort of entry point developers can see and play around with QIR functionality such thaty they can then implement support in a more direct or integrated way in their own projects.
The primary dependency is on [pyQIR](https://github.com/qir-alliance/pyqir) for the core Python - QIR conversion implementation.

## Planned features

- [ ] Parse blocks from QIR bit files into circuit representations
  - [x] Cirq
  - [x] [OpenQASM2](https://arxiv.org/pdf/1707.03429v2.pdf)
  - [ ] OpenQASM3
  - [-] Qiskit (cheating right now, need direct impelmentation)
  - [ ] QuTiP
- [ ] Visualization functions for loaded QIR modules.
  - [x] Block level using [NetworkX](https://networkx.org/documentation/stable/index.html) and [pyvis](https://pyvis.readthedocs.io/en/latest/index.html) maybe? [Other examples](https://www.python-graph-gallery.com/network-chart/)
- Other ideas? File an issue! <3

## Resources/Notes

- Current project setup requires installing pyqir wheels from GH releases, qwop is currently build against release 0.0.1 of pyqir.
- For a development setup, see [CONTRIBUTING.md](CONTRIBUTING.md).
- Conversion tools inspired by [PR](https://github.com/microsoft/qsharp-compiler/pull/1221/files) by @cgranade
  