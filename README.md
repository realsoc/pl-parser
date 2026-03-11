# pl-parser

Simple PDF parser for typed document.

## Dependencies

- [pymupdf](https://pymupdf.readthedocs.io/) - PDF parsing library
- [tesseract](https://github.com/tesseract-ocr/tesseract) - OCR engine (system dependency, install separately)

## Installation

Install [uv](https://docs.astral.sh/uv/) if not already installed, then:

```bash
uv sync
```

## Usage

```bash
uv run pl-parser <filename>.pdf
```

This will output a `<filename>.md` file in the same directory.
