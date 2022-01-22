# qwop : tools to help you work with QIR in Python

_EXPERIMENTAL_
This package is intended to be a collection of tools/utilities that allow
developers to work with [QIR](https://github.com/qir-alliance/qir-spec) in Python and add functionality to their own
projects. The primary dependency is on [pyQIR](https://github.com/qir-alliance/pyqir) for the core Python - QIR conversion implementation.

## Planned features

- [ ] Parse blocks from QIR bit files into circuit representations
  - [ ] Cirq
  - [ ] [OpenQASM2](https://arxiv.org/pdf/1707.03429v2.pdf)
  - [ ] OpenQASM3
  - [ ] Qiskit
  - [ ] QuTiP
- [ ] Block level visualization functions for loaded QIR modules.
  - [ ] Using [NetworkX](https://networkx.org/documentation/stable/index.html) and [pyvis](https://pyvis.readthedocs.io/en/latest/index.html) maybe? [Other examples](https://www.python-graph-gallery.com/network-chart/)
- Other ideas? File an issue! <3

## Resources/Notes

- Current project setup requires installing pyqir wheels from GH releases (downloaded packages pushed here until on pypi)
- A couple of QIR bc files are included in the repo, and later source will be added to generate these and other examples.
- Conversion tools inspired by [PR](https://github.com/microsoft/qsharp-compiler/pull/1221/files) by @cgranade
  