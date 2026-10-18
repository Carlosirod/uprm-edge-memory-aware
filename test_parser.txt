
from pathlib import Path
from parser import parse


def main():
    test_dir = Path("tests")

    valid_files = [
        "01_within_budget.uedge",
        "02_over_budget.uedge",
    ]

    for filename in valid_files:
        source = (test_dir / filename).read_text(encoding="utf-8")

        try:
            result = parse(source)
            print(f"PASS: {filename} parsed successfully")
            print(result)
        except Exception as error:
            print(f"FAIL: {filename}: {error}")


if __name__ == "__main__":
    main()
