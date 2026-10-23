#!/usr/bin/env python3
"""Mask local-model review answers; reveal attribution only after scores exist."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / ".runtime/strata-trial"


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    Path(path).chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reveal", action="store_true")
    args = parser.parse_args()
    fixtures = read(ROOT / "fixtures/local-model-review.json")
    packet_path, mapping_path = TRIAL / "blind-review.json", TRIAL / "blind-review-mapping.json"
    if not args.reveal:
        if packet_path.exists() or mapping_path.exists():
            raise SystemExit("A blinded packet already exists; preserving its labels")
        reports = {m: read(TRIAL / f"{m}-review.json") for m in ["qwen", "strata"]}
        if reports["qwen"]["fixtureSha256"] != reports["strata"]["fixtureSha256"]:
            raise SystemExit("Review fixture hashes differ")
        rubric_sha = hashlib.sha256((ROOT / "fixtures/local-model-review.json").read_bytes()).hexdigest()
        if any(r.get("reviewRubricSha256") != rubric_sha for r in reports.values()):
            raise SystemExit("The review rubric differs from what was fixed before generation")
        answers = {}
        for model, report in reports.items():
            answers[model] = {r["id"]: r for r in report["accuracy"] if r["repeat"] == 0}
            if set(answers[model]) != {r["id"] for r in fixtures["cases"]}:
                raise SystemExit(f"{model} review is incomplete")
        retry_reports = {m: read(TRIAL / f"{m}-review-retry.json") if (TRIAL / f"{m}-review-retry.json").exists() else None for m in reports}
        if any(retry_reports.values()):
            if not all(retry_reports.values()) or retry_reports["qwen"]["fixtureSha256"] != retry_reports["strata"]["fixtureSha256"]:
                raise SystemExit("Paired retry reports are missing or use different fixtures")
            retry_ids = None
            for model, report in retry_reports.items():
                if not report.get("completed") or report.get("reviewRubricSha256") != rubric_sha:
                    raise SystemExit("Retry is incomplete or changed the fixed rubric")
                chosen = {r["id"]: r for r in report["accuracy"] if r["repeat"] == 0}
                if not set(chosen) <= set(answers[model]) or (retry_ids is not None and set(chosen) != retry_ids):
                    raise SystemExit("Retry case IDs do not match")
                retry_ids = set(chosen)
                answers[model].update(chosen)
        packet = {"rubric": fixtures["scoring"], "cases": []}
        mapping = {}
        for row in fixtures["cases"]:
            models = ["qwen", "strata"]
            secrets.SystemRandom().shuffle(models)
            mapping[row["id"]] = dict(zip(["A", "B"], models))
            pair = {}
            for label, model in mapping[row["id"]].items():
                answer = answers[model][row["id"]]
                pair[label] = {"answer": answer.get("answer", ""),
                               "generationFailed": bool(answer.get("error")),
                               "truncated": answer.get("finishReason") == "length",
                               "requestedMaxOutputTokens": answer.get("requestedMaxOutputTokens", row["max_tokens"])}
            packet["cases"].append({"id": row["id"], "prompt": row["prompt"], "reference": row["reference"], "responses": pair})
        write(packet_path, packet)
        write(mapping_path, mapping)
        print(f"Created {packet_path}; attribution is kept in a separate file")
        return
    grades_path = TRIAL / "blind-review-grades.json"
    grades, mapping = read(grades_path), read(mapping_path)
    if {r["id"] for r in grades["cases"]} != set(mapping):
        raise SystemExit("Every blinded case must be scored before revealing attribution")
    results = {"reviewer": "assistant in this chat", "method": "model labels randomized per case; rubric and reference facts fixed before generation", "models": {m: {"total": 0, "maximum": 0, "cases": []} for m in ["qwen", "strata"]}}
    for row in grades["cases"]:
        for label, model in mapping[row["id"]].items():
            grade = row["responses"][label]
            total = 0
            for dimension, rubric in fixtures["scoring"].items():
                value = grade[dimension]
                if not isinstance(value, (float, int)) or not 0 <= value <= rubric["max"]:
                    raise SystemExit(f"Invalid score: {row['id']} {label} {dimension}")
                total += value
            target = results["models"][model]
            target["total"] += total
            target["maximum"] += 10
            target["cases"].append(dict(id=row["id"], total=total, **grade))
    write(TRIAL / "review-scores.json", results)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
