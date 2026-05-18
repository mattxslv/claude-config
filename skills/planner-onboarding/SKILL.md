---
name: planner-onboarding
description: Plans a feature or sprint before any implementation starts. Use when asked to build something new, plan a sprint, break down a feature, create a PRD, or when the user says "let's add X" for anything non-trivial.
user-invocable: true
argument-hint: "[feature or sprint goal]"
---

## Purpose

Think before building. The cost of a wrong plan is higher than the cost of spending 5 minutes planning.

## Step 1 — Understand the ask

Before anything else, answer:
- What problem does this solve?
- Who uses it and what do they need?
- What's the simplest version that would work?
- What's explicitly out of scope?

If you can't answer these, ask the user now — not mid-implementation.

## Step 2 — Read the project context

```bash
cat CLAUDE.md 2>/dev/null
git log --oneline -10            # Recent work — avoid duplicate effort
```

Look for:
- Existing patterns to follow (don't invent new ones)
- Constraints (WAF rules, DB constraints, auth requirements)
- Current focus area (what's already in progress)

## Step 3 — Map the impact

Identify every file and system that will change:
- New pages / routes
- New API endpoints
- DB schema changes
- New env vars or secrets
- Auth / permission changes
- Third-party services touched

## Step 4 — Write the plan

Present a clear plan in this format:

```
## Plan: [Feature Name]

### What it does
[1-2 sentences]

### Files changing
- `path/to/file.ts` — what changes and why
- ...

### New things being created
- `path/to/new.ts` — what it does
- ...

### Order of implementation
1. [Step] — [why this first]
2. ...

### Risks / open questions
- [Anything that could go wrong]
- [Decisions that need the user's input]

### NOT included
- [What's intentionally out of scope]
```

## Step 5 — Get approval

Present the plan. Do not write code until the user confirms the approach.

If the user approves: proceed step by step. Mark each step done as you complete it.

## Rules

- No implementation before plan approval
- Flag any dependencies that could block the plan (missing env vars, external APIs, etc.)
- If a step reveals something unexpected, stop and update the plan before continuing
- For DB schema changes: write migrations, don't edit tables directly
