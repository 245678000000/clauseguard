"""Command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, llm, report, scanner


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="clauseguard",
        description="Local-first bilingual (EN/中文) contract risk scanner: "
        "deterministic rules + an open-weight LLM via Ollama. Nothing leaves "
        "your machine.",
    )
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    scan_p = sub.add_parser("scan", help="scan a contract file")
    scan_p.add_argument("file", help="path to a .txt/.md contract")
    scan_p.add_argument("-o", "--out", help="write markdown report here (default: stdout summary)")
    scan_p.add_argument("--json", action="store_true", help="emit JSON findings")
    scan_p.add_argument("--model", default=llm.DEFAULT_MODEL, help=f"Ollama model (default {llm.DEFAULT_MODEL})")
    scan_p.add_argument("--no-llm", action="store_true", help="rules only, skip the local LLM")
    scan_p.add_argument("--url", default=llm.OLLAMA_URL, help="Ollama base URL")

    rules_p = sub.add_parser("rules", help="list built-in rules")
    rules_p.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "rules":
        if args.json:
            print(
                json.dumps(
                    [
                        {
                            "id": r.id,
                            "category": r.category,
                            "severity": r.severity,
                            "en": r.name_en,
                            "zh": r.name_zh,
                        }
                        for r in __import__("clauseguard.rules", fromlist=["RULES"]).RULES
                    ],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            for r in __import__("clauseguard.rules", fromlist=["RULES"]).RULES:
                print(f"[sev {r.severity}] {r.id:24} {r.name_en} / {r.name_zh}")
        return 0

    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")

    result = scanner.scan(
        text, use_llm=not args.no_llm, model=args.model, url=args.url
    )

    if args.json:
        print(
            json.dumps(
                {"summary": result.summary(), "findings": [f.as_dict() for f in result.findings]},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report.render(result, path.name), encoding="utf-8")
        print(report.render_terminal(result, path.name))
        print(f"\nmarkdown report written to {args.out}")
    else:
        print(report.render_terminal(result, path.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
