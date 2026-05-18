---
name: developer-onboarding
description: Ramps up on a project before writing code. Use when starting work in a new project directory, picking up a task after context was lost, or when the user says "let's work on X" without providing full context.
user-invocable: true
argument-hint: "[project-path or name]"
---

## Purpose

Get oriented fast before touching any code. This prevents wrong assumptions, duplicate work, and broken builds.

## Step 1 — Read the project rules

```bash
cat CLAUDE.md 2>/dev/null || echo "No CLAUDE.md found"
cat test-guide.md 2>/dev/null || echo "No test-guide.md found"
```

If no CLAUDE.md: ask the user before proceeding — you don't know the stack, conventions, or prod-danger zones.

## Step 2 — Check current state

```bash
git pull                         # Always pull first
git log --oneline -10            # What changed recently
git status                       # Any uncommitted work already here
git branch -a | head -20         # What branches exist
```

## Step 3 — Check the environment

```bash
# Look for env files and package manager
ls -la | grep -E '\.env|package\.json|pnpm-lock|yarn\.lock|go\.mod|requirements|Cargo'
cat package.json 2>/dev/null | jq '.scripts' 2>/dev/null || true
```

## Step 4 — Understand what's being asked

Before writing a single line:
- Confirm the exact task with the user if ambiguous
- Identify which files will be touched
- Check if there are existing tests for the area
- Note any WAF rules, auth requirements, or prod-danger callouts in CLAUDE.md

## Step 5 — Proceed

Now write code. Follow the project's patterns exactly — don't introduce new conventions.

## After completing work

- Run the pre-push checklist from CLAUDE.md (type check, build, env vars, auth on new routes)
- Commit with imperative mood subject line
- Push

## What to never do

- Never `pnpm dev` or `npm run dev` without checking if it hits prod DB (see CLAUDE.md)
- Never start implementing before reading CLAUDE.md
- Never commit without running the type check and build first
