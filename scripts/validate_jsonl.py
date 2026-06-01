import json
import sys
from pathlib import Path


def validate_jsonl(path: str | Path) -> int:
    path_obj = Path(path)
    if not path_obj.exists():
        print(f"File not found: {path_obj}")
        return 1

    errors = 0
    with path_obj.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                print(f"Line {line_number}: empty line")
                errors += 1
                continue
            try:
                json.loads(stripped)
            except json.JSONDecodeError as error:
                print(f"Line {line_number}: invalid JSON — {error}")
                errors += 1

    if errors == 0:
        print(f"Valid JSONL: {path_obj} ({line_number} lines)" if line_number > 0 else f"Empty file: {path_obj}")
    else:
        print(f"Validation FAILED: {path_obj} — {errors} error(s)")
    return 0 if errors == 0 else 1


def main():
    if len(sys.argv) > 1:
        results = []
        for arg in sys.argv[1:]:
            code = validate_jsonl(arg)
            results.append(code)
        sys.exit(max(results))
    else:
        default = Path("benchmarks/enterpriseqa_v0.jsonl")
        sys.exit(validate_jsonl(default))


if __name__ == "__main__":
    main()
