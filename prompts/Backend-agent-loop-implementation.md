# Session: Backend agent loop implementation

**Session ID:** ses_16f53d7a4ffeduqpmAaOUEghiF

**Agent:** build

**Model:** llama/default

**Messages:** 9

---

## User (1)

## User Input

```text
Spec implementation of the agent loop in backend/ as defined in @Technical Assessment (1).html 
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before specification)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_specify` key
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Outline

The text the user typed after `/speckit.specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `Spec implementation of the agent loop in backend/ as defined in @Technical Assessment (1).html ` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate a concise short name** (2-4 words) for the feature:
   - Analyze the feature description and extract the most meaningful keywords
   - Create a 2-4 word short name that captures the essence of the feature
   - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
   - Keep it concise but descriptive enough to understand the feature at a glance
   - Examples:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **Branch creation** (optional, via hook):

   If a `before_specify` hook ran successfully in the Pre-Execution Checks above, it will have created/switched to a git branch and output JSON containing `BRANCH_NAME` and `FEATURE_NUM`. Note these values for reference, but the branch name does **not** dictate the spec directory name.

   If the user explicitly provided `GIT_BRANCH_NAME`, pass it through to the hook so the branch script uses the exact value as the branch name (bypassing all prefix/suffix generation).

3. **Create the spec feature directory**:

   Specs live under the default `specs/` directory unless the user explicitly provides `SPECIFY_FEATURE_DIRECTORY`.

   **Resolution order for `SPECIFY_FEATURE_DIRECTORY`**:
   1. If the user explicitly provided `SPECIFY_FEATURE_DIRECTORY` (e.g., via environment variable, argument, or configuration), use it as-is
   2. Otherwise, auto-generate it under `specs/`:
      - Check `.specify/init-options.json` for `branch_numbering`
      - If `"timestamp"`: prefix is `YYYYMMDD-HHMMSS` (current timestamp)
      - If `"sequential"` or absent: prefix is `NNN` (next available 3-digit number after scanning existing directories in `specs/`)
      - Construct the directory name: `<prefix>-<short-name>` (e.g., `003-user-auth` or `20260319-143022-user-auth`)
      - Set `SPECIFY_FEATURE_DIRECTORY` to `specs/<directory-name>`

   **Create the directory and spec file**:
   - `mkdir -p SPECIFY_FEATURE_DIRECTORY`
   - Resolve the active `spec-template` through the Spec Kit preset/template resolution stack (equivalent to `specify preset resolve spec-template`)
   - Copy the resolved `spec-template` file to `SPECIFY_FEATURE_DIRECTORY/spec.md` as the starting point
   - Set `SPEC_FILE` to `SPECIFY_FEATURE_DIRECTORY/spec.md`
   - Persist the resolved path to `.specify/feature.json`:
     ```json
     {
       "feature_directory": "<resolved feature dir>"
     }
     ```
     Write the actual resolved directory path value (for example, `specs/003-user-auth`), not the literal string `SPECIFY_FEATURE_DIRECTORY`.
     This allows downstream commands (`/speckit.plan`, `/speckit.tasks`, etc.) to locate the feature directory without relying on git branch name conventions.

   **IMPORTANT**:
   - You must only create one feature per `/speckit.specify` invocation
   - The spec directory name and the git branch name are independent — they may be the same but that is the user's choice
   - The spec directory and file are always created by this command, never by the hook

4. Load the resolved active `spec-template` file to understand required sections.

5. **IF EXISTS**: Load `.specify/memory/constitution.md` for project principles and governance constraints.

6. Follow this execution flow:
    1. Parse user description from arguments
       If empty: ERROR "No feature description provided"
    2. Extract key concepts from description
       Identify: actors, actions, data, constraints
    3. For unclear aspects:
       - Make informed guesses based on context and industry standards
       - Only mark with [NEEDS CLARIFICATION: specific question] if:
         - The choice significantly impacts feature scope or user experience
         - Multiple reasonable interpretations exist with different implications
         - No reasonable default exists
       - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
       - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
    4. Fill User Scenarios & Testing section
       If no clear user flow: ERROR "Cannot determine user scenarios"
    5. Generate Functional Requirements
       Each requirement must be testable
       Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
    6. Define Success Criteria
       Create measurable, technology-agnostic outcomes
       Include both quantitative metrics (time, performance, volume) and qualitative measures (user satisfaction, task completion)
       Each criterion must be verifiable without implementation details
    7. Identify Key Entities (if data involved)
    8. Return: SUCCESS (spec ready for planning)

6. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.

7. **Specification Quality Validation**: After writing the initial spec, validate it against quality criteria:

   a. **Create Spec Quality Checklist**: Generate a checklist file at `SPECIFY_FEATURE_DIRECTORY/checklists/requirements.md` using the checklist template structure with these validation items:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]
      
      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]
      
      ## Content Quality
      
      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed
      
      ## Requirement Completeness
      
      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified
      
      ## Feature Readiness
      
      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification
      
      ## Notes
      
      - Items marked incomplete require spec updates before `/speckit.clarify` or `/speckit.plan`
      ```

   b. **Run Validation Check**: Review the spec against each checklist item:
      - For each item, determine if it passes or fails
      - Document specific issues found (quote relevant spec sections)

   c. **Handle Validation Results**:

      - **If all items pass**: Mark checklist complete and proceed to the Mandatory Post-Execution Hooks section

      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues
        2. Update the spec to address each issue
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues in checklist notes and warn user

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 3 markers exist, keep only the 3 most critical (by scope/security/UX impact) and make informed guesses for the rest
        3. For each clarification needed (max 3), present options to user in this format:

           ```markdown
           ## Question [N]: [Topic]
           
           **Context**: [Quote relevant spec section]
           
           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]
           
           **Suggested Answers**:
           
           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |
           
           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted:
           - Use consistent spacing with pipes aligned
           - Each cell should have spaces around content: `| Content |` not `|Content|`
           - Header separator must have at least 3 dashes: `|--------|`
           - Test that the table renders correctly in markdown preview
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting for responses
        7. Wait for user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update the spec by replacing each [NEEDS CLARIFICATION] marker with the user's selected or provided answer
        9. Re-run validation after all clarifications are resolved

   d. **Update Checklist**: After each validation iteration, update the checklist file with current pass/fail status

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_specify`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_specify` key.
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue to the Completion Report.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Mandatory hook** (`optional: false`) — **You MUST emit `EXECUTE_COMMAND:` for each mandatory hook**:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## Completion Report

Report completion to the user with:
- `SPECIFY_FEATURE_DIRECTORY` — the feature directory path
- `SPEC_FILE` — the spec file path
- Checklist results summary
- Readiness for the next phase (`/speckit.clarify` or `/speckit.plan`)

**NOTE:** Branch creation is handled by the `before_specify` hook (git extension). Spec directory and file creation are always handled by this core command.

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- DO NOT create any checklists that are embedded in the spec. That will be a separate command.

### Section Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation

When creating this spec from a user prompt:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions that:
   - Significantly impact feature scope or user experience
   - Have multiple reasonable interpretations with different implications
   - Lack any reasonable default
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
6. **Common areas needing clarification** (only if no reasonable default exists):
   - Feature scope and boundaries (include/exclude specific use cases)
   - User types and permissions (if multiple conflicting interpretations possible)
   - Security/compliance requirements (when legally/financially significant)

**Examples of reasonable defaults** (don't ask about these):

- Data retention: Industry-standard practices for the domain
- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: Use project-appropriate patterns (REST/GraphQL for web services, function calls for libraries, CLI args for tools, etc.)

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective, not system internals
4. **Verifiable**: Can be tested/validated without knowing implementation details

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical, use "Users see results instantly")
- "Database can handle 1000 TPS" (implementation detail, use user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)

## Done When

- [ ] Specification written to `SPEC_FILE` and validated against quality checklist
- [ ] Extension hooks dispatched or skipped according to the rules in Mandatory Post-Execution Hooks above
- [ ] Completion reported to user with feature directory, spec file path, and checklist results
Called the Read tool with the following input: {"filePath":"/var/home/peter/Repos/Personal/ElevateIQ-AgentKit/Technical Assessment (1).html"}
<path>/var/home/peter/Repos/Personal/ElevateIQ-AgentKit/Technical Assessment (1).html</path>
<type>file</type>
<content>
1: <!DOCTYPE html>
2: <html lang="en-AU">
3: <head>
4: <meta charset="UTF-8" />
5: <meta name="viewport" content="width=device-width, initial-scale=1.0" />
6: <title>ExpandIQ AgentKit Take-Home</title>
7: <style>
8:   :root {
9:     --bg: #0b1020;
10:     --panel: #121830;
11:     --panel-2: #171f3d;
12:     --border: #263058;
13:     --text: #e6e9f5;
14:     --muted: #9aa3c4;
15:     --accent: #6aa6ff;
16:     --accent-2: #b98bff;
17:     --ok: #4ade80;
18:     --warn: #facc15;
19:     --hard: #f87171;
20:     --tag: #2a355f;
21:   }
22:   [data-theme="light"] {
23:     --bg: #f6f7fb;
24:     --panel: #ffffff;
25:     --panel-2: #f0f2f8;
26:     --border: #dfe3ef;
27:     --text: #12162a;
28:     --muted: #5a6485;
29:     --accent: #2563eb;
30:     --accent-2: #7c3aed;
31:     --tag: #e6ebf5;
32:   }
33:   * { box-sizing: border-box; }
34:   html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif; line-height: 1.6; }
35:   header {
36:     padding: 22px 32px 18px;
37:     border-bottom: 1px solid var(--border);
38:     background: linear-gradient(135deg, rgba(106,166,255,0.08), rgba(185,139,255,0.06));
39:     position: sticky; top: 0; z-index: 10; backdrop-filter: blur(8px);
40:   }
41:   .header-top { display: flex; align-items: center; gap: 16px; justify-content: space-between; }
42:   .header-text { flex: 1; min-width: 0; }
43:   .logo-wrap { flex-shrink: 0; padding: 6px 10px; background: rgba(255,255,255,0.92); border-radius: 8px; }
44:   [data-theme="light"] .logo-wrap { background: transparent; padding: 0; }
45:   .logo { height: 44px; width: auto; display: block; }
46:   h1 { margin: 0 0 4px; font-size: 22px; letter-spacing: -0.01em; }
47:   h1 .accent { color: var(--accent); }
48:   .sub { color: var(--muted); font-size: 13px; }
49:   .meta-bar { display: flex; gap: 16px; margin-top: 12px; flex-wrap: wrap; font-size: 13px; }
50:   .meta-bar .pill { background: var(--panel-2); border: 1px solid var(--border); padding: 4px 10px; border-radius: 999px; color: var(--muted); }
51:   .meta-bar .pill strong { color: var(--text); }
52: 
53:   .toolbar { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
54:   .toolbar button {
55:     background: var(--panel); color: var(--text); border: 1px solid var(--border);
56:     border-radius: 8px; padding: 7px 12px; font-size: 13px; cursor: pointer;
57:   }
58:   .toolbar button:hover { border-color: var(--accent); }
59:   .toolbar .progress { margin-left: auto; color: var(--muted); font-size: 12px; align-self: center; }
60: 
61:   .layout {
62:     max-width: 1200px; margin: 0 auto; padding: 24px 32px 64px;
63:     display: grid; grid-template-columns: minmax(0, 1fr) 200px; gap: 32px;
64:     align-items: start;
65:   }
66:   main { min-width: 0; }
67: 
68:   section.block {
69:     background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
70:     padding: 22px 26px; margin-bottom: 18px;
71:   }
72:   section.block h2 {
73:     margin: 0 0 14px; font-size: 16px; letter-spacing: 0.03em; text-transform: uppercase;
74:     color: var(--accent); display: flex; align-items: center; gap: 10px;
75:   }
76:   section.block h2 .idx {
77:     background: var(--panel-2); color: var(--muted); padding: 2px 8px; border-radius: 6px;
78:     font-size: 12px; font-weight: 600;
79:   }
80:   section.block h3 { margin: 20px 0 10px; font-size: 14.5px; color: var(--accent-2); }
81:   section.block p { margin: 10px 0; font-size: 14.5px; }
82:   section.block ul, section.block ol { margin: 10px 0 10px 20px; padding: 0; }
83:   section.block li { margin: 8px 0; font-size: 14.5px; }
84:   section.block code { background: var(--panel-2); padding: 1px 6px; border-radius: 4px; font-size: 13px; }
85:   section.block pre { background: var(--panel-2); padding: 12px 14px; border-radius: 8px; overflow-x: auto; font-size: 13px; border: 1px solid var(--border); margin: 12px 0; }
86:   section.block table {
87:     width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px;
88:   }
89:   section.block th, section.block td {
90:     text-align: left; padding: 10px 12px; border: 1px solid var(--border); vertical-align: top;
91:   }
92:   section.block th { background: var(--panel-2); color: var(--muted); font-weight: 600; }
93: 
94:   .callout {
95:     padding: 14px 18px; border-radius: 8px; margin: 14px 0;
96:     border-left: 3px solid var(--accent);
97:     background: rgba(106,166,255,0.07);
98:   }
99:   .callout.warn { border-color: var(--warn); background: rgba(250,204,21,0.08); }
100:   .callout.ok { border-color: var(--ok); background: rgba(74,222,128,0.08); }
101:   .callout.hard { border-color: var(--hard); background: rgba(248,113,113,0.08); }
102:   .callout strong { color: var(--text); }
103: 
104:   .checklist { list-style: none; margin: 0; padding: 0; }
105:   .checklist li {
106:     display: flex; align-items: flex-start; gap: 10px; padding: 8px 0;
107:     border-bottom: 1px dashed var(--border);
108:   }
109:   .checklist li:last-child { border-bottom: none; }
110:   .checklist input[type="checkbox"] {
111:     margin-top: 4px; width: 16px; height: 16px; accent-color: var(--accent); cursor: pointer;
112:   }
113:   .checklist label { flex: 1; cursor: pointer; font-size: 14px; }
114:   .checklist li.done label { color: var(--muted); text-decoration: line-through; }
115: 
116:   .toc {
117:     position: sticky; top: 160px; font-size: 13px; align-self: start;
118:   }
119:   .toc a {
120:     display: block; color: var(--muted); text-decoration: none;
121:     padding: 4px 8px; border-left: 2px solid transparent; border-radius: 0 4px 4px 0;
122:   }
123:   .toc a:hover, .toc a.active { color: var(--accent); border-left-color: var(--accent); background: var(--panel-2); }
124: 
125:   footer { text-align: center; color: var(--muted); font-size: 12px; padding: 24px 0; border-top: 1px solid var(--border); }
126: 
127:   @media (max-width: 900px) {
128:     .layout { grid-template-columns: 1fr; }
129:     .toc { display: none; }
130:   }
131:   @media print {
132:     header { position: static; }
133:     .toolbar, .toc { display: none; }
134:     section.block { break-inside: avoid; border: 1px solid #999; }
135:     body { background: white; color: black; }
136:     .layout { grid-template-columns: 1fr; }
137:   }
138: </style>
139: </head>
140: <body>
141: <header>
142:   <div class="header-top">
143:     <div class="header-text">
144:       <h1><span class="accent">AgentKit</span> ExpandIQ Take-Home Assignment</h1>
145:       <div class="sub">For candidates interviewing for the AI and Software Engineer role. Build a minimal agent-runtime service with tool calling, safety guards and persistence, plus a small frontend to drive it.</div>
146:     </div>
147:     <div class="logo-wrap">
148:       <img src="assets/expandiq-logo.png" alt="ExpandIQ" class="logo"
149:         onerror="this.onerror=null;this.src=&quot;data:image/svg+xml;utf8,&lt;svg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 220 56%27&gt;&lt;defs&gt;&lt;linearGradient id=%27g%27 x1=%270%27 y1=%270%27 x2=%271%27 y2=%270%27&gt;&lt;stop offset=%270%27 stop-color=%27%233a3aff%27/&gt;&lt;stop offset=%271%27 stop-color=%27%23b94bff%27/&gt;&lt;/linearGradient&gt;&lt;/defs&gt;&lt;text x=%2710%27 y=%2740%27 font-family=%27Arial,sans-serif%27 font-size=%2732%27 font-weight=%27700%27 fill=%27url(%23g)%27&gt;ExpandIQ&lt;/text&gt;&lt;/svg&gt;&quot;;" />
150:     </div>
151:   </div>
152:   <div class="meta-bar">
153:     <span class="pill"><strong>Backend:</strong> Python 3.12 or TypeScript</span>
154:     <span class="pill"><strong>Frontend:</strong> Vite + React + TypeScript</span>
155:     <span class="pill"><strong>Deliverable:</strong> Git repo, README and a walkthrough</span>
156:     <span class="pill"><strong>AI-assist:</strong> Allowed, with prompt history submitted</span>
157:   </div>
158:   <div class="toolbar">
159:     <button id="toggle-theme">Toggle theme</button>
160:     <button id="reset-progress">Reset checklist</button>
161:     <button id="print-btn">Print</button>
162:     <span class="progress" id="progress-label">0 / 0 items checked</span>
163:   </div>
164: </header>
165: 
166: <div class="layout">
167: <main>
168:   <section class="block" id="context" data-title="Context">
169:     <h2><span class="idx">01</span> Context</h2>
170:     <p>ExpandIQ is building an AI platform where agents call hundreds of tools to send email, query data and generate documents. We would like you to build a small, production-shaped slice of that runtime so we can talk about your design choices afterwards.</p>
171:     <p>Your task is to build <strong>AgentKit</strong>, a minimal agent-runtime service that executes a single tool-calling run against a <em>mock</em> LLM. The service should include safety guards, structured tool-error handling and per-step persistence.</p>
172:     <div class="callout">
173:       <p>You do not need any real LLM keys or external APIs for this exercise. The mock LLM is part of the assignment, and we want the run to be deterministic so we can replay it. We would rather see a thoughtful, smaller scope completed end to end than an ambitious scope left unfinished.</p>
174:     </div>
175:   </section>
176: 
177:   <section class="block" id="evaluating" data-title="What we evaluate">
178:     <h2><span class="idx">02</span> What we are evaluating</h2>
179:     <p>We are looking at design judgement, code quality, your pragmatism around LLM and agent systems, and how you communicate decisions. We are not counting lines of code.</p>
180:     <table>
181:       <thead><tr><th>Axis</th><th>What we look for</th></tr></thead>
182:       <tbody>
183:         <tr>
184:           <td><strong>Correctness</strong></td>
185:           <td>The core scope works end to end, the safety guards actually fire when they should, and errors are handled distinctly from successful results.</td>
186:         </tr>
187:         <tr>
188:           <td><strong>Design judgement</strong></td>
189:           <td>You can explain where you drew the boundaries between modules, why you chose SQLite over Postgres (or the reverse) and why your tool-retrieval approach makes sense. The README should walk a reader through these trade-offs clearly.</td>
190:         </tr>
191:         <tr>
192:           <td><strong>Code quality</strong></td>
193:           <td>The code is readable, properly typed (using pyright, mypy or strict TypeScript), free of accidental complexity and consistent in style. We will run <code>ruff</code> or <code>tsc --noEmit</code> against your repo and we expect a clean run.</td>
194:         </tr>
195:         <tr>
196:           <td><strong>Testing</strong></td>
197:           <td>Your tests target what is genuinely at risk. The loop guards and error paths are covered, and at least one integration test demonstrates that the whole thing works together.</td>
198:         </tr>
199:         <tr>
200:           <td><strong>Pragmatism</strong></td>
201:           <td>We want to see that you knew when the core was working and stopped there, rather than spending your remaining time building abstractions that the spec did not call for. Knowing when something is done is part of the skill.</td>
202:         </tr>
203:         <tr>
204:           <td><strong>Communication</strong></td>
205:           <td>Your README is honest about what is finished, what was deliberately skipped and what is still rough. Your commit history is something a reviewer can follow.</td>
206:         </tr>
207:         <tr>
208:           <td><strong>UI / UX craft</strong></td>
209:           <td>Your frontend reads at a glance, handles loading, empty and error states without jank, treats run state visibly (running, succeeded, stuck, capped, errored) and feels considered rather than thrown together. Keyboard accessibility and contrast are not afterthoughts.</td>
210:         </tr>
211:       </tbody>
212:     </table>
213:     <div class="callout ok">
214:       <p><strong>What impresses us</strong></p>
215:       <ul>
216:         <li>A README that includes an honest "Known gaps" section. We would much rather hear about a bug from you than discover it ourselves.</li>
217:         <li>A commit where you wrote a test, watched it fail, and then fixed the underlying bug. That story shows up clearly in the history when it happens.</li>
218:         <li>A short paragraph in the README that captures one sharp observation about the problem itself, rather than just restating the spec.</li>
219:         <li>Structured logging that a reviewer (or a future on-call engineer) would actually find useful.</li>
220:       </ul>
221:     </div>
222:     <div class="callout hard">
223:       <p><strong>What concerns us</strong></p>
224:       <ul>
225:         <li>We are wary of abstractions that exist only for imagined future requirements that the spec does not describe.</li>
226:         <li>We will flag any code path that swallows errors silently instead of surfacing them.</li>
227:         <li>We do not value tests that lock down implementation details rather than describing the behaviour we care about.</li>
228:         <li>We are sceptical when someone says they ran out of time but the repo also contains a custom dependency-injection framework or similar yak-shave.</li>
229:         <li>We do not want a submission that calls itself "production-ready". This is a small exercise, and being honest about what would still need to happen before shipping is more useful than the claim.</li>
230:       </ul>
231:     </div>
232:   </section>
233: 
234:   <section class="block" id="core" data-title="Core scope">
235:     <h2><span class="idx">03</span> Core scope (required)</h2>
236: 
237:     <h3>API surface</h3>
238:     <pre><code>POST  /runs             -&gt; create a run, return { run_id }
239: GET   /runs             -&gt; list recent runs (paginated, newest first)
240: GET   /runs/{run_id}    -&gt; return run state and steps
241: POST  /runs/{run_id}/resume   (optional)</code></pre>
242: 
243:     <p>The request body for <code>POST /runs</code> looks like this:</p>
244:     <pre><code>{
245:   "goal": "Free-text goal the agent should pursue",
246:   "max_steps": 20,
247:   "max_cost_usd": 0.50
248: }</code></pre>
249: 
250:     <h3>Agent loop</h3>
251:     <ol>
252:       <li>Load the full tool registry, which should contain around ten tools that you define.</li>
253:       <li>Run a tool-retrieval step to pick the top-K most relevant tools (something like five) for the goal before calling the LLM. A keyword match, a BM25 implementation or a simple embedding-based approach are all fine. The point is that you can articulate why we should not be dumping thirty tools into every LLM call.</li>
254:       <li>Call the mock LLM with <code>{ goal, past_steps, candidate_tools }</code>. It should return either a tool call or a final answer.</li>
255:       <li>If the LLM returns a tool call, dispatch it through a tool runtime that enforces the error contract below, persist the step and continue the loop.</li>
256:       <li>If the LLM returns a final answer, persist it and mark the run as <code>succeeded</code>.</li>
257:     </ol>
258: 
259:     <h3>Safety guards</h3>
260:     <p>The runtime needs to enforce four guards, each of which should terminate the run with a clear reason.</p>
261:     <ul>
262:       <li>The <strong>step cap</strong> uses <code>max_steps</code> from the request, defaulting to twenty.</li>
263:       <li>The <strong>cost cap</strong> sums the (mock) token cost reported by each step and stops the run once it crosses <code>max_cost_usd</code>.</li>
264:       <li>The <strong>stuck detector</strong> watches for the same <code>(tool_name, args_hash)</code> repeating three times and terminates the run with reason <code>stuck</code>.</li>
265:       <li>The <strong>wall-clock guard</strong> enforces a sixty-second hard ceiling on a single run.</li>
266:     </ul>
267:     <p>A terminated run must record a clear reason chosen from <code>step_cap</code>, <code>cost_cap</code>, <code>stuck</code>, <code>timeout</code>, <code>error</code> or <code>succeeded</code>.</p>
268: 
269:     <h3>Tool error contract</h3>
270:     <p>Tools should return a structured result rather than raising raw exceptions back into the loop:</p>
271:     <pre><code>{
272:   "ok": bool,
273:   "data": ... | None,
274:   "error": { "code": str, "message": str, "recoverable": bool } | None
275: }</code></pre>
276:     <p>The runtime should decide whether to retry transparently when the error is transient or surface the error to the model when it is semantic (for example, an invalid argument). Retries should be bounded.</p>
277: 
278:     <h3>Persistence</h3>
279:     <p>Each step should persist to SQLite, or to Postgres if you prefer running it under Docker locally. Two tables cover the requirement:</p>
280:     <ul>
281:       <li>The <code>runs</code> table stores <code>id</code>, <code>goal</code>, <code>status</code>, <code>reason</code>, <code>total_cost</code>, <code>started_at</code> and <code>finished_at</code>.</li>
282:       <li>The <code>steps</code> table stores <code>run_id</code>, <code>step_number</code>, <code>tool_name</code>, <code>args_json</code>, <code>result_json</code>, <code>cost</code> and <code>created_at</code>.</li>
283:     </ul>
284:     <p>Once a run finishes, it must be readable through <code>GET /runs/{run_id}</code>.</p>
285: 
286:     <h3>Testing</h3>
287:     <ul>
288:       <li>Unit tests should cover the tool-retrieval ranking, stuck detection, the cost and step caps and the retry-classification logic.</li>
289:       <li>At least one integration test should drive a full run end to end against the mock LLM and assert on the resulting database state.</li>
290:     </ul>
291:     <p>Full coverage is not what we are after. We want to see that you can pick the small number of tests that actually reduce risk in this design.</p>
292: 
293:     <h3>Mock LLM and tool registry</h3>
294:     <p>The mock LLM should be a deterministic function. Any keyword-based dispatch driven by the <code>goal</code> string and the length of <code>past_steps</code> is fine:</p>
295:     <pre><code>def mock_llm(goal: str, past_steps: list, candidate_tools: list) -&gt; dict:
296:     # Return either:
297:     #   {"type": "tool_call", "tool": "search_docs", "args": {"q": "..."}, "cost": 0.002}
298:     #   {"type": "final", "content": "...", "cost": 0.001}
299:     ...</code></pre>
300:     <p>The mock should be rich enough to exercise every part of the loop. We expect to see goals that drive two to five tool calls before finalising, at least one goal that intentionally repeats the same tool so the stuck detector fires, at least one goal that pushes the cumulative cost past the cap, and at least one tool call that returns a recoverable error on the first attempt and succeeds on retry.</p>
301:     <p>Here is a starter list of tools, which you are welcome to adapt.</p>
302:     <table>
303:       <thead><tr><th>Tool</th><th>Description</th></tr></thead>
304:       <tbody>
305:         <tr><td><code>search_docs</code></td><td>Search internal docs by keyword.</td></tr>
306:         <tr><td><code>fetch_doc</code></td><td>Fetch a full doc by id.</td></tr>
307:         <tr><td><code>send_email</code></td><td>Send an email. Non-idempotent and requires an idempotency key.</td></tr>
308:         <tr><td><code>create_calendar_event</code></td><td>Schedule an event.</td></tr>
309:         <tr><td><code>query_sql</code></td><td>Run a SELECT against a mock database.</td></tr>
310:         <tr><td><code>summarise_text</code></td><td>Summarise a passage of text.</td></tr>
311:         <tr><td><code>translate</code></td><td>Translate text between languages.</td></tr>
312:         <tr><td><code>fetch_weather</code></td><td>Get the weather for a city.</td></tr>
313:         <tr><td><code>lookup_contact</code></td><td>Find a contact by name.</td></tr>
314:         <tr><td><code>web_search</code></td><td>Search the web.</td></tr>
315:       </tbody>
316:     </table>
317:     <p>The tool bodies themselves can be stubbed with canned data keyed on the input, and you should annotate each tool with <code>parallel_safe</code> and <code>idempotent</code> flags.</p>
318: 
319:     <h3>README contents</h3>
320:     <p>The README at the root of the repo should cover the following.</p>
321:     <ol>
322:       <li>Instructions for running the service. You can use <code>uv</code>, <code>pip</code>, <code>poetry</code> or <code>npm</code>, whichever lets you move fastest. Include the commands a reviewer needs to run the server and the test suite.</li>
323:       <li>A short section on your design decisions, including what you built the way you did, what you deliberately skipped and what you would do next.</li>
324:       <li>A "Known gaps" section that lists any rough edges or partial implementations.</li>
325:       <li>An "AI-assist log" section as described under section 08 if you used a coding agent.</li>
326:     </ol>
327:   </section>
328: 
329:   <section class="block" id="frontend" data-title="Frontend">
330:     <h2><span class="idx">04</span> Frontend (required)</h2>
331:     <p>We would like you to build a small single-page application that drives your AgentKit service. The point is not to ship a polished product, but to give us a window into how you think about visual hierarchy, state, accessibility and the kind of small details that make a tool feel trustworthy.</p>
332: 
333:     <h3>Stack</h3>
334:     <p>Vite with React and TypeScript is what we use in production for our web app, so it is our preferred choice and we will be most fluent reviewing it. Vue, Svelte or SolidJS on Vite are also welcome if you are quicker in those.</p>
335:     <p>You may use a component library if you wish (shadcn/ui, Radix, Mantine, Chakra, MUI). If you do, please use it cleanly rather than fighting it. Plain CSS, CSS Modules or Tailwind are equally fine.</p>
336: 
337:     <h3>Scope (keep it small)</h3>
338:     <p>One main screen, chat-style, plus a simple list of past runs. Think of it as the experience a non-technical user would have, not a debug console. Aim for around an hour of frontend work. We are not asking for a polished product, only that the screens feel considered and the user can actually use them.</p>
339: 
340:     <h3>What the UI needs to do</h3>
341:     <ol>
342:       <li><strong>Ask for a goal in plain language.</strong> A single text input is enough. The technical knobs (<code>max_steps</code>, <code>max_cost_usd</code>) should not be in the user's face. Either hide them behind a small "Advanced" toggle or just send sensible defaults from the frontend and skip the UI entirely.</li>
343:       <li><strong>Show the agent's progress in plain language while it runs.</strong> As steps come in, render a friendly line per step (for example, "Searching documents for 'Q3 report'" rather than <code>tool_call: search_docs {"q":"Q3 report"}</code>). Power users can still expand a step to see the raw arguments and result if they want to, but that should not be the default view.</li>
344:       <li><strong>Show the final answer prominently.</strong> When the run finishes successfully, the agent's final response should be the most visible thing on the screen, not buried at the end of the timeline.</li>
345:       <li><strong>Translate terminal reasons into something a person can act on.</strong> A run that ended with <code>cost_cap</code> should read as something like "Reached the $0.50 budget for this run." A <code>stuck</code> run should explain that the agent kept repeating itself. The raw code can still appear as a small label, but the message is what the user sees first.</li>
346:       <li><strong>List past runs.</strong> A sidebar or simple list showing each run's goal, an outcome glyph (success, capped, stuck, errored) and a relative timestamp. Clicking a row reopens that run.</li>
347:       <li><strong>Live updates while a run is in flight.</strong> Polling <code>GET /runs/{id}</code> every one to two seconds is fine. If you did the streaming stretch on the backend, wire the SSE or WebSocket feed in instead.</li>
348:     </ol>
349: 
350:     <h3>What we look for in the UI</h3>
351:     <ul>
352:       <li>The screen reads at a glance. The goal, the current activity and the final answer are the loudest things.</li>
353:       <li>Outcome states (running, succeeded, capped, stuck, errored) are visually distinct, not just words inside a sentence.</li>
354:       <li>Loading, empty and error states are all handled. A failed API call should not leave a spinner running forever.</li>
355:       <li>Accessibility basics. Semantic HTML, keyboard navigability, focus rings preserved, decent contrast.</li>
356:       <li>Typography, spacing and colour feel consistent. Off-the-shelf component libraries are fine if you use them cleanly.</li>
357:     </ul>
358: 
359:     <h3>What is not in scope for the frontend</h3>
360:     <ul>
361:       <li>Custom design systems built from scratch. Off-the-shelf or plain CSS is preferred here.</li>
362:       <li>Cancel, retry, edit-and-rerun, run filtering or any feature beyond the list above.</li>
363:       <li>A separate launcher screen, routing, history pages or any architecture that adds frontend complexity for its own sake.</li>
364:       <li>Mobile responsiveness, internationalisation, multi-theme support or login flows.</li>
365:       <li>Production build pipelines. Running it via <code>npm run dev</code> against your local backend is enough.</li>
366:     </ul>
367: 
368:     <h3>Wiring</h3>
369:     <p>Keep the frontend in the same repository, in its own folder (something like <code>frontend/</code> or <code>web/</code>). Talk to the backend either through a Vite dev-server proxy or by enabling a simple CORS allowlist on the backend. The README should say which approach you chose and the commands to bring backend and frontend up together.</p>
370:   </section>
371: 
372:   <section class="block" id="stack" data-title="Stack">
373:     <h2><span class="idx">05</span> Stack</h2>
374:     <p>For context, our production stack runs Python microservices on FastAPI for the AI and agent workloads, a TypeScript monolith on Azure Functions for the API surface, and Azure PostgreSQL underneath.</p>
375:     <p>For this exercise we would prefer <strong>Python 3.12 with FastAPI, async SQLAlchemy and pytest</strong>, since that lines up directly with how we run our agent and document-parser services in production.</p>
376:     <p>If you would rather work in TypeScript, that is fine too. A plain Node service on Express, Fastify or Hono with SQLite or Postgres and vitest or jest will work nicely. We do not expect you to spin up an Azure Functions project locally just to mirror the monolith for a take-home.</p>
377:     <p>The choice should come down to whichever stack lets you move fastest while still showing us your judgement.</p>
378:   </section>
379: 
380:   <section class="block" id="stretch" data-title="Stretch goals">
381:     <h2><span class="idx">06</span> Stretch (optional)</h2>
382:     <div class="callout warn">
383:       <p>You should only touch a stretch goal once the core scope is solid. The list below is roughly ordered by how much signal each option gives us.</p>
384:     </div>
385:     <ol>
386:       <li>Support for parallel tool calls, where the mock LLM occasionally returns several tool calls in one turn and the runtime executes the parallel-safe ones concurrently while serialising the unsafe ones.</li>
387:       <li>An idempotency layer where <code>POST /runs</code> accepts an <code>Idempotency-Key</code> header and duplicate requests within the replay window return the original run.</li>
388:       <li>A streaming endpoint, either WebSocket or Server-Sent Events, that emits step events as they happen.</li>
389:       <li>A resume endpoint at <code>POST /runs/{run_id}/resume</code> that picks up a run that was interrupted partway through.</li>
390:       <li>Tool retrieval driven by embeddings rather than keyword matching, using either a local sentence-transformers model or a stub embedding function.</li>
391:     </ol>
392:     <p>If you do tackle a stretch goal, please write a short note in the README explaining why you chose that one.</p>
393:   </section>
394: 
395:   <section class="block" id="not-scope" data-title="Not in scope">
396:     <h2><span class="idx">07</span> Explicitly not in scope</h2>
397:     <p>Please do not spend effort on the following areas.</p>
398:     <ul>
399:       <li>Real LLM integration with OpenAI or Anthropic. We want you to use the mock so that runs stay deterministic.</li>
400:       <li>Authentication or user management. Treat the service as single-tenant with no login.</li>
401:       <li>Docker, Kubernetes or any deployment pipeline.</li>
402:       <li>Exhaustive test coverage. We would rather see a small set of well-chosen tests than a sprawling suite.</li>
403:       <li>Heavy observability tooling. A clear log line per step is plenty for this exercise.</li>
404:     </ul>
405:   </section>
406: 
407:   <section class="block" id="ai-assist" data-title="AI-assist policy">
408:     <h2><span class="idx">08</span> Using AI coding agents</h2>
409:     <div class="callout ok">
410:       <p>You can reasonably use coding agents such as Claude Code, Cursor, Copilot, Codex or Aider on this exercise. We use them ourselves, and using them well is part of the skill we are hiring for. The conditions below are how we make sure the submission still tells us about your judgement and not the agent's defaults.</p>
411:     </div>
412:     <p>If you use an agent, please do the following.</p>
413:     <ul>
414:       <li>Submit your prompt history. A dump of the conversation, an export of the chat or the Cursor composer, screenshots, JSON or a markdown paste are all fine. We want to see what you asked and how you steered the agent through the task.</li>
415:       <li>Submit your setup. Tell us which tools and which model you used, and include any custom system prompt, rules file (such as <code>CLAUDE.md</code> or <code>.cursorrules</code>), MCP servers or hooks. If those configs live in the repo, even better.</li>
416:       <li>Take ownership of the output. You are responsible for every line that ends up committed. If the agent introduced a bug, you shipped that bug, so please review before committing.</li>
417:       <li>Be honest about the split between you and the agent. In your AI-assist log, give us a rough breakdown of what the agent wrote, what you wrote yourself and what you rewrote after the agent drafted it.</li>
418:     </ul>
419:     <p>When we read your prompts, the things that catch our eye are these.</p>
420:     <ul>
421:       <li>How you framed the task. We notice the difference between someone who pasted the entire spec and asked for "the solution" and someone who broke it into reviewable chunks.</li>
422:       <li>How you steered after the first output. We notice when a candidate caught a bad pattern, pushed back on the agent and got a better result.</li>
423:       <li>How you tested what the agent produced, or whether you tested it at all.</li>
424:       <li>Whether you used the agent for the parts that genuinely benefit from it (boilerplate, schema drafting, test scaffolding) or whether you let it make architectural decisions on your behalf.</li>
425:     </ul>
426:     <div class="callout warn">
427:       <p>What we are not hoping to see is a single mega-prompt of the form "build AgentKit per this spec". We would much rather read a series of smaller, iterative prompts where you clearly drove the design and the agent helped you execute on it.</p>
428:     </div>
429:     <p>Not using an agent at all is a perfectly valid choice. Please just say so in the README. We do not score by tool use either way.</p>
430:   </section>
431: 
432:   <section class="block" id="deliverables" data-title="Deliverables">
433:     <h2><span class="idx">09</span> Deliverables</h2>
434:     <p>When you are ready to share your work, please send through the following.</p>
435:     <ol>
436:       <li>A Git repository, either as a public GitHub link or as a zip archive. We do read commit history, so a tidy series of commits is welcome.</li>
437:       <li>A README at the root of the repo covering the sections described under section 03.</li>
438:       <li>All your code and tests inside the repo. If something is not runnable from the documented commands, we have to assume it does not exist.</li>
439:       <li>A <code>prompts/</code> directory or README section containing the AI-assist log and any relevant agent configuration, if you used a coding agent.</li>
440:     </ol>
441: 
442:     <h3>Presenting your work</h3>
443:     <p>We would also like you to walk us through the working code rather than just sending the repo and waiting for feedback. We will set up a follow-up meeting with the ExpandIQ team (Jonas and Manny) where you share your screen, run the integration test live, walk us through one or two interesting design decisions and answer questions as we go.</p>
444:     <p>The conversation matters as much to us as the code. We want to hear how you reasoned about the design, where you would have invested more effort, and which parts you are not yet happy with.</p>
445: 
446:     <h3>Self-check before submitting</h3>
447:     <ul class="checklist" id="submit-checklist">
448:       <li><input type="checkbox" id="c1"/><label for="c1"><code>POST /runs</code> creates a run and returns a <code>run_id</code>.</label></li>
449:       <li><input type="checkbox" id="c2"/><label for="c2"><code>GET /runs/{id}</code> returns the run state along with all of its steps.</label></li>
450:       <li><input type="checkbox" id="c3"/><label for="c3">Tool retrieval narrows the candidate set before each LLM call.</label></li>
451:       <li><input type="checkbox" id="c4"/><label for="c4">The step cap terminates the run correctly and records its reason.</label></li>
452:       <li><input type="checkbox" id="c5"/><label for="c5">The cost cap terminates the run correctly.</label></li>
453:       <li><input type="checkbox" id="c6"/><label for="c6">Stuck detection fires when the same tool call repeats three times.</label></li>
454:       <li><input type="checkbox" id="c7"/><label for="c7">The wall-clock guard triggers at the sixty-second ceiling.</label></li>
455:       <li><input type="checkbox" id="c8"/><label for="c8">The tool error contract is implemented and the runtime retries on recoverable errors.</label></li>
456:       <li><input type="checkbox" id="c9"/><label for="c9">Unit tests cover the guards, the retrieval logic and the retry classifier.</label></li>
457:       <li><input type="checkbox" id="c10"/><label for="c10">An integration test drives a full run end to end.</label></li>
458:       <li><input type="checkbox" id="c11"/><label for="c11">The type checker (<code>mypy</code>, <code>pyright</code> or <code>tsc --noEmit</code>) passes cleanly.</label></li>
459:       <li><input type="checkbox" id="c12"/><label for="c12">The linter (<code>ruff</code> or <code>eslint</code>) passes cleanly.</label></li>
460:       <li><input type="checkbox" id="c13"/><label for="c13">The README covers run commands, design decisions and known gaps.</label></li>
461:       <li><input type="checkbox" id="c14"/><label for="c14">The AI-assist log and any agent configs are included, or you have noted that you did not use an agent.</label></li>
462:       <li><input type="checkbox" id="c15"/><label for="c15">The repo clones and runs cleanly on a fresh machine.</label></li>
463:       <li><input type="checkbox" id="c16"/><label for="c16">The user can enter a goal in plain language and start a run without seeing raw config knobs.</label></li>
464:       <li><input type="checkbox" id="c17"/><label for="c17">Step activity renders in friendly language as the run progresses.</label></li>
465:       <li><input type="checkbox" id="c18"/><label for="c18">The final answer is the loudest thing on the screen when a run succeeds.</label></li>
466:       <li><input type="checkbox" id="c19"/><label for="c19">Terminal reasons (capped, stuck, errored) are translated into a human message, not just shown as raw codes.</label></li>
467:       <li><input type="checkbox" id="c20"/><label for="c20">Past runs list with goal, outcome and time. Clicking a row reopens that run.</label></li>
468:       <li><input type="checkbox" id="c21"/><label for="c21">Loading, empty and error states are handled. No infinite spinners.</label></li>
469:       <li><input type="checkbox" id="c22"/><label for="c22">Keyboard navigation, focus rings and contrast are not broken.</label></li>
470:       <li><input type="checkbox" id="c23"/><label for="c23">README explains how to run backend and frontend together.</label></li>
471:       <li><input type="checkbox" id="c24"/><label for="c24">You have decided how you want to walk us through the working code.</label></li>
472:     </ul>
473:   </section>
474: 
475:   <section class="block" id="notes" data-title="Practical notes">
476:     <h2><span class="idx">10</span> Practical notes</h2>
477:     <ul>
478:       <li>If something in the spec is ambiguous, make a reasonable call and document it in the README under "Interpretation". A defensible decision is always fine, and we are interested in how you reason under ambiguity.</li>
479:       <li>If you have questions before you start, please reply to the email that sent you this brief.</li>
480:     </ul>
481:     <div class="callout">
482:       <p>Good luck. We are looking forward to reading the repo and chatting through it with you.</p>
483:     </div>
484:   </section>
485: </main>
486: <nav class="toc" id="toc"></nav>
487: </div>
488: 
489: <footer>ExpandIQ AgentKit Take-Home. Checklist persists in localStorage.</footer>
490: 
491: <script>
492: const toc = document.getElementById("toc");
493: document.querySelectorAll("section.block").forEach(s => {
494:   const a = document.createElement("a");
495:   a.href = `#${s.id}`;
496:   a.textContent = s.dataset.title;
497:   toc.appendChild(a);
498: });
499: const links = toc.querySelectorAll("a");
500: window.addEventListener("scroll", () => {
501:   let active = null;
502:   document.querySelectorAll("section.block").forEach(s => {
503:     const r = s.getBoundingClientRect();
504:     if (r.top < 200) active = s.id;
505:   });
506:   links.forEach(l => l.classList.toggle("active", l.getAttribute("href") === `#${active}`));
507: });
508: 
509: document.getElementById("toggle-theme").addEventListener("click", () => {
510:   const cur = document.documentElement.getAttribute("data-theme");
511:   document.documentElement.setAttribute("data-theme", cur === "light" ? "" : "light");
512:   localStorage.setItem("expandiq-takehome-theme", cur === "light" ? "" : "light");
513: });
514: const savedTheme = localStorage.getItem("expandiq-takehome-theme");
515: if (savedTheme) document.documentElement.setAttribute("data-theme", savedTheme);
516: 
517: const STORAGE_KEY = "expandiq-takehome-checks";
518: const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
519: const boxes = document.querySelectorAll("#submit-checklist input[type=checkbox]");
520: function updateLabel() {
521:   const checked = [...boxes].filter(b => b.checked).length;
522:   document.getElementById("progress-label").textContent = `${checked} / ${boxes.length} items checked`;
523: }
524: boxes.forEach(b => {
525:   if (saved[b.id]) { b.checked = true; b.closest("li").classList.add("done"); }
526:   b.addEventListener("change", () => {
527:     saved[b.id] = b.checked;
528:     localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
529:     b.closest("li").classList.toggle("done", b.checked);
530:     updateLabel();
531:   });
532: });
533: updateLabel();
534: document.getElementById("reset-progress").addEventListener("click", () => {
535:   localStorage.removeItem(STORAGE_KEY);
536:   boxes.forEach(b => { b.checked = false; b.closest("li").classList.remove("done"); });
537:   updateLabel();
538: });
539: 
540: document.getElementById("print-btn").addEventListener("click", () => window.print());
541: </script>
542: </body>
543: </html>

