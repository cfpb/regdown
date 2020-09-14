# Regdown

![Build Status](https://github.com/cfpb/regdown/workflows/ci/badge.svg)[![Coverage Status](https://coveralls.io/repos/cfpb/regdown/badge.svg)](https://coveralls.io/r/cfpb/regdown)

Regdown is a [Python-Markdown](https://python-markdown.github.io) extension for interactive regulation text.

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Documentation](#documentation)
- [Getting help](#getting-help)
- [Getting involved](#getting-involved)
- [Licensing](#licensing)
- [Credits and references](#credits-and-references)

## Dependencies

- Python 3.6, 3.8
- [Python-Markdown](https://python-markdown.github.io) 3.2

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


Regdown adds three major features to Markdown to support making federal regulations easier to navigate and read.

### Labeled Paragraphs

`{label} Paragraph text`

Each paragraph can have a defined label, using `{label}` syntax at the start of the paragraph. This is translated into an `id` attribute on the resulting HTML paragraph element. If no label is given, the contents of the paragraph are hashed to generate a unique `id` for that paragraph. This makes any paragraph in the text directly linkable.

### Pseudo Forms

- `Form field: __`
- `__Form Field`
- `inline__fields__`

Example print forms, where the `\_\_` indicate a space for hand-written input. Can be any number of underscores between 2 and 50.

### Section symbols

`§ 1024.5(d)`
`§1024.5(d)`

Section symbols will always have a non-breaking space (&nbsp;) inserted between them and whatever follows to avoid hanging a symbol at the end of a line.

### Block references

`see(label)`

Insert the contents of labeled paragraphs in other Regdown documents inline into the current document. 

References can be placed before or after paragraphs. These references are to labeled paragraphs in other Markdown documents. When a `contents_resolver` callback and `url_resolver` callback are provided, the text of those other paragraphs can be looked up and inserted inline into the document making the reference. If `render_block_reference` callback is provided, custom rendering of the referenced text to HTML can be performed.

Callbacks:

- `contents_resolver(label)`: resolve the paragraph label and return the Markdown contents of that paragraph if the paragraph exists.
- `url_resolver(label)`: resolve the paragraph label and return a URL to that paragraph if the paragraph exists.
- `render_block_reference(contents, url=None)`: render the contents of a block reference to HTML. The url to the reference may be give as a keyword argument if `url_resolver` is provided.

```python
from regdown import regdown

def my_contents_resolver(label):
    # Lookup the document that contains the given label …
    return corresponding_markdown_text

def my_block_renderer(block_markdown_contents, url=None):
    # Render the block to HTML
    return block_html

regdown(
    text,
    contents_resolver=my_contents_resolver,
    render_block_reference=my_block_renderer
)
```

## Getting help

Please add issues to the [issue tracker](https://github.com/cfpb/regdown/issues).

## Getting involved

General instructions on _how_ to contribute can be found in [CONTRIBUTING](CONTRIBUTING.md).

## Licensing
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)

## Credits and references

regdown was forked from [Wagtail-Flags](https://github.com/cfpb/wagtail-flags), which was itself forked from [consumerfinance.gov](https://github.com/cfpb/consumerfinance.gov).
