"""AI coaching engine — generates personalised interview prep."""
import os

SYSTEM = """You are a world-class interview coach and hiring manager with 20 years of experience
across startups, FAANG, and consulting. You are direct, specific, and brutally honest.
You give actionable advice, not generic tips. You know exactly what interviewers are looking for
and where candidates fail. Never give platitudes like "be yourself" or "research the company"."""

PREP_PROMPT = """Prepare this candidate for their interview.

## Job Posting
{job}

## Candidate CV / Background
{cv}

---

Generate a complete interview prep guide structured as follows:

## Role Snapshot
What is this role actually about day-to-day? What does success look like in 90 days?

## Fit Analysis
**Strengths** — where the candidate's background aligns strongly with this role.
**Gaps** — honest list of missing skills, experience, or signals the interviewer will probe.
**Wildcard** — one non-obvious angle the candidate can use to stand out.

## Likely Interview Questions
For each question: the question itself, why they're asking it, and a coaching note on how to answer it well (not a scripted answer — a strategic note).

Include at least:
- 3 behavioural questions (STAR format signals)
- 3 technical/skills questions specific to this role
- 2 culture/values questions based on the job description
- 1 curveball they probably won't expect

## Gap Mitigation
For each gap identified: one concrete thing the candidate can do or say before/during the interview to reduce the risk.

## Questions to Ask the Interviewer
5 sharp questions that signal intelligence and genuine interest. No generic ones.

## Red Flags to Avoid
3 things this specific candidate should NOT say or do in this interview, based on their background.

## 48-Hour Prep Plan
A prioritised list of what to do in the 48 hours before the interview. Be specific."""


def prepare(job: str, cv: str, provider: str) -> str:
    prompt = PREP_PROMPT.format(
        job=job[:4000],  # cap to stay within token budget
        cv=cv[:3000],
    )

    if provider == "claude":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            msg = stream.get_final_message()
            for block in reversed(msg.content):
                if block.type == "text":
                    return block.text
            return ""

    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM)
        return model.generate_content(prompt).text

    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        return client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096,
        ).choices[0].message.content

    elif provider == "groq":
        from groq import Groq
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096,
        ).choices[0].message.content

    else:
        raise ValueError(f"Unknown provider: {provider}")
