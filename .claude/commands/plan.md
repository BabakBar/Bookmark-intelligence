---
description: Create detailed implementation plan through research and iteration
---

# Plan

Create a phased implementation plan with clear verification criteria. You should be skeptical, thorough, and work collaboratively with the user to produce high-quality technical specifications.

## Process

### 0. Understand the Goal

Ask if not clear:
- What are we building?
- Why is this needed?
- Any constraints or requirements?

### 1. Research Current State

**Read mentioned files FULLY first** (no limit/offset)

Then spawn research agents to investigate:
- Existing implementations
- Patterns to follow
- Integration points
- Dependencies
- Best practices from the web 2025
- Modern and Updated tools/Libraries from the web 2025

Wait for ALL agents before proceeding.

### 2. Present Understanding

```
Based on my research:

Current State:
- [Key finding with file:line]
- [Pattern discovered]

Proposed Approach:
- [High-level strategy]

Questions:
- [Any clarifications needed]
```

Get alignment before continuing.

### 3. Draft Plan Structure

```
Implementation Phases:
1. [Phase] - [what it accomplishes]
2. [Phase] - [what it accomplishes]
3. [Phase] - [what it accomplishes]

Does this make sense?
```

### 4. Research & Discovery

After getting initial clarifications:

1. **If the user corrects any misunderstanding**:
   - DO NOT just accept the correction
   - Spawn new research tasks to verify the correct information
   - Read the specific files/directories they mention
   - Only proceed once you've verified the facts yourself

2. **Create a research todo list** using TodoWrite to track exploration tasks

3. **Spawn parallel sub-tasks for comprehensive research**:
   - Create multiple Task agents to research different aspects concurrently

4. **Wait for ALL sub-tasks to complete** before proceeding

5. **Present findings and design options**:
   ```
   Based on my research, here's what I found:

   **Current State:**
   - [Key discovery about existing code]
   - [Pattern or convention to follow]

   **Design Options:**
   1. [Option A] - [pros/cons]
   2. [Option B] - [pros/cons]

   **Open Questions:**
   - [Technical uncertainty]
   - [Design decision needed]

   Which approach aligns best with your vision?
   ```

### 5. Write Detailed Plan

Once aligned on approach, wrtite a detailed phased implementation plan.

Save to `docs/dev/plans/YYYY-MM-DD-description.md`:

```markdown
# [Feature] Implementation Plan

**Date**: YYYY-MM-DD
**Goal**: [What we're building]

## Current State
[What exists now]

## Desired End State
[What we want + how to verify it]

## What We're NOT Doing
[Out of scope]

## Implementation Approach
[High-level strategy and reasoning]

---

## Phase 1: [Name]

### Changes
**File**: `path/to/file.py`
- [Change 1]
- [Change 2]

### Success Criteria

#### Automated Verification
- [ ] Tests pass: `pytest tests/`
- [ ] Types pass: `mypy .`
- [ ] Lint passes: `ruff check`

#### Manual Verification
- [ ] Feature works via API
- [ ] Edge cases handled
- [ ] No regressions

---

## Phase 2: [Name]
[Same structure...]

---

## Testing Strategy
[How to test this feature]

## References
- Research: `docs/dev/research/[relevant].md`
- Similar code: `file.py:123`
```

### 6. Iterate

Get feedback and refine until ready.

## Key Principles

- **Be skeptical** - question vague requirements
- **Be interactive** - get buy-in at each step
- **Be thorough** - research actual patterns
- **Be practical** - focus on incremental changes
- **No open questions** - resolve everything before finalizing

## User Input

```
$ARGUMENTS
```
