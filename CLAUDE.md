# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## 5. Post-Implementation Checklist

After completing any change, review the diff and answer:

1. **Scope control** — Did the change stay within the requested scope, or did it touch unrelated files?
2. **File boundaries** — Were any files modified that should not have been touched?
3. **Compatibility** — Are interfaces and data structures backward-compatible?
4. **Error handling** — Are edge cases and abnormal states handled properly?
5. **Maintainability** — Was any hard-to-maintain duplicated logic introduced?
6. **Code hygiene** — Is there dead code, hardcoded values, or leftover debug output?

---

## Project State (ai-console)

### Mock Data Cleanup
- All `.js` mock files under `ai-console/src/mock/` have been deleted.
- Inline hardcoded `ref([...])` mock data removed from Vue views:
  - `Events.vue`, `DataClean.vue`, `Firmware.vue`, and others.

### Database Seeds
- **Menus**: `scripts/seed_menus.py` inserts 42 menu records matching frontend routes.
- **Resources**: `scripts/seed_resources.py` dynamically extracts all FastAPI routes (`app.routes`) and inserts 191 permission records grouped by `resource_group` + `service_code`.

### Ports & URLs
- Frontend dev server: `http://localhost:5173` (Vite)
- Backend: `http://127.0.0.1:8000`
- Vite proxy (`vite.config.ts`): `/api` → `http://127.0.0.1:8080` **(mismatch — backend runs on 8000)**
- Database: PostgreSQL on port `5434`

### Environment
- Conda env: `llm_deng`
- Python path: `/home/daxiong/tool/miniconda3/envs/llm_deng/bin/python`
- Run seeds with: `DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/ai_console" python scripts/seed_xxx.py`
