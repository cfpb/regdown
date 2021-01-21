# -*- coding: utf-8 -*-
import re
from hashlib import sha3_224

from markdown import markdown, util
from markdown.blockprocessors import BlockProcessor, ParagraphProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import DoubleTagInlineProcessor, Pattern


# ***strongem*** or ***em*strong**
EM_STRONG_RE = r"(\*)\1{2}(.+?)\1(.*?)\1{2}"

# Form field: __
# __Form Field
# inline__fields__
PSEUDO_FORM_RE = r"(?P<underscores>_{2,50})(?P<line_ending>\s*$)?"

# Section symbol §
SECTION_SYMBOL_RE = r"(?P<section_symbol>§)\s+"

# Emdash ---
EMDASH_RE = r"---"


DEFAULT_URL_RESOLVER = lambda l: ""
DEFAULT_CONTENTS_RESOLVER = lambda l: ""
DEFAULT_RENDER_BLOCK_REFERENCE = (
    lambda c, **kwargs: "<blockquote>{}</blockquote>".format(regdown(c))
)


class RegulationsExtension(Extension):

    config = {
        "url_resolver": [
            DEFAULT_URL_RESOLVER,
            "Function to resolve the URL of a reference. "
            "Should return (title, url).",
        ],
        "contents_resolver": [
            DEFAULT_CONTENTS_RESOLVER,
            "Function to resolve the contents of a reference. "
            "Should return markdown contents of the reference or an empty "
            "string.",
        ],
        "render_block_reference": [
            DEFAULT_RENDER_BLOCK_REFERENCE,
            "Function that will render a block reference",
        ],
    }

    def extendMarkdown(self, md):
        md.registerExtension(self)

        # Replace all inlinePatterns that include an underscore with patterns
        # that do not include underscores.
        md.inlinePatterns.deregister("em_strong2")

        md.inlinePatterns.register(
            DoubleTagInlineProcessor(EM_STRONG_RE, "strong,em"),
            "em_strong2",
            60,
        )

        # Add inline emdash and pseudo form patterns.
        md.inlinePatterns.register(EmDashPattern(EMDASH_RE), "emdash", 200)
        md.inlinePatterns.register(
            PseudoFormPattern(PSEUDO_FORM_RE), "pseudo-form", 210
        )
        md.inlinePatterns.register(
            SectionSymbolPattern(SECTION_SYMBOL_RE), "section-symbol", 220
        )

        # Add block reference processor for `see(label)` syntax
        md.parser.blockprocessors.register(
            BlockReferenceProcessor(
                md.parser,
                url_resolver=self.getConfig("url_resolver"),
                contents_resolver=self.getConfig("contents_resolver"),
                render_block_reference=self.getConfig(
                    "render_block_reference"
                ),
            ),
            "blockreference",
            200,
        )

        # Replace the default paragraph processor with one that handles
        # `{label}` syntax and gives default hash-based ids to paragraphs
        md.parser.blockprocessors.deregister("paragraph")
        md.parser.blockprocessors.register(
            LabeledParagraphProcessor(md.parser), "paragraph", 10
        )

        # Delete the ordered list processor
        md.parser.blockprocessors.deregister("olist")


class EmDashPattern(Pattern):
    """ Replace '---' with an &mdash; """

    def handleMatch(self, m):
        return "{}mdash;".format(util.AMP_SUBSTITUTE)


class PseudoFormPattern(Pattern):
    """Return a <span class="pseudo-form"></span> element for matches of the
    given pseudo-form pattern."""

    def handleMatch(self, m):
        el = util.etree.Element("span")
        el.set("class", "regdown-form")
        if m.group("line_ending") is not None:
            el.set("class", "regdown-form_extend")
            util.etree.SubElement(el, "span")
        el.text = m.group("underscores")
        return el


class SectionSymbolPattern(Pattern):
    """ Make whitespace after a section symbol non-breaking """

    def handleMatch(self, m):
        return "{section}{stx}{char}{etx}#160;".format(
            section=m.group("section_symbol"),
            stx=util.STX,
            char=ord("&"),
            etx=util.ETX,
        )