(End of file - total 543 lines)
</content>

---

## Assistant (2)

## Extension Hooks

**Automatic Pre-Hook**: git
Executing: `/speckit.git.feature`
EXECUTE_COMMAND: speckit.git.feature

Wait for the result of the hook command before proceeding to the Outline.

---

## User (3)

<!-- Extension: git -->
<!-- Config: .specify/extensions/git/ -->
# Create Feature Branch

Create and switch to a new git feature branch for the given specification. This command handles **branch creation only** — the spec directory and files are created by the core `/speckit.specify` workflow.

## User Input

```text

```

You **MUST** consider the user input before proceeding (if not empty).

## Environment Variable Override

If the user explicitly provided `GIT_BRANCH_NAME` (e.g., via environment variable, argument, or in their request), pass it through to the script by setting the `GIT_BRANCH_NAME` environment variable before invoking the script. When `GIT_BRANCH_NAME` is set:
- The script uses the exact value as the branch name, bypassing all prefix/suffix generation
- `--short-name`, `--number`, and `--timestamp` flags are ignored
- `FEATURE_NUM` is extracted from the name if it starts with a numeric prefix, otherwise set to the full branch name

## Prerequisites

- Verify Git is available by running `git rev-parse --is-inside-work-tree 2>/dev/null`
- If Git is not available, warn the user and skip branch creation

