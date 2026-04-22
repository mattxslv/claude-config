#!/usr/bin/env python3
import os, json, requests
from datetime import datetime, timezone, timedelta
import google.generativeai as genai

GITLAB_TOKEN = os.environ["GITLAB_TOKEN"]
GITLAB_PROJECT_ID = os.environ["GITLAB_PROJECT_ID"]
GITLAB_BASE = "https://gitlab.com/api/v4"
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ.get("GITHUB_REPO", "deadPixel505/pemedes-local")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "staging")
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]


def get_recent_commits():
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    resp = requests.get(
        f"https://api.github.com/repos/{GITHUB_REPO}/commits",
        params={"sha": GITHUB_BRANCH, "since": since, "per_page": 100},
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
    )
    resp.raise_for_status()
    return [c["commit"]["message"].split("\n")[0] for c in resp.json()]


def group_commits_with_gemini(commits):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    commit_list = "\n".join(f"- {c}" for c in commits)
    prompt = f"""Group these git commits into logical feature/fix groups for GitLab work items.

Commits:
{commit_list}

Return a JSON array only, no markdown, no extra text. Each item:
- "title": work item title, imperative mood, under 70 chars
- "description": markdown bullet list of commits in this group

Example: [{{"title": "feat: User auth flow", "description": "- feat: add login\\n- fix: token expiry"}}]"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def create_and_close_issue(title, description):
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN, "Content-Type": "application/json"}
    resp = requests.post(
        f"{GITLAB_BASE}/projects/{GITLAB_PROJECT_ID}/issues",
        headers=headers,
        json={"title": title, "description": description},
    )
    resp.raise_for_status()
    iid = resp.json()["iid"]
    requests.put(
        f"{GITLAB_BASE}/projects/{GITLAB_PROJECT_ID}/issues/{iid}",
        headers=headers,
        json={"state_event": "close"},
    ).raise_for_status()
    print(f"  #{iid} [closed] {title[:60]}")


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"GitLab daily update — {today}")

    commits = get_recent_commits()
    if not commits:
        print("No commits in the last 24 hours. Skipping.")
        return

    print(f"Found {len(commits)} commit(s). Grouping with Gemini...")
    groups = group_commits_with_gemini(commits)

    print(f"Creating {len(groups)} issue(s)...")
    for group in groups:
        desc = f"**Daily update: {today}**\n\n{group['description']}"
        create_and_close_issue(group["title"], desc)

    print("Done.")


if __name__ == "__main__":
    main()
