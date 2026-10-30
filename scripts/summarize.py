from __future__ import annotations
import argparse, json, sqlite3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from workflow import dashboard_metrics

p = argparse.ArgumentParser(description="Print recruitment dashboard metrics")
p.add_argument("database", type=Path, nargs="?", default=Path("data/generated/recruitment.db"))
a = p.parse_args()
c = sqlite3.connect(a.database)
print(json.dumps(dashboard_metrics(c), indent=2))
c.close()
