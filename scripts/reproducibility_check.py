from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=20261022)
    p.add_argument("--scale", type=float, default=0.1)
    args = p.parse_args()
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "run_a", Path(td) / "run_b"
        for out in (a, b):
            subprocess.run([sys.executable, "-m", "src.generator", "--output", str(out), "--seed", str(args.seed), "--scale", str(args.scale)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        files_a = {p.name: digest(p) for p in a.iterdir() if p.is_file() and p.name != "recruitment.db"}
        files_b = {p.name: digest(p) for p in b.iterdir() if p.is_file() and p.name != "recruitment.db"}
        with (a / "validation_summary.json").open() as f: summary = json.load(f)
        report = {"seed": args.seed, "scale": args.scale, "csv_json_sql_and_metadata_identical": files_a == files_b,
                  "files_compared": sorted(files_a), "baseline_counts": summary["baseline_counts"], "row_counts_including_labelled_cases": summary["actual_counts_including_labelled_cases"],
                  "validation_pass": summary["validation"]["pass"]}
        print(json.dumps(report, indent=2))
        if files_a != files_b or not report["validation_pass"]: raise SystemExit(1)
if __name__ == "__main__": run()
