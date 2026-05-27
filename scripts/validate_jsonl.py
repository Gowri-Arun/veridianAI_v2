import json
from pathlib import Path

path = Path("benchmarks/enterpriseqa_v0.jsonl")

with path.open("r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        if line.strip():
            try:
                json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {error}"
                ) from error

print("JSONL benchmark is valid.")
