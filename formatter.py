"""Output formatting for interview-prep."""

BOLD  = "\033[1m"
CYAN  = "\033[96m"
RESET = "\033[0m"
SEP   = "─" * 72


def console(prep_text: str, provider: str, role_hint: str = "") -> str:
    header = (
        f"{SEP}\n"
        f"  {BOLD}interview-prep{RESET}  "
        f"{CYAN}{role_hint}{RESET}  "
        f"coached by {BOLD}{provider}{RESET}\n"
        f"{SEP}\n\n"
    )
    return header + prep_text + f"\n\n{SEP}"


def markdown(prep_text: str, provider: str, role_hint: str = "") -> str:
    return (
        f"# Interview Prep — {role_hint}\n\n"
        f"*Coached by `{provider}`*\n\n"
        f"---\n\n"
        f"{prep_text}\n"
    )