## Branch Numbering Mode

Determine the branch numbering strategy by checking configuration in this order:

1. Check `.specify/extensions/git/git-config.yml` for `branch_numbering` value
2. Check `.specify/init-options.json` for `branch_numbering` value (backward compatibility)
3. Default to `sequential` if neither exists

## Execution

Generate a concise short name (2-4 words) for the branch:
- Analyze the feature description and extract the most meaningful keywords
- Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
- Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)

Run the appropriate script based on your platform:

- **Bash**: `.specify/extensions/git/scripts/bash/create-new-feature.sh --json --short-name "<short-name>" "<feature description>"`
- **Bash (timestamp)**: `.specify/extensions/git/scripts/bash/create-new-feature.sh --json --timestamp --short-name "<short-name>" "<feature description>"`
- **PowerShell**: `.specify/extensions/git/scripts/powershell/create-new-feature.ps1 -Json -ShortName "<short-name>" "<feature description>"`
- **PowerShell (timestamp)**: `.specify/extensions/git/scripts/powershell/create-new-feature.ps1 -Json -Timestamp -ShortName "<short-name>" "<feature description>"`

**IMPORTANT**:
- Do NOT pass `--number` — the script determines the correct next number automatically
- Always include the JSON flag (`--json` for Bash, `-Json` for PowerShell) so the output can be parsed reliably
- You must only ever run this script once per feature
- The JSON output will contain `BRANCH_NAME` and `FEATURE_NUM`

