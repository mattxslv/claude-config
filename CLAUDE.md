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
- Don't future-proof code for hypothetical requirementsq
- Don't add features not explicitly asked for

# GitLab Daily Automation

Automatically groups today's commits by feature and posts them as closed GitLab work items. Uses Gemini to do the grouping intelligently.

## How it works
- Script: `~/.claude/gitlab-daily/main.py` — reads commits from GitHub, calls Gemini to group them, creates+closes GitLab issues
- Config: `~/.claude/.gitlab-config` — all tokens and project-specific values live here
- Automated: runs daily at 11pm PHT via Cloud Run Job + Cloud Scheduler (set up once per project)
- Manual: just say "update GitLab" and Claude will trigger it

## Config file (~/.claude/.gitlab-config)
```
GITLAB_BASE_URL=https://gitlab.com
GITLAB_TOKEN=<GitLab personal access token>
GITLAB_PROJECT_ID=<GitLab project numeric ID>
GITLAB_PROJECT_PATH=<group/project-name>

GITHUB_TOKEN=<GitHub personal access token>
GITHUB_REPO=<username/repo>
GITHUB_BRANCH=<branch to track, e.g. staging or main>

GEMINI_API_KEY=<Google AI Studio API key>
```

## Setting up for a new project
1. Update `~/.claude/.gitlab-config` with the new project's values
2. Get GitLab project ID: go to the project → Settings → General → Project ID
3. Get Gemini API key: aistudio.google.com → Get API key → use existing GCP project

## Setting up automated Cloud Run Job (optional, needs GCP)
```bash
# Build and push image (only needed once or when script changes)
gcloud builds submit --tag gcr.io/<GCP_PROJECT>/gitlab-daily-job:latest --project <GCP_PROJECT> ~/.claude/gitlab-daily/

# Create the job (run once per project)
source ~/.claude/.gitlab-config
gcloud run jobs create gitlab-daily-job \
  --image gcr.io/<GCP_PROJECT>/gitlab-daily-job:latest \
  --region asia-southeast1 --project <GCP_PROJECT> \
  --set-env-vars "GITLAB_TOKEN=${GITLAB_TOKEN},GITLAB_PROJECT_ID=${GITLAB_PROJECT_ID},GITHUB_TOKEN=${GITHUB_TOKEN},GITHUB_REPO=${GITHUB_REPO},GITHUB_BRANCH=${GITHUB_BRANCH},GEMINI_API_KEY=${GEMINI_API_KEY},GCP_PROJECT_ID=<GCP_PROJECT>,VERTEX_REGION=us-east5" \
  --max-retries 1 --task-timeout 300

# Create Cloud Scheduler (11pm PHT = 15:00 UTC)
gcloud scheduler jobs create http gitlab-daily-update \
  --location asia-southeast1 --project <GCP_PROJECT> \
  --schedule "0 15 * * *" --time-zone "UTC" \
  --uri "https://asia-southeast1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/<GCP_PROJECT>/jobs/gitlab-daily-job:run" \
  --http-method POST \
  --oauth-service-account-email <PROJECT_NUMBER>-compute@developer.gserviceaccount.com
```

## Manual trigger
```bash
gcloud run jobs execute gitlab-daily-job --region asia-southeast1 --project <GCP_PROJECT>
```

## Current project (pemedes)
- GCP project: `ai-innov-474401`, region: `asia-southeast1`
- GitLab: `dictcloud/pemedes` (ID: `81356854`)
- GitHub: `deadPixel505/pemedes-local`, branch: `staging`

# Pre-Push Checklist (universal)
Before every `git push`:
1. Run `tsc --noEmit` (or equivalent type check) — zero errors
2. Run the project build — must succeed
3. Check for any new env vars added — verify they exist in the deployment environment
4. All SQL queries must be parameterized — never string concatenation with user input
5. All new API routes must have auth checks
