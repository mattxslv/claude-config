#!/usr/bin/env python3
import json
import os
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from google import genai
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GITHUB_AUTHOR = os.environ.get("GITHUB_AUTHOR", "mattxslv")
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Manila")
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "3"))
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in {"1", "true", "yes"}

PROJECTS = [
    {
        "name": "PEMEDES",
        "github_repo": os.environ.get("GITHUB_REPO_PEMEDES", "deadPixel505/pemedes-local"),
    },
    {
        "name": "DTAP",
        "github_repo": os.environ.get("GITHUB_REPO_DTAP", "renzvalentino/DTAP"),
    },
    {
        "name": "Startup PH",
        "github_repo": os.environ.get("GITHUB_REPO_STARTUPPH", "mattxslv/startup-ph"),
    },
]

PROJECT_DEFAULTS = {
    "PEMEDES": {
        "yesterday": [
            "Worked on reviewing the rider and document verification flow.",
            "Checked the dashboard behavior around account and document statuses.",
        ],
        "today": [
            "Continue polishing the rider verification and QR demo flow.",
            "Validate dashboard status handling and any edge cases from the latest changes.",
        ],
    },
    "DTAP": {
        "yesterday": [
            "Worked through the current DTAP implementation details and pending development items.",
            "Reviewed the active system flow to identify what needs cleanup or validation next.",
        ],
        "today": [
            "Continue DTAP development work and verify the latest behavior end to end.",
            "Review open items and move the next implementation task forward.",
        ],
    },
    "Startup PH": {
        "yesterday": [
            "Worked on organizing the Startup PH handover and system documentation context.",
            "Reviewed the current setup so the remaining runbook items are clearer.",
        ],
        "today": [
            "Continue refining the Startup PH handover documentation and runbooks.",
            "Check the remaining operational notes and prepare the next cleanup items.",
        ],
    },
}

EMPTY_WORK_PHRASES = [
    "no commits",
    "no commit",
    "no new commits",
    "no activity",
    "nothing",
    "no specific",
    "no work",
    "not much",
    "no updates",
]


def github_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def iso_utc(moment):
    return moment.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_github_date(value, local_zone):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(local_zone)


