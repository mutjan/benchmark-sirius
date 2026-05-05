#!/usr/bin/env python3
"""Build the published aggregate results JSON from per-model source files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = ROOT / "data" / "benchmark.json"
SOURCE_DIR = ROOT / "data" / "results"
OUTPUT_PATH = ROOT / "data" / "results.json"

REQUIRED_RESULT_FIELDS = {
    "id",
    "model",
    "model_version",
    "provider",
    "api_endpoint",
    "test_date",
    "notes",
    "scores",
    "answers",
    "full_answer",
}


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_benchmark(path: Path = BENCHMARK_PATH) -> dict[str, Any]:
    benchmark = load_json(path)
    if not isinstance(benchmark, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return benchmark


def question_maxes(benchmark: dict[str, Any]) -> dict[str, float]:
    questions = benchmark.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValidationError("benchmark.json must define a non-empty questions array")

    maxes: dict[str, float] = {}
    for q in questions:
        if not isinstance(q, dict):
            raise ValidationError("each benchmark question must be an object")
        qid = q.get("id")
        qmax = q.get("max")
        if not isinstance(qid, str) or not qid:
            raise ValidationError("each benchmark question needs a non-empty string id")
        if qid in maxes:
            raise ValidationError(f"duplicate benchmark question id: {qid}")
        if not is_number(qmax) or qmax < 0:
            raise ValidationError(f"question {qid} has invalid max: {qmax!r}")
        maxes[qid] = float(qmax)

    total = benchmark.get("total_points")
    if not is_number(total):
        raise ValidationError("benchmark total_points must be numeric")
    if abs(sum(maxes.values()) - float(total)) > 1e-9:
        raise ValidationError(
            f"question max sum {sum(maxes.values())} != total_points {total}"
        )

    for dim in benchmark.get("dimensions", []):
        if not isinstance(dim, dict):
            raise ValidationError("each benchmark dimension must be an object")
        key = dim.get("key")
        dim_questions = dim.get("questions")
        dim_max = dim.get("max")
        if not isinstance(key, str) or not isinstance(dim_questions, list):
            raise ValidationError(f"invalid dimension definition: {dim!r}")
        missing = [qid for qid in dim_questions if qid not in maxes]
        if missing:
            raise ValidationError(f"dimension {key} references missing questions: {missing}")
        expected = sum(maxes[qid] for qid in dim_questions)
        if not is_number(dim_max) or abs(expected - float(dim_max)) > 1e-9:
            raise ValidationError(f"dimension {key} max {dim_max!r} != question sum {expected}")

    return maxes


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def load_source_results(source_dir: Path = SOURCE_DIR) -> list[dict[str, Any]]:
    if not source_dir.exists():
        raise ValidationError(f"missing source directory: {source_dir}")
    if not source_dir.is_dir():
        raise ValidationError(f"source path is not a directory: {source_dir}")

    paths = sorted(source_dir.glob("*.json"))
    if not paths:
        raise ValidationError(f"no per-model JSON files found in {source_dir}")

    results: list[dict[str, Any]] = []
    for path in paths:
        result = load_json(path)
        if not isinstance(result, dict):
            raise ValidationError(f"{path} must contain one result object")
        rid = result.get("id")
        if rid != path.stem:
            raise ValidationError(f"{path} filename must match result id {rid!r}")
        results.append(result)
    return results


def validate_results(benchmark: dict[str, Any], results: list[dict[str, Any]]) -> None:
    maxes = question_maxes(benchmark)
    qids = set(maxes)
    seen: set[str] = set()

    for result in results:
        rid = result.get("id")
        if not isinstance(rid, str) or not rid:
            raise ValidationError("each result needs a non-empty string id")
        if rid in seen:
            raise ValidationError(f"duplicate result id: {rid}")
        seen.add(rid)

        missing_fields = sorted(REQUIRED_RESULT_FIELDS - set(result))
        if missing_fields:
            raise ValidationError(f"{rid} missing required fields: {missing_fields}")

        scores = result.get("scores")
        answers = result.get("answers")
        if not isinstance(scores, dict):
            raise ValidationError(f"{rid} scores must be an object")
        if not isinstance(answers, dict):
            raise ValidationError(f"{rid} answers must be an object")

        score_keys = set(scores)
        answer_keys = set(answers)
        if score_keys != qids:
            raise ValidationError(
                f"{rid} scores keys mismatch; missing={sorted(qids - score_keys)} "
                f"extra={sorted(score_keys - qids)}"
            )
        if answer_keys != qids:
            raise ValidationError(
                f"{rid} answers keys mismatch; missing={sorted(qids - answer_keys)} "
                f"extra={sorted(answer_keys - qids)}"
            )

        for qid, value in scores.items():
            if not is_number(value):
                raise ValidationError(f"{rid} {qid} score must be numeric, got {value!r}")
            if value < 0 or value > maxes[qid]:
                raise ValidationError(f"{rid} {qid} score {value} outside 0..{maxes[qid]}")

        for qid, answer in answers.items():
            if not isinstance(answer, dict):
                raise ValidationError(f"{rid} {qid} answer must be an object")
            snippet = answer.get("snippet")
            if not isinstance(snippet, str) or not snippet.strip():
                raise ValidationError(f"{rid} {qid} answer.snippet must be non-empty")

        full_answer = result.get("full_answer")
        if not isinstance(full_answer, str):
            raise ValidationError(f"{rid} full_answer must be a string")


def build(
    write: bool,
    benchmark_path: Path = BENCHMARK_PATH,
    source_dir: Path = SOURCE_DIR,
    output_path: Path = OUTPUT_PATH,
) -> list[dict[str, Any]]:
    benchmark = load_benchmark(benchmark_path)
    results = load_source_results(source_dir)
    validate_results(benchmark, results)
    if write:
        write_json(output_path, results)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate sources without rewriting data/results.json",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=BENCHMARK_PATH,
        help="benchmark definition JSON path",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=SOURCE_DIR,
        help="directory containing per-model result JSON files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="aggregate results JSON path",
    )
    args = parser.parse_args()

    try:
        results = build(
            write=not args.check,
            benchmark_path=args.benchmark,
            source_dir=args.source_dir,
            output_path=args.output,
        )
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    action = "validated" if args.check else "built"
    print(f"{action} {len(results)} result files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
