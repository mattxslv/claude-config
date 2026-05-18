---
name: skills-updater
description: Reviews completed work and updates relevant skill files with new learnings. Run after finishing a significant piece of work to keep skills accurate and useful.
user-invocable: true
argument-hint: "[what was just built or fixed]"
---

## Purpose

Skills rot if they're never updated. After non-trivial work, check if any skill files should be improved with what was just learned.

## When to run

After:
- Fixing a bug caused by a pattern that should be avoided
- Discovering a new convention or pattern in the codebase
- Adding a new project (new CLAUDE.md, test-guide, etc.)
- Finding that a skill's instructions didn't match reality

Not needed after: small fixes, typo corrections, minor UI tweaks.

## Step 1 — What changed?

Review the work just completed:
- What was built or fixed?
- What was discovered that wasn't obvious before?
- Did any step go wrong that a skill could have prevented?
- Was there a pattern or decision worth remembering?

## Step 2 — Which skills are relevant?

Check the skills directory:
```bash
ls ~/.claude/skills/
```

Match the work to skills:
- Added a new feature flow → `developer-onboarding` (add the pattern)
- Found a WAF gotcha → `developer-onboarding` (add the constraint)
- Researched an API → `research-onboarding` (add search strategy if novel)
- Built something after planning → `planner-onboarding` (add what to check)
- Uncovered project-specific bug pattern → the relevant project's CLAUDE.md

## Step 3 — Update precisely

Only add what's genuinely new. Don't pad or rewrite. Insert:
- A concise bullet under the relevant section
- Or a new "gotcha" entry if it's a prod-breaking pattern
- Or a new command/pattern if it's a common operation

**Format for gotchas:**
```
- [What you did] → [What broke] — [How to avoid it]
```

**Format for patterns:**
```
- [When to use]: [How to do it correctly]
```

## Step 4 — Commit the updates

```bash
cd ~/.claude
git add skills/
git commit -m "Update skills after [brief description of work]"
git push
```

## Rules

- Update only what's actually new — don't rewrite existing content
- If a skill's instruction was wrong and you fixed it, mark the old entry as replaced, don't just add a note
- If a project's CLAUDE.md needs updating (new bug pattern, new pattern), update that too
- Keep updates short — one or two lines per insight is usually enough
