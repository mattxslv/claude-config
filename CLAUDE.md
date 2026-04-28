# Preferences

- Always pull before starting work on a git repo
- Always commit after completing work (with good commit messages)
- Be concise, skip explanations unless asked
- Use bash on Linux (Arch)
- Never add Co-Authored-By lines to commits — commits should only show the user's name

# Communication & Behavior
- Don't apologize or say "Great question!" — just answer
- Don't add unsolicited suggestions or improvements outside the task
- Don't explain what you're about to do — just do it
- Ask for clarification before starting complex tasks, not midway through
- If unsure, say so instead of guessing

# Code Style
- Prefer explicit over clever — readability over brevity
- No comments unless the logic is genuinely non-obvious
- Don't add TODO comments — either do it or don't
- No console.log left in production code
- Fail loudly — no silent error swallowing
- Prefer editing existing files over creating new ones
- Don't create files "just in case" — only what's needed
- Don't refactor code that wasn't part of the task
- Complete tasks fully — no half-implementations

# Git & Commits
- Commit messages: imperative mood, concise subject line
- Never amend pushed commits
- Commit related changes together, unrelated ones separately
- Always commit after completing work

# Testing
- Don't write tests unless explicitly asked
- When asked for tests, test behavior not implementation

# When Things Go Wrong
- When a fix doesn't work, diagnose why before trying something else
- Don't retry the exact same thing twice
- If stuck after 2 attempts, stop and explain the situation instead of guessing

# File & Code Hygiene
- Read a file before editing it
- When deleting code, make sure it's actually unused first
- Don't add type annotations to code you didn't change
- Remove dead code instead of commenting it out

# Responses
- Short responses for simple tasks, detailed only when asked
- When showing code, show only the relevant changed parts — not the whole file
- Tables only when data is genuinely tabular
- No bullet points for things that could be one sentence
- Don't pad responses with "I hope this helps!" or similar
- Don't restate what the user just said before answering

# Autonomy & Decisions
- For destructive actions (delete, reset, force push) — always confirm first
- For reversible actions — just do it
- Don't ask permission for every small decision within a task
- Make sensible defaults and explain if asked

# What to Avoid
- Don't over-engineer — simplest solution that works
- Don't add logging/error handling beyond what's needed
- Don't future-proof code for hypothetical requirements
- Don't add features not explicitly asked for
- Never use Playwright — not for testing, not for UI verification, not for any purpose

# GitLab Daily Automation

Automatically groups today's commits by feature and posts them as closed GitLab work items. Uses Gemini to do the grouping intelligently. One Cloud Run job handles all three projects in a single run.

## How it works
- Script: `~/.claude/gitlab-daily/main.py` — reads commits from ALL branches of each GitHub repo, calls Gemini to group by feature, creates+closes GitLab issues
- Config: `~/.claude/.gitlab-config` — shared tokens only (project repos/IDs are hardcoded in the script as defaults)
- GitHub author filter: `mattxslv` (only commits by this author are picked up)
- Automated: runs daily at 11pm PHT (15:00 UTC) via Cloud Run Job + Cloud Scheduler
- Manual: just say "update GitLab" and Claude will trigger it

## Tracked projects (hardcoded in main.py)
| Project | GitHub repo | GitLab project ID |
|---|---|---|
| PEMEDES | `deadPixel505/pemedes-local` | `81356854` (dictcloud/pemedes) |
| DTAP | `renzvalentino/DTAP` | `81354540` |
| Startup PH | `mattxslv/startup-ph` | `81533201` |

To add a new project, add an entry to the `PROJECTS` list in `~/.claude/gitlab-daily/main.py` and rebuild the Docker image.

## Config file (~/.claude/.gitlab-config)
Shared tokens only — project-specific values live in the script:
```
GITLAB_TOKEN=<GitLab personal access token>
GITHUB_TOKEN=<GitHub personal access token>
GEMINI_API_KEY=<Google AI Studio API key>
```

## GCP setup (already live)
- GCP project: `ai-innov-474401`, region: `asia-southeast1`
- Cloud Run job: `gitlab-daily-job`
- Cloud Scheduler: `gitlab-daily-update`, runs at `0 15 * * *` UTC (11pm PHT)

## Rebuild and redeploy (run when main.py changes)
```bash
source ~/.claude/.gitlab-config
gcloud builds submit --tag gcr.io/ai-innov-474401/gitlab-daily-job:latest --project ai-innov-474401 ~/.claude/gitlab-daily/
gcloud run jobs update gitlab-daily-job \
  --image gcr.io/ai-innov-474401/gitlab-daily-job:latest \
  --region asia-southeast1 --project ai-innov-474401
```

## First-time Cloud Run + Scheduler setup (reference, already done)
```bash
source ~/.claude/.gitlab-config

# Create job
gcloud run jobs create gitlab-daily-job \
  --image gcr.io/ai-innov-474401/gitlab-daily-job:latest \
  --region asia-southeast1 --project ai-innov-474401 \
  --set-env-vars "GITLAB_TOKEN=${GITLAB_TOKEN},GITHUB_TOKEN=${GITHUB_TOKEN},GEMINI_API_KEY=${GEMINI_API_KEY}" \
  --max-retries 1 --task-timeout 300

# Create scheduler (11pm PHT = 15:00 UTC)
gcloud scheduler jobs create http gitlab-daily-update \
  --location asia-southeast1 --project ai-innov-474401 \
  --schedule "0 15 * * *" --time-zone "UTC" \
  --uri "https://asia-southeast1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/ai-innov-474401/jobs/gitlab-daily-job:run" \
  --http-method POST \
  --oauth-service-account-email $(gcloud projects describe ai-innov-474401 --format="value(projectNumber)")-compute@developer.gserviceaccount.com
```

## Manual trigger
```bash
gcloud run jobs execute gitlab-daily-job --region asia-southeast1 --project ai-innov-474401
```

## Check logs
```bash
gcloud run jobs executions list --job gitlab-daily-job --region asia-southeast1 --project ai-innov-474401
```

# Pre-Push Checklist (universal)
Before every `git push`:
1. Run `tsc --noEmit` (or equivalent type check) — zero errors
2. Run the project build — must succeed
3. Check for any new env vars added — verify they exist in the deployment environment
4. All SQL queries must be parameterized — never string concatenation with user input
5. All new API routes must have auth checks
