import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>.pdf")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = input_path.with_suffix(".md")

    print("Hello world!")


if __name__ == "__main__":
    main()
