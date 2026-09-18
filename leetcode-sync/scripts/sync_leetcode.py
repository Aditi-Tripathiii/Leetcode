"""
Pulls your recently ACCEPTED LeetCode submissions and writes:
  quest/<slug>/README.md   -> problem statement, difficulty, link
  sol/<slug>/solution.<ext> -> your accepted code

State is tracked in data/synced.json so we never rewrite/duplicate a submission
we've already synced (unless you accept a *new* submission id for the same
problem, in which case we overwrite with the newer one).

Auth note: leetcode.com/api/submissions/ is not officially public API, it's
the same endpoint your browser calls when you open "Submissions" on your
profile. It needs your session cookie. This will keep working as long as
you're logged into LeetCode with that session; if you log out everywhere /
the session expires, you'll need to grab a fresh cookie (see SETUP.md).
"""

import os
import sys
import json
import time
import pathlib
import requests

LEETCODE_SESSION = os.environ["LEETCODE_SESSION"]
CSRF_TOKEN = os.environ["LEETCODE_CSRF_TOKEN"]
USERNAME = os.environ.get("LEETCODE_USERNAME", "")

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "data" / "synced.json"
QUEST_DIR = ROOT / "quest"
SOL_DIR = ROOT / "sol"

HEADERS = {
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN};",
    "x-csrftoken": CSRF_TOKEN,
    "Referer": "https://leetcode.com/",
    "User-Agent": "Mozilla/5.0",
}

LANG_EXT = {
    "python": "py", "python3": "py", "java": "java", "c": "c", "cpp": "cpp",
    "csharp": "cs", "javascript": "js", "typescript": "ts", "ruby": "rb",
    "swift": "swift", "golang": "go", "scala": "scala", "kotlin": "kt",
    "rust": "rs", "php": "php", "racket": "rkt", "erlang": "erl",
    "elixir": "ex", "dart": "dart", "mysql": "sql", "mssql": "sql",
    "oraclesql": "sql", "postgresql": "sql",
}


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def fetch_recent_submissions(limit=40):
    url = f"https://leetcode.com/api/submissions/?offset=0&limit={limit}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("submissions_dump", [])


def fetch_question_content(slug):
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        difficulty
        content
      }
    }
    """
    r = requests.post(
        "https://leetcode.com/graphql",
        headers=HEADERS,
        json={"query": query, "variables": {"titleSlug": slug}},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["data"]["question"]


def write_problem(slug, submission, state):
    sub_id = str(submission["id"])
    if state.get(slug) == sub_id:
        return False  # already synced this exact submission

    q = fetch_question_content(slug)
    ext = LANG_EXT.get(submission["lang"], submission["lang"])

    quest_path = QUEST_DIR / slug
    sol_path = SOL_DIR / slug
    quest_path.mkdir(parents=True, exist_ok=True)
    sol_path.mkdir(parents=True, exist_ok=True)

    readme = (
        f"# {q['questionFrontendId']}. {q['title']}\n\n"
        f"**Difficulty:** {q['difficulty']}\n\n"
        f"https://leetcode.com/problems/{slug}/\n\n"
        f"---\n\n"
        f"{q['content']}\n"
    )
    (quest_path / "README.md").write_text(readme, encoding="utf-8")
    (sol_path / f"solution.{ext}").write_text(submission["code"], encoding="utf-8")

    state[slug] = sub_id
    print(f"synced: {slug} (submission {sub_id})")
    return True


def main():
    state = load_state()
    submissions = fetch_recent_submissions()

    # oldest first, so if there are multiple accepted attempts we end on the latest
    accepted = [s for s in submissions if s.get("status_display") == "Accepted"]
    accepted.reverse()

    changed = False
    for s in accepted:
        slug = s["title_slug"]
        try:
            if write_problem(slug, s, state):
                changed = True
            time.sleep(1)  # be polite to LeetCode's endpoint
        except Exception as e:
            print(f"failed on {slug}: {e}", file=sys.stderr)

    if changed:
        save_state(state)
    else:
        print("no new accepted submissions")


if __name__ == "__main__":
    main()
