# [Project Name]

> One sentence: what this does and who it's for.

---

## What This Is

[2-3 sentences. The core problem, the user, the solution. No fluff.]

---

## Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Language | | |
| Framework | | |
| Database | | |
| Auth | | |
| Hosting | | |
| CI/CD | | |
| Other | | |

---

## Architecture

[How the system is structured. Monolith / API + SPA / microservices / etc. Key patterns used.]

### Directory Layout

```
/
├── ...     # describe what lives where
```

### Data Flow

[How data moves through the system. API → service → DB, or wherever it gets complex.]

---

## Key Decisions

These were decided intentionally. Don't change them without asking.

- **[Decision]** — [why]
- **[Decision]** — [why]

Examples:
- All DB queries live in `/db/queries/` — no inline SQL elsewhere
- No ORM — raw SQL only
- All new API routes require auth middleware
- No `any` in TypeScript — use explicit types or `unknown`

---

## Project Structure Rules

- Where do new API routes go?
- Where do new components go?
- Where do types live?
- Where do DB queries live?
- Naming conventions (files, functions, variables)?

---

## Environment Variables

All vars documented in `.env.example`. Never hardcode values.

| Var | Purpose |
|---|---|
| | |

---

## Design

[Link to Figma or describe the design system. Color palette, component library used, fonts.]

Figma: [link]

---

## Current Focus

> Update this as the project evolves — it's the most-read section.

What we're actively building right now. What's done. What's next.

**Done:**
- 

**In progress:**
- 

**Next:**
- 

---

## What Claude Should Never Do Here

- [project-specific constraints]
- Example: Never modify the DB schema directly — migrations only
- Example: Never add dependencies without checking bundle size impact
- Example: Never use `localStorage` for auth tokens — use httpOnly cookies
