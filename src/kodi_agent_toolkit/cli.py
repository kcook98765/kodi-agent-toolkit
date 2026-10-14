"""Small portable command-line surface; no agent or Kodi runtime dependency."""
import argparse
import json
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(prog="kodi-toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
    discovery = sub.add_parser("discover")
    discovery.add_argument("directory", type=Path, nargs="?", default=Path("."))
    val = sub.add_parser("validate")
    val.add_argument("addon", type=Path)
    val.add_argument("--branch", choices=["matrix", "nexus", "omega", "piers"], default="nexus")
    val.add_argument("--cache", type=Path, default=Path(__file__).resolve().parents[2] / ".local/index-cache")
    context = sub.add_parser("review-context")
    context.add_argument("addon", type=Path)
    review = sub.add_parser("review-validate")
    review.add_argument("addon", type=Path)
    review.add_argument("report", type=Path)
    compose = sub.add_parser("review-compose")
    compose.add_argument("addon", type=Path)
    compose.add_argument("report", type=Path)
    compose.add_argument("--branch", choices=["matrix","nexus","omega","piers"], default="nexus")
    compose.add_argument("--cache", type=Path, default=Path(__file__).resolve().parents[2] / ".local/index-cache")
    final = sub.add_parser('report-build', help='Build status from trusted recorded results; never model prose')
    final.add_argument('addon', type=Path)
    final.add_argument('--validation', type=Path)
    final.add_argument('--review', type=Path)
    final.add_argument('--execution', type=Path)
    final.add_argument('--before', type=Path)
    final.add_argument('--markdown', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'report-build':
            from .reporting import build_report, render_report
            records = {k: json.loads(getattr(args, k).read_bytes())
                       for k in ('validation','review','execution','before') if getattr(args, k)}
            result = build_report(args.addon, **records,
                                  artifacts=[str(getattr(args,k)) for k in records])
            print(render_report(result) if args.markdown else json.dumps(result, indent=2))
            return 0 if result['outcome'] == 'PASS' else 1
        elif args.command == "discover":
            from .paths import discover
            result = discover(args.directory)
        elif args.command == "validate":
            from .validate import validate
            result = validate(args.addon, branch=args.branch, cache=args.cache)
        elif args.command == "review-context":
            from .review import review_context
            result = review_context(args.addon)
        elif args.command == "review-compose":
            from .compose import compose_review
            result = compose_review(args.addon, json.loads(args.report.read_bytes()), branch=args.branch, cache=args.cache)
        else:
            from .review import validate_review
            result = validate_review(args.addon, json.loads(args.report.read_bytes()))
        print(json.dumps(result, indent=2))
        if args.command == "review-context":
            return 0
        if args.command in {"validate","review-compose"}:
            return int(result.get("returncode", 0 if result.get("passed") else 1))
        return 0 if result.get("passed") else 1
    except Exception as exc:
        print(json.dumps({"passed": False, "infrastructure_error": type(exc).__name__,
                          "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
