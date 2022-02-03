# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/crazy4pi314/qwop/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

Qwop could always use more documentation, whether as part of the
official qwop docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/crazy4pi314/qwop/issues.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `qwop` for local development.

> ❗Development setup currently uses conda for the environment management, so make
> sure you have anaconda installed.

1. Fork the `qwop` repo on GitHub.
2. Clone your fork locally.
3. Use conda to setup a development environment (pip and user setup in progress).

```shell
$ conda env create -f environment.yml
$ conda activate qwop
```

4. Download and install the pyqir parser wheel from their [GitHub releases](https://github.com/qir-alliance/pyqir/releases) page.
   >_FIXME should be pip or conda packages, see [#1](https://github.com/crazy4pi314/qwop/issues/1)_

```shell
pip install .\pyqir_parser-SOMEVERSION.whl
```

5. Create a branch for local development:
```shell
$ git checkout -b name-of-your-bugfix-or-feature
```
    Now you can make your changes locally.

5. When you're done making changes, check that your changes pass tests (tests under development, skip for now :P)

6. Commit your changes and push your branch to GitHub:

```shell
$ git add .
$ git commit -m "Your detailed description of your changes."
$ git push origin name-of-your-bugfix-or-feature
```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests (if applicable).
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to a relevant page/section of the docs.
3. Update the changelog.

## Tips


## Deploying

Should be done automatically with a version tag via GitHub Actions.