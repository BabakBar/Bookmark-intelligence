---
description: Execute implementation plans phase by phase with verification
---

# Implement

Execute an approved plan from `docs/dev/plans/` with verification at each phase.

## Usage

```
/implement docs/dev/plans/2025-01-29-feature.md
```

## Process

### 1. Read Plan Completely

- Read the FULL plan (no limit/offset)
- Check for existing checkmarks `[x]`
- Read any referenced files
- Understand the complete picture

### 2. Create Todo List

Track your progress through phases with TodoWrite.

### 3. Implement Phase by Phase

For each phase:

**a) Implement the changes**
   - Follow the plan's guidance
   - Adapt if reality differs (communicate why)
   - Think about how pieces fit together

**b) Run automated verification**
   ```bash
   # Usually covered by:
   make test
   make check
   pytest
   mypy
   ruff check
   ```

**c) Fix any issues before proceeding**

**d) Update progress**
   - Check off completed items in the plan file using Edit
   - Update your todo list
   - Mark automated criteria as done

**e) Pause for manual verification**
   ```
   Phase [N] Complete - Ready for Manual Verification

   Automated verification passed:
   ✓ Tests passed
   ✓ Types checked
   ✓ Linting passed

   Please verify manually:
   - [Manual verification item from plan]
   - [Another manual item]

   Let me know when ready for Phase [N+1].
   ```

**f) Wait for user confirmation before next phase**

### 4. Handle Mismatches

If plan doesn't match reality:

```
Issue in Phase [N]:
Expected: [what plan says]
Found: [actual situation]
Why this matters: [explanation]

How should I proceed?
```

### 5. Complete

When all phases done:
- Verify all checkboxes marked
- Run final verification
- Summarize what was accomplished

## Resuming Work

If plan has checkmarks:
- Trust completed work
- Pick up from first unchecked item
- Verify only if something seems off

## Key Points

- **Read fully first** - understand the complete plan
- **One phase at a time** - complete before moving on
- **Verify thoroughly** - run all checks
- **Update progress** - check off items as you go
- **Pause for human** - wait for manual verification
- **Adapt intelligently** - reality might differ from plan

## User Input

```
$ARGUMENTS
```
