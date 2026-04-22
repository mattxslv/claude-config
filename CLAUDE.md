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

Commits are automatically grouped and posted as closed GitLab work items every day at 11pm PHT via a Cloud Run Job.

- **Job**: `gitlab-daily-job` on GCP project `ai-innov-474401`, region `asia-southeast1`
- **Scheduler**: Cloud Scheduler `gitlab-daily-update` — `0 15 * * *` UTC (= 11pm PHT)
- **Script**: `~/.claude/gitlab-daily/main.py` — pulls from GitHub `staging` branch, groups with Gemini, creates+closes GitLab issues
- **Config**: `~/.claude/.gitlab-config` (GitLab token + project ID)
- **To trigger manually**: `gcloud run jobs execute gitlab-daily-job --region asia-southeast1 --project ai-innov-474401`
- **To update the script**: edit `~/.claude/gitlab-daily/main.py`, then run `gcloud builds submit --tag gcr.io/ai-innov-474401/gitlab-daily-job:latest --project ai-innov-474401 ~/.claude/gitlab-daily/`

# Pre-Push Checklist (universal)
Before every `git push`:
1. Run `tsc --noEmit` (or equivalent type check) — zero errors
2. Run the project build — must succeed
3. Check for any new env vars added — verify they exist in the deployment environment
4. All SQL queries must be parameterized — never string concatenation with user input
5. All new API routes must have auth checks