## Graceful Degradation

If Git is not installed or the current directory is not a Git repository:
- Branch creation is skipped with a warning: `[specify] Warning: Git repository not detected; skipped branch creation`
- The script still outputs `BRANCH_NAME` and `FEATURE_NUM` so the caller can reference them

## Output

The script outputs JSON with:
- `BRANCH_NAME`: The branch name (e.g., `003-user-auth` or `20260319-143022-user-auth`)
- `FEATURE_NUM`: The numeric or timestamp prefix used

---

## Assistant (4)

Now I'll write the specification and the feature.json.

---

## Assistant (5)

Now I'll create the quality checklist and validate the spec against it.

---

## Assistant (6)

Now let me validate the spec against the checklist. I'll review each item:

**Validation Results:**

| Item | Status | Issues |
|------|--------|--------|
| No implementation details | FAIL | Assumptions mention "TypeScript with Bun, bun:sqlite" - implementation details |
| Focused on user value | PASS | |
| Written for non-technical stakeholders | FAIL | API endpoint syntax (`POST /runs`) is technical; success criteria mention "mock LLM", "database" |
| All mandatory sections completed | PASS | |
| No NEEDS CLARIFICATION markers | PASS | None present |
| Requirements testable and unambiguous | PASS | |
| Success criteria measurable | PASS | |
| Success criteria technology-agnostic | FAIL | SC-006 mentions "mock LLM", SC-007 mentions "database" |
| Acceptance scenarios defined | PASS | |
| Edge cases identified | PASS | |
| Scope clearly bounded | FAIL | No explicit out-of-scope section |
| Dependencies and assumptions identified | PASS | |
| FR acceptance criteria clear | PASS | |
| User scenarios cover primary flows | PASS | |
| Measurable outcomes | PASS | |
| No implementation details leak | FAIL | Same as first item |

Let me fix the issues:

---

## Assistant (7)

Now let me clean up the technical language in user stories and requirements:

---

## Assistant (8)

All items pass now. Let me update the checklist:

---

## Assistant (9)

## Extension Hooks

**Optional Hook**: git
Command: `/speckit.git.commit`
Description: Auto-commit after specification

Prompt: Commit specification changes?
To execute: `/speckit.git.commit`

---

**Optional Hook**: agent-context
Command: `/speckit.agent-context.update`
Description: Refresh agent context after specification

Prompt: Execute speckit.agent-context.update?
To execute: `/speckit.agent-context.update`

---

## Completion Report

- **SPECIFY_FEATURE_DIRECTORY**: `specs/001-agent-loop`
- **SPEC_FILE**: `specs/001-agent-loop/spec.md`
- **Checklist**: All 16 items passed ✅
- **NEEDS CLARIFICATION**: None — all decisions made with informed guesses documented in Assumptions
- **Next phase**: Ready for `/speckit.clarify` or `/speckit.plan`

---

