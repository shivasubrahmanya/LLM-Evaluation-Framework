import csv
import datetime

# File name for storing results
CSV_FILE = "results.csv"

# Columns required by your assignment
FIELDS = [
    "timestamp",
    "model_id",
    "task",
    "temperature",
    "seed",
    "prompt_chars",
    "completion_chars",
    "latency_ms",
    "est_cost_usd",
    "passed",
    "notes"
]

# Create new CSV with header
def init_csv():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

# Append a new row
def log_result(res):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow({k: res.get(k, "") for k in FIELDS})

# Run directly to test
if __name__ == "__main__":
    init_csv()
    log_result({
        "timestamp": datetime.datetime.now().isoformat(),
        "model_id": "test_model",
        "task": "test_task",
        "temperature": 0.7,
        "seed": 42,
        "prompt_chars": 10,
        "completion_chars": 20,
        "latency_ms": 123,
        "est_cost_usd": 0.0,
        "passed": True,
        "notes": "logger test row"
    })
    print("✅ logger.py created results.csv with one test row")
