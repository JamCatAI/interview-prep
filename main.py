#!/usr/bin/env python3
"""interview-prep — AI-powered personalised interview coach."""
import argparse
import os

# auto-load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import sys

PROVIDERS = ["claude", "gemini", "openai", "groq"]
API_KEY_MAP = {
    "claude": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "groq":   "GROQ_API_KEY",
}


def main():
    parser = argparse.ArgumentParser(
        prog="interview-prep",
        description="AI-powered personalised interview coach.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  python main.py --job posting.txt --cv resume.pdf
  python main.py --job https://jobs.ashby.io/company/role --cv cv.txt
  python main.py --job posting.txt --cv resume.pdf --provider gemini
  python main.py --job posting.txt --cv resume.pdf --format md -o prep.md
        """,
    )
    parser.add_argument("--job", required=True,
                        help="Job posting: file path, URL, or raw text")
    parser.add_argument("--cv", required=True,
                        help="Your CV/resume: file path or raw text")
    parser.add_argument("--provider", choices=PROVIDERS, default="claude")
    parser.add_argument("--format", choices=["console", "md"], default="console", dest="fmt")
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()

    key = API_KEY_MAP[args.provider]
    if not os.environ.get(key):
        print(f"error: {key} not set", file=sys.stderr)
        sys.exit(2)

    from parser import load_text
    from coach import prepare
    from formatter import console, markdown

    print("Loading job posting...", file=sys.stderr)
    job = load_text(args.job)
    if not job.strip():
        print("error: empty job posting", file=sys.stderr)
        sys.exit(2)

    print("Loading CV...", file=sys.stderr)
    cv = load_text(args.cv)
    if not cv.strip():
        print("error: empty CV", file=sys.stderr)
        sys.exit(2)

    # extract a short role hint for the header
    import re
    role_hint = ""
    m = re.search(r"(?:job title|position|role)[:\s]+([^\n]{5,60})", job, re.IGNORECASE)
    if not m:
        m = re.search(r"^#+\s*(.{5,60})", job, re.MULTILINE)
    if m:
        role_hint = m.group(1).strip()

    print(f"Coaching with {args.provider}...", file=sys.stderr)
    prep = prepare(job, cv, args.provider)
    print("✓ Prep guide ready", file=sys.stderr)

    output = (console(prep, args.provider, role_hint)
              if args.fmt == "console"
              else markdown(prep, args.provider, role_hint))

    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Saved: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
