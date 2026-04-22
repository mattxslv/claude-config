#!/usr/bin/env python3
import os, json, requests
from datetime import datetime, timezone, timedelta
import google.generativeai as genai

GITLAB_TOKEN = os.environ["GITLAB_TOKEN"]
GITLAB_BASE = "https://gitlab.com/api/v4"
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# All projects to track — add new ones here
PROJECTS = [
    {
        "name": "PEMEDES",
        "github_repo": os.environ.get("GITHUB_REPO_PEMEDES", "deadPixel505/pemedes-local"),
        "gitlab_project_id": os.environ.get("GITLAB_PROJECT_ID_PEMEDES", "81356854"),
    },
    {
        "name": "DTAP",
        "github_repo": os.environ.get("GITHUB_REPO_DTAP", "renzvalentino/DTAP"),
        "gitlab_project_id": os.environ.get("GITLAB_PROJECT_ID_DTAP", "81354540"),
    },
    {
        "name": "Startup PH",
        "github_repo": os.environ.get("GITHUB_REPO_STARTUPPH", "mattxslv/startup-ph"),
        "gitlab_project_id": os.environ.get("GITLAB_PROJECT_ID_STARTUPPH", "81533201"),
    },
]


def get_all_branches(github_repo):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    branches, page = [], 1
    while True:
        resp = requests.get(
            f"https://api.github.com/repos/{github_repo}/branches",
            params={"per_page": 100, "page": page},
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        branches.extend(b["name"] for b in data)
        page += 1
    return branches


def get_recent_commits(github_repo):
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    seen_shas, commits = set(), []

    branches = get_all_branches(github_repo)
    for branch in branches:
        try:
            resp = requests.get(
                f"https://api.github.com/repos/{github_repo}/commits",
                params={"sha": branch, "since": since, "per_page": 100},
                headers=headers,
            )
            resp.raise_for_status()
            for c in resp.json():
                if c["sha"] not in seen_shas:
                    seen_shas.add(c["sha"])
                    msg = c["commit"]["message"].split("\n")[0]
                    commits.append(f"[{branch}] {msg}")
        except Exception:
            pass

    return commits


def group_commits_with_gemini(project_name, commits):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    commit_list = "\n".join(f"- {c}" for c in commits)
    prompt = f"""You are a technical project manager writing GitLab work items for the {project_name} project.

Group these git commits into logical feature/fix groups. Write clear, informative titles and descriptions that explain what was built and why it matters — not just a list of commit messages.

Commits:
{commit_list}

Return a JSON array only, no markdown, no extra text. Each item:
- "title": work item title, imperative mood, under 70 chars, prefixed with feat/fix/chore
- "description": 2-3 sentence summary of what was done and its impact, followed by a bullet list of the commits

Example:
[{{"title": "feat: User authentication flow", "description": "Implemented secure login and session management for riders and operators. Users can now register, verify email, and maintain persistent sessions.\\n\\n**Commits:**\\n- feat: add login page\\n- fix: token expiry handling"}}]"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def create_and_close_issue(gitlab_project_id, title, description):
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN, "Content-Type": "application/json"}
    resp = requests.post(
        f"{GITLAB_BASE}/projects/{gitlab_project_id}/issues",
        headers=headers,
        json={"title": title, "description": description},
    )
    resp.raise_for_status()
    iid = resp.json()["iid"]
    requests.put(
        f"{GITLAB_BASE}/projects/{gitlab_project_id}/issues/{iid}",
        headers=headers,
        json={"state_event": "close"},
    ).raise_for_status()
    print(f"    #{iid} [closed] {title[:60]}")


def run_project(project):
    name = project["name"]
    print(f"\n── {name} ({project['github_repo']} — all branches)")

    try:
        commits = get_recent_commits(project["github_repo"])
    except requests.HTTPError as e:
        print(f"  ⚠ Could not fetch commits: {e}")
        return

    if not commits:
        print(f"  No commits in the last 24 hours — skipping.")
        return

    print(f"  {len(commits)} commit(s) found. Grouping with Gemini...")
    try:
        groups = group_commits_with_gemini(name, commits)
    except Exception as e:
        print(f"  ⚠ Gemini grouping failed: {e}")
        return

    print(f"  Creating {len(groups)} issue(s)...")
    today = datetime.now().strftime("%Y-%m-%d")
    for group in groups:
        desc = f"**Daily update: {today}**\n\n{group['description']}"
        try:
            create_and_close_issue(project["gitlab_project_id"], group["title"], desc)
        except Exception as e:
            print(f"  ⚠ Failed to create issue '{group['title']}': {e}")


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"GitLab daily update — {today}")
    print(f"Running for {len(PROJECTS)} project(s)...")

    for project in PROJECTS:
        run_project(project)

    print("\nDone.")


if __name__ == "__main__":
    main()
