---
name: research-onboarding
description: Maps a codebase, API, or system before analyzing or explaining anything. Use when asked to "investigate", "find out how X works", "trace a bug", "understand the architecture", or explain code without immediately changing it.
user-invocable: true
argument-hint: "[what to investigate]"
---

## Purpose

Gather facts before forming opinions. Research mode means no code changes — only reading, mapping, and reporting.

## Step 1 — Orient to the project

```bash
cat CLAUDE.md 2>/dev/null || echo "No CLAUDE.md"
git log --oneline -5             # Recent context
```

## Step 2 — Map the area being investigated

Identify and read the relevant files. Don't read everything — trace the path:

```bash
# Find entry points
find . -name "*.ts" -o -name "*.tsx" | xargs grep -l "keyword" 2>/dev/null | head -10

# Trace API routes
grep -r "route\|endpoint\|handler" --include="*.ts" -l | head -10

# Find where state is managed
grep -r "useState\|useReducer\|zustand\|context" --include="*.tsx" -l | head -10
```

## Step 3 — Build a mental model

Before reporting, answer:
- What is the data flow? (input → transform → output)
- Where does this feature start and end in the code?
- What are the failure modes?
- What dependencies does this touch?

## Step 4 — Report clearly

Structure findings as:
1. **What it does** (one paragraph)
2. **Key files** (list with one-line descriptions)
3. **How it works** (flow, not code dump)
4. **What's unusual or risky** (anything that would surprise a new dev)
5. **Open questions** (what's unclear, what needs confirmation)

## Rules for research mode

- No code edits unless the user explicitly asks
- If you find a bug while researching, report it — don't silently fix it
- Don't summarize what you *assume* — only what you *read*
- If a file is too large, read the relevant sections, not the whole thing
- State uncertainty clearly: "I couldn't find where X is set — it may come from env or a parent component"
