import sys
from pathlib import Path

import pymupdf


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>.pdf")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = input_path.with_suffix(".md")

    doc = pymupdf.open(input_path)
    text = "\n\n".join(page.get_text() for page in doc)
    doc.close()

    output_path.write_text(text, encoding="utf-8")
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
