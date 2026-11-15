---
description: Research codebase and technical questions to build understanding
---

# Research

Investigate the codebase, understand implementations, and document findings.

## Scope: document and explain the codebase as it exists today
- Do not suggest improvements or changes unless the user explicitly asks for them
- Do not perform root cause analysis unless the user explicitly asks for it
- Do not propose future enhancements unless the user explicitly asks for them
- Do not critique the implementation or identify problems
- Do not recommend refactoring, optimization, or architectural changes
- Describe what exists, where it exists, how it works, and how components interact
- You are creating a technical map/documentation of the existing system

## When to Use

- Understanding how existing code works
- Investigating technical approaches
- Finding patterns and conventions
- Exploring integration points

## Process

0. **Understand the Question**
   - What are you trying to learn?
   - What context do you need?
   - If the user mentions specific files (tickets, docs, JSON), read them first

1. **Analyze and decompose the research question:**
   - Consider the underlying patterns, connections, and architectural implications the user might be seeking

2. **Investigate**

   Example research areas:
   - How does X currently work?
   - Where is Y implemented?
   - What patterns exist for Z?
   - How do A and B integrate?

   **For web research (only if user asks):**
   - Use the **web-search-researcher** agent for external documentation and resources
   - If you use web-research agents, instruct them to return links with their findings and include those links in your final report
   - Focus on Modern and Updated tools/Libraries from the web 2025

3. **Read Identified Files Completely**
   - Read the relevant files you identified
   - Understand how pieces fit together

4. **Document Findings**
   Create `docs/dev/research/YYYY-MM-DD-topic.md`:

   ```markdown
   # Research: [Topic]

   **Date**: YYYY-MM-DD
   **Question**: [Original question]

   ## Summary
   [High-level findings]

   ## Current Implementation
   - **Component**: `file.py:123` - [what it does]
   - **Pattern**: [how it works]

   ## Key Discoveries
   1. [Important finding]
   2. [Pattern to follow]

   ## References
   - `path/to/file:line` - [description]
   ```

5. **Present Findings**
   - Answer the original question with specifics
   - Include file references
   - Note patterns to follow

## Important

- **Document what EXISTS** - don't suggest improvements
- **Include file:line references** - for easy navigation

## User Input

```
$ARGUMENTS
```

## Important notes:
- You are a documentarian, not an evaluator, and so is any web-research agent you use
- Document what is, not what should be
- Make no recommendations; describe only the current state of the codebase
