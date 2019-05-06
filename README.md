# Regdown

[![Build Status](https://travis-ci.org/cfpb/regdown.svg?branch=master)](https://travis-ci.org/cfpb/regdown)
[![Coverage Status](https://coveralls.io/repos/github/cfpb/regdown/badge.svg?branch=master)](https://coveralls.io/github/cfpb/regdown?branch=master)

Regdown is a [Python-Markdown](https://python-markdown.github.io) extension for interactive regulation text.

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Documentation](#documentation)
- [Getting help](#getting-help)
- [Getting involved](#getting-involved)
- [Licensing](#licensing)
- [Credits and references](#credits-and-references)

## Dependencies

- Python 2.7+, 3.6+
- [Python-Markdown](https://python-markdown.github.io) 3.0+

## Installation

First, install Regdown:

```shell
pip install regdown
```

Then you can either:


- Specify Regdown as an extension in calls to `markdown`:

    ```python
    import markdown
    from regdown import RegulationsExtension

    markdown.markdown(text, extensions=[RegulationsExtension()],)
    ```

- Use convenience `regdown` function to render Markdown with the `RegulationsExtension`:

    ```python
    from regdown import regdown

    regdown(text)
    ```

## Documentation




## Getting help

Please add issues to the [issue tracker](https://github.com/cfpb/regdown/issues).

## Getting involved

General instructions on _how_ to contribute can be found in [CONTRIBUTING](CONTRIBUTING.md).

## Licensing
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)

## Credits and references

regdown was forked from [Wagtail-Flags](https://github.com/cfpb/wagtail-flags), which was itself forked from [cfgov-refresh](https://github.com/cfpb/cfgov-refresh).
