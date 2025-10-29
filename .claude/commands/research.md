---
description: Research codebase and technical questions to build understanding
---

# Research

Investigate the codebase, understand implementations, and document findings.

## CRITICAL: YOUR ONLY JOB IS TO DOCUMENT AND EXPLAIN THE CODEBASE AS IT EXISTS TODAY
- DO NOT suggest improvements or changes unless the user explicitly asks for them
- DO NOT perform root cause analysis unless the user explicitly asks for them
- DO NOT propose future enhancements unless the user explicitly asks for them
- DO NOT critique the implementation or identify problems
- DO NOT recommend refactoring, optimization, or architectural changes
- ONLY describe what exists, where it exists, how it works, and how components interact
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
   - If the user mentions specific files (tickets, docs, JSON), read them FULLY first
   - **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
   - **CRITICAL**: Read these files yourself in the main context before spawning any sub-tasks
   - This ensures you have full context before decomposing the research

1. **Analyze and decompose the research question:**
   - Take time to ultrathink about the underlying patterns, connections, and architectural implications the user might be seeking
   - Create a research plan using TodoWrite to track all subtasks

2. **Spawn Parallel Research**
   Use specialized agents to investigate:
   - Run multiple agents in parallel for different aspects
   - **IMPORTANT**: All agents are documentarians, not critics. They will describe what exists without suggesting improvements or identifying issues.

   Example research areas:
   - How does X currently work?
   - Where is Y implemented?
   - What patterns exist for Z?
   - How do A and B integrate?

   **For web research (only if user asks):**
   - Use the **web-search-researcher** agent for external documentation and resources
   - IF you use web-research agents, instruct them to return LINKS with their findings, and please INCLUDE those links in your final report
   - Focus on Modern and Updated tools/Libraries from the web 2025

3. **Read Identified Files Completely**
   - After agents return findings, read ALL relevant files
   - Read files WITHOUT limit/offset (full context needed)
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
- **Read files fully** - need complete context
- **Use parallel agents** - maximize efficiency
- **Include file:line references** - for easy navigation

## User Input

```
$ARGUMENTS
```

## Important notes:
- **CRITICAL**: You and all sub-agents are documentarians, not evaluators
- **REMEMBER**: Document what IS, not what SHOULD BE
- **NO RECOMMENDATIONS**: Only describe the current state of the codebase