class LabeledParagraphProcessor(ParagraphProcessor):
    """Process paragraph blocks, including those with labels.
    This processor entirely replaces the standard ParagraphProcessor in
    order to ensure that all paragraphs are labeled in some way."""

    RE = re.compile(r"(?:^){(?P<label>[\w\-]+)}(?:\s?)(?P<text>.*)(?:\n|$)")

    def test(self, parent, block):
        # return self.RE.search(block)
        return True

    def run(self, parent, blocks):
        block = blocks.pop(0)
        match = self.RE.search(block)

        if match:
            # If there's a match, then this is a labeled paragraph. We'll add
            # the paragraph tag, label id, and initial text, then process the
            # rest of the blocks normally.
            label, text = match.group("label"), match.group("text")
            # Labeled paragraphs without text should use a div element
            if text == "":
                el = util.etree.SubElement(parent, "div")
            else:
                el = util.etree.SubElement(parent, "p")
            el.set("id", label)
            el.set("data-label", label)

            # We use CSS classes to indent paragraph text. To get the correct
            # class, we count the number of dashes in the label to determine
            # how deeply nested the paragraph is. Inline interps have special
            # prefixes that are removed before counting the dashes.
            # e.g. 6-a-Interp-1 becomes 1 and gets a `level-0` class
            # e.g. 12-b-Interp-2-i becomes 2-i and gets a `level-1` class
            label = re.sub(
                r"^(\w+\-)+interp\-", "", label, flags=re.IGNORECASE
            )

            # Appendices also have special prefixes that need to be stripped.
            # e.g. A-1-a becomes a and gets a `level-0` class
            # e.g. A-2-d-1 becomes d-1 and gets a `level-1` class
            label = re.sub(r"^[A-Z]\d?\-\w+\-?", "", label)
            level = label.count("-")
            class_name = "regdown-block level-{}".format(level)
            el.set("class", class_name)

            el.text = text.lstrip()

        elif block.strip():
            if self.parser.state.isstate("list"):
                # Pass off to the ParagraphProcessor for lists
                super(ParagraphProcessor, self).run(
                    parent, blocks
                )  # pragma: no cover
            else:
                # Generate a label that is a hash of the block contents. This
                # way it won't change unless the rest of this block changes.
                text = block.lstrip()
                label = sha3_224(text.encode("utf-8")).hexdigest()
                class_name = "regdown-block"
                p = util.etree.SubElement(parent, "p")
                p.set("id", label)
                p.set("class", class_name)
                p.set("data-label", "")

                p.text = text


class BlockReferenceProcessor(BlockProcessor):
    """Process `see(label)` as an blockquoted reference.
    To render the block reference, the extension must be initialized with a
    callable render_block_reference option that will take the contents of
    the block reference, rendering to HTML, and return the HTML.
    """

    RE = re.compile(r"(?:^)see\((?P<label>[\w-]+)\)(?:\n|$)")

    def __init__(
        self,
        parser,
        url_resolver=None,
        contents_resolver=None,
        render_block_reference=None,
    ):
        super(BlockReferenceProcessor, self).__init__(parser)
        self.url_resolver = url_resolver
        self.contents_resolver = contents_resolver
        self.render_block_reference = render_block_reference

    def test(self, parent, block):
        return self.RE.search(block)

    def run(self, parent, blocks):
        block = blocks.pop(0)
        match = self.RE.match(block)

        if match:
            # Without a contents_resolver, we can't resolve block contents
            if not callable(self.contents_resolver) or not callable(
                self.render_block_reference
            ):
                return

            label = match.group("label")
            contents = self.contents_resolver(label)
            url = self.url_resolver(label)

            if contents == "":
                return

            rendered_contents = self.render_block_reference(contents, url=url)

            parent.append(
                util.etree.fromstring(rendered_contents.encode("utf-8"))
            )


def makeExtension(*args, **kwargs):
    return RegulationsExtension(*args, **kwargs)


def regdown(text, **kwargs):
    """Regdown convenience function
    Takes text and parses it with the RegulationsExtention configured with
    the given keyword arguments."""
    return markdown(
        text,
        extensions=[
            "markdown.extensions.tables",
            RegulationsExtension(**kwargs),
        ],
        **kwargs,
    )


def extract_labeled_paragraph(label, text, exact=True):
    """Extract all the Regdown between the given label and the next.
    This utility function extracts all text between a labeled paragraph
    (with leading {label}) and the next labeled paragraph. If exact is False,
    it will match all paragraphs with labels that *begin with* the given
    label."""
    para_lines = []

    for line in text.splitlines(True):
        match = LabeledParagraphProcessor.RE.search(line)
        if match:
            # It's the correct label and we want an exact match
            if exact and match.group("label") == label:
                para_lines.append(line)

            # We don't want an exact match and the label starts with our given
            # label
            elif not exact and match.group("label").startswith(label):
                para_lines.append(line)

            # We've already found a label, and this is another one
            elif len(para_lines) > 0:
                break

        # We've found a label and haven't found the next
        elif len(para_lines) > 0:
            para_lines.append(line)

    return "".join(para_lines)
