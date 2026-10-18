
import sys
from pathlib import Path
from parser import parse


def main():
    if len(sys.argv) != 2:
        print("Error: expected one .uedge file as argument")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    try:
        source = file_path.read_text(encoding="utf-8")
        parse(source)
        print("Parse successful")

    except SyntaxError as error:
        print(f"Error: {error}")
        sys.exit(1)

    except OSError as error:
        print(f"Error: could not read file: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
