#!/usr/bin/env python3
"""Summarize retained benchmark receipts; keep objective and reviewer scores apart."""
import json
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / ".runtime/strata-trial"


def median(values):
    values = [v for v in values if isinstance(v, (float, int))]
    return round(statistics.median(values), 3) if values else None


def read(path):
    return json.loads(path.read_text()) if path.exists() else None


def answer_choice(row):
    """Post-hoc format audit, distinct from the unchanged original grader."""
    if row.get("error") or row.get("finishReason") == "length":
        return None
    actual = row["grade"].get("actual")
    if isinstance(actual, dict) and actual.get("answer") in ("A", "B", "C", "D"):
        return actual["answer"]
    trailing = re.search(r'\{\s*"answer"\s*:\s*"([ABCD])"\s*\}\s*$', row.get("answer", ""))
    return trailing[1] if trailing else None


def main():
    result = {"models": {}, "pairedCategories": {}, "pairedLawAnswerChoices": {"bothCorrect": 0, "qwenOnly": 0, "strataOnly": 0, "bothWrong": 0}, "hardware": read(TRIAL / "hardware.json")}
    accuracy = {}
    for model in ["qwen", "strata"]:
        reports = {kind: read(TRIAL / f"{model}-{kind}.json") for kind in ["thinking", "speed", "review"]}
        review_answers = {r["id"]: r for r in (reports["review"] or {}).get("accuracy", []) if r["repeat"] == 0}
        review_retry = read(TRIAL / f"{model}-review-retry.json")
        if review_retry:
            review_answers.update({r["id"]: r for r in review_retry.get("accuracy", []) if r["repeat"] == 0})
        accuracy[model] = {(r["id"], r["repeat"]): r for r in (reports["thinking"] or {}).get("accuracy", [])}
        categories = {}
        for row in accuracy[model].values():
            cat = categories.setdefault(row["category"], {"passed": 0, "total": 0, "errors": 0, "truncated": 0, "strictJsonFailures": 0, "failures": []})
            cat["total"] += 1
            cat["passed"] += row["grade"]["passed"] is True
            cat["errors"] += bool(row.get("error"))
            cat["truncated"] += row.get("finishReason") == "length"
            cat["strictJsonFailures"] += row["grade"].get("strictJson") is False
            if not row["grade"]["passed"]:
                cat["failures"].append(row["id"])
        speed = {}
        for row in (reports["speed"] or {}).get("speed", []):
            group = speed.setdefault(str(row["backgroundRows"]), {"valid": [], "invalid": []})
            valid = not row.get("error") and row.get("usage", {}).get("completion_tokens") == 128 and row.get("reasoningChars", 0) == 0
            group["valid" if valid else "invalid"].append(row)
        for group in speed.values():
            rows = group.pop("valid")
            group.update(samples=len(rows),
                         promptTokens=median([r.get("usage", {}).get("prompt_tokens") for r in rows]),
                         completionSeconds=median([r.get("elapsedSeconds") for r in rows]),
                         firstContentSeconds=median([r.get("firstContentSeconds") for r in rows]),
                         serverGenerationTokensPerSecond=median([r.get("timings", {}).get("predicted_per_second") for r in rows]),
                         serverPromptTokensPerSecond=median([r.get("timings", {}).get("prompt_per_second") for r in rows]),
                         cachedPromptTokens=median([r.get("timings", {}).get("cache_n") for r in rows]))
        verification_reports = [r for r in [*reports.values(), review_retry] if r]
        law = [r for r in accuracy[model].values() if r["category"] == "public-law"]
        law_choice = {r["id"]: answer_choice(r) for r in law}
        result["models"][model] = {"categories": categories, "speed": speed,
                                    "objectiveTotals": {key: sum(c[key] for c in categories.values()) for key in ["passed", "total", "errors", "truncated", "strictJsonFailures"]},
                                    "lawAnswerChoiceAudit": {"correct": sum(law_choice[r["id"]] == r["grade"].get("expected", {}).get("answer") for r in law),
                                                             "total": len(law),
                                                             "formatOnlyFailures": [r["id"] for r in law if not r["grade"]["passed"] and law_choice[r["id"]] == r["grade"].get("expected", {}).get("answer")]},
                                    "reviewMedianSeconds": median([r.get("elapsedSeconds") for r in review_answers.values()]),
                                    "reviewCases": {key: {k: r.get(k) for k in ["elapsedSeconds", "finishReason", "requestedMaxOutputTokens"]} for key, r in review_answers.items()},
                                    "completed": {kind: bool((report or {}).get("completed")) for kind, report in reports.items()},
                                    "configurationUnchanged": all(report.get("originalFilesUnchanged", False) for report in verification_reports),
                                    "productionStateRestored": all(report.get("productionStateRestored", False) for report in verification_reports),
                                    "fixtureSha256": (reports["thinking"] or {}).get("fixtureSha256")}
    if all(accuracy.values()):
        if result["models"]["qwen"]["fixtureSha256"] != result["models"]["strata"]["fixtureSha256"]:
            raise SystemExit("Cannot compare different accuracy fixtures")
        for key in accuracy["qwen"].keys() & accuracy["strata"].keys():
            q, s = accuracy["qwen"][key], accuracy["strata"][key]
            cat = result["pairedCategories"].setdefault(q["category"], {"bothPass": 0, "qwenOnly": 0, "strataOnly": 0, "bothFail": 0})
            cat["bothPass" if q["grade"]["passed"] and s["grade"]["passed"] else "qwenOnly" if q["grade"]["passed"] else "strataOnly" if s["grade"]["passed"] else "bothFail"] += 1
            if q["category"] == "public-law":
                correct = q["grade"]["expected"]["answer"]
                qc, sc = answer_choice(q) == correct, answer_choice(s) == correct
                result["pairedLawAnswerChoices"]["bothCorrect" if qc and sc else "qwenOnly" if qc else "strataOnly" if sc else "bothWrong"] += 1
    result["review"] = read(TRIAL / "review-scores.json")
    path = TRIAL / "summary.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    path.chmod(0o600)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