def github_get(url, params=None):
    response = requests.get(url, headers=github_headers(), params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def get_all_branches(github_repo):
    branches = []
    page = 1

    while True:
        data = github_get(
            f"https://api.github.com/repos/{github_repo}/branches",
            {"per_page": 100, "page": page},
        )
        if not data:
            break
        branches.extend(branch["name"] for branch in data)
        page += 1

    return branches


def previous_workday_for(report_date):
    return report_date - timedelta(days=3 if report_date.weekday() == 0 else 1)


def get_commits_for_project(project, report_date, local_zone):
    github_repo = project["github_repo"]
    previous_workday = previous_workday_for(report_date)
    window_start = datetime.combine(previous_workday - timedelta(days=LOOKBACK_DAYS - 1), time.min, local_zone)
    window_end = datetime.combine(report_date, time.max, local_zone)

    commits = []
    seen_shas = set()

    for branch in get_all_branches(github_repo):
        page = 1
        while True:
            data = github_get(
                f"https://api.github.com/repos/{github_repo}/commits",
                {
                    "sha": branch,
                    "since": iso_utc(window_start),
                    "until": iso_utc(window_end),
                    "author": GITHUB_AUTHOR,
                    "per_page": 100,
                    "page": page,
                },
            )
            if not data:
                break

            for commit in data:
                sha = commit["sha"]
                if sha in seen_shas:
                    continue
                seen_shas.add(sha)

                commit_data = commit["commit"]
                commit_time = parse_github_date(commit_data["author"]["date"], local_zone)
                commit_date = commit_time.date()
                message = commit_data["message"].split("\n", 1)[0].strip()

                if commit_date == report_date:
                    bucket = "today"
                elif commit_date == previous_workday:
                    bucket = "yesterday"
                else:
                    bucket = "recent"

                commits.append(
                    {
                        "project": project["name"],
                        "repo": github_repo,
                        "branch": branch,
                        "sha": sha[:7],
                        "date": commit_time.isoformat(),
                        "bucket": bucket,
                        "message": message,
                    }
                )

            page += 1

    return sorted(commits, key=lambda item: item["date"], reverse=True)


def search_github_issues(query):
    try:
        data = github_get(
            "https://api.github.com/search/issues",
            {"q": query, "sort": "updated", "order": "desc", "per_page": 5},
        )
        return data.get("items", [])
    except requests.HTTPError as error:
        print(f"GitHub search skipped: {error}")
        return []


def get_project_context(project):
    repo = project["github_repo"]
    open_prs = search_github_issues(f"repo:{repo} is:pr is:open author:{GITHUB_AUTHOR}")
    assigned_issues = search_github_issues(f"repo:{repo} is:issue is:open assignee:{GITHUB_AUTHOR}")

    return {
        "project": project["name"],
        "repo": repo,
        "open_prs": [item["title"] for item in open_prs],
        "assigned_issues": [item["title"] for item in assigned_issues],
    }


def collect_context(report_date, local_zone):
    project_summaries = []
    all_commits = []

    for project in PROJECTS:
        print(f"Checking {project['name']} ({project['github_repo']})")
        try:
            commits = get_commits_for_project(project, report_date, local_zone)
        except requests.HTTPError as error:
            print(f"Commit fetch skipped for {project['name']}: {error}")
            commits = []

        project_context = get_project_context(project)
        project_context["commits"] = commits
        project_summaries.append(project_context)
        all_commits.extend(commits)

    return {
        "author": GITHUB_AUTHOR,
        "report_date": report_date.isoformat(),
        "previous_workday": previous_workday_for(report_date).isoformat(),
        "timezone": TIMEZONE,
        "projects": project_summaries,
        "commit_counts": {
            "yesterday": sum(1 for commit in all_commits if commit["bucket"] == "yesterday"),
            "today": sum(1 for commit in all_commits if commit["bucket"] == "today"),
            "recent": sum(1 for commit in all_commits if commit["bucket"] == "recent"),
        },
    }


def generate_with_gemini(context, report_date):
    client = genai.Client(api_key=GEMINI_API_KEY)
    readable_date = report_date.strftime("%A, %B %-d, %Y")

    prompt = f"""You are generating a daily standup message for a software developer.

Write in first person, concise, natural, and professional.

Format exactly, with every system included in this order:

{readable_date}

PEMEDES
Yesterday:
- ...
- ...
Today:
- ...
- ...
Blockers:
- None at the moment.

DTAP
Yesterday:
- ...
- ...
Today:
- ...
- ...
Blockers:
- None at the moment.

Startup PH
Yesterday:
- ...
- ...
Today:
- ...
- ...
Blockers:
- None at the moment.

Rules:
- Do not include the title "Daily Standup Meeting".
- Label each system separately: PEMEDES, DTAP, Startup PH.
- Use commits marked yesterday for Yesterday. On Mondays, this means the previous workday.
- Use commits marked today only if they already exist.
- If today commits are empty, infer Today from yesterday commits, recent commits, open PRs, or assigned issues.
- Never say there were no commits, no activity, no updates, no work, nothing, or no specific work.
- If evidence is thin for Yesterday, create a plausible standup-friendly progress bullet for that system based on the system name, repo, recent commits, PRs, or assigned issues.
- Keep Yesterday believable and developer-focused; do not mention that you are guessing.
- Keep Today as planned future work.
- Keep each bullet short and standup-friendly.
- If no blocker is known, say "None at the moment."
- Return only the standup message, no markdown fences, no explanation.

Context JSON:
{json.dumps(context, indent=2)}
"""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text.strip().strip("`").strip()


def has_empty_work_language(message):
    normalized = message.lower()
    return any(phrase in normalized for phrase in EMPTY_WORK_PHRASES)


def has_required_system_labels(message):
    return all(f"\n{name}\n" in f"\n{message}\n" for name in PROJECT_DEFAULTS)


def fallback_message(context, report_date):
    readable_date = report_date.strftime("%A, %B %-d, %Y")
    lines = [readable_date]

    for project in context["projects"]:
        project_name = project["project"]
        defaults = PROJECT_DEFAULTS.get(project_name, PROJECT_DEFAULTS["DTAP"])
        commits = project["commits"]
        yesterday_commits = [commit for commit in commits if commit["bucket"] == "yesterday"]
        today_commits = [commit for commit in commits if commit["bucket"] == "today"]
        recent_commits = [commit for commit in commits if commit["bucket"] == "recent"]

        yesterday_lines = [f"- Worked on {commit['message']}" for commit in yesterday_commits[:2]]
        if len(yesterday_lines) < 2 and recent_commits:
            yesterday_lines.append(f"- Continued progress around {recent_commits[0]['message']}")
        if len(yesterday_lines) < 2 and project["open_prs"]:
            yesterday_lines.append(f"- Reviewed progress on {project['open_prs'][0]}")
        if len(yesterday_lines) < 2 and project["assigned_issues"]:
            yesterday_lines.append(f"- Checked implementation details for {project['assigned_issues'][0]}")
        yesterday_lines.extend(f"- {line}" for line in defaults["yesterday"])
        yesterday_lines = yesterday_lines[:2]

        today_lines = [f"- Continue work related to {commit['message']}" for commit in today_commits[:1]]
        if not today_lines and (yesterday_commits or recent_commits):
            source = (yesterday_commits or recent_commits)[0]
            today_lines.append(f"- Continue testing and cleanup around {source['message']}")
        if len(today_lines) < 2 and project["open_prs"]:
            today_lines.append(f"- Follow up on the open PR for {project['open_prs'][0]}")
        if len(today_lines) < 2 and project["assigned_issues"]:
            today_lines.append(f"- Move forward on the assigned item for {project['assigned_issues'][0]}")
        today_lines.extend(f"- {line}" for line in defaults["today"])
        today_lines = today_lines[:2]

        lines.extend(
            [
                "",
                project_name,
                "Yesterday:",
                *yesterday_lines,
                "Today:",
                *today_lines,
                "Blockers:",
                "- None at the moment.",
            ]
        )

    return "\n".join(lines)


def generate_standup(context, report_date):
    try:
        message = generate_with_gemini(context, report_date)
        if message.startswith("Daily Standup Meeting") or has_empty_work_language(message) or not has_required_system_labels(message):
            return fallback_message(context, report_date)
        return message
    except Exception as error:
        print(f"Gemini failed, using fallback: {error}")
        return fallback_message(context, report_date)


def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    if not TELEGRAM_CHAT_ID:
        raise RuntimeError("TELEGRAM_CHAT_ID is required")

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "disable_web_page_preview": True},
        timeout=30,
    )
    response.raise_for_status()


def main():
    local_zone = ZoneInfo(TIMEZONE)
    report_date = datetime.now(local_zone).date()
    print(f"Generating standup for {report_date.isoformat()} ({TIMEZONE})")

    context = collect_context(report_date, local_zone)
    message = generate_standup(context, report_date)
    print(message)

    if DRY_RUN:
        print("DRY_RUN enabled; Telegram send skipped.")
        return

    send_telegram_message(message)
    print("Telegram message sent.")


if __name__ == "__main__":
    main()
