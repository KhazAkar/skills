<---
This is a high level sketch, nothing TOO precise. Each contract is one skill, made one by one.
--->

# LodeStack

Cognitive + execution partner for work

## Description

This is a collection of skills useful for software engineering for solo developers. Made from 4 contracts:

1. Memory
2. Edit
3. Standards
4. AGENTS.md

Each contract is made in following way:

- SKILL.md - contract core
- Reference.md - holds important context and interpretations, as well as mapping between OSMM and LodeStack, as well as mapping of [AMDD](http://agilemodeling.com/essays/amdd.htm\](http://agilemodeling.com/essays/amdd.htm) to LodeStack, with one distinction - models are permanent, iterated through the development cycle of ADR implementation.

If more than one reference is needed, put them in `refs/` directory

Edit contract also gains `tse-recipes.md`, which contains common usage examples for tree-sitter-edit tool, copied from tree-sitter-edit tool, including a simple header containing `tree-sitter-edit: <tree-sitter-edit_SHA>`

**Everything is kept minimal and unambiguous**

Standards contract is split between:

1. Code
2. Test

Overall system shall follow OpenSource Maturity Model (`Petrinja, Nambakam, Sillitti, "Introducing the OpenSource Maturity Model" (ICSE 2009 workshop)`) and should be modelled to fulfil at least Basic level, assessed continuously. 

Development follows AMDD. Following map applies:

- Diagram/Architecture: ADR
- Test: Written test, derived directly from ADR
- Code: Code satisfying Architecture

Code is the representation of design described through ADRs and tests, living as end to end contract. 

ADR - Test - Code makes one development cycle.
From implementation point of view code is the source of truth. 
ADR+Test+Code is the system/integration-level package source of truth.
With addition of Plan - its feature-level source of truth.

When it comes to code manipulation, reasoning and decisions - short-cuts are FORBIDDEN

Research before solutions is mandatory.
STE-100 Simplified English language specification utilized. For other languages - keep STE-100 in spirit.
Be concise and precise - don't perform an info-dump on developer

## Lode-stone

Optional add-on/transformation of Memory contract

Transforms Memory contract of LodeStack into multi-user collective common knowledge repository for one team. It transforms Lode into shared knowledge hub, which holds shared knowledge, as well as project specific one.

In each project repository, which utilizes lode-stone, 1 marker should live inside project repository AGENTS.md:

`Lode-stone transformed this project memory and now it lives here: <link_to_repository>, linked as submodule named 'lode' with project memory entry point living here: lode/projects/<name>/lode-map.md. For shared knowledge entry point, use lode/stone-map.md.`

Which means: lode gains per-project structures + hub-wide structure

`lode/tmp` becomes `tmp`

Sometimes it might be that system consists of several projects, then it should be done in depth - lode/systems/<name-of-system>/<project-name>.md & lode/systems/<name-of-system>/<project-name>-<module>.md

For system-level overview, check `lode/systems/<name-of-system>.md`

For shared/common knowledge elements -> `lode/shared/<topic>/` instead of `lode`. There should land things like common practices, quirks & gotchas etc.

Migration path:

- lode -> lode-project
- Add knowledge hub as sub-module at lode/
- Transfer lode-project content, except `lode/tmp`, to lode/projects/<project_name_taken_from_git>/, with `mkdir -p` beforehand
- Move `lode/tmp` contents to `tmp`
- Edit `.gitignore`, replacing `lode/tmp` to `tmp`
- Delete `lode-project` and `lode/tmp`
- Add specified line to AGENTS.md
- Self-Verify the changes in adversarial manner
- Propose the push with developer-made verification before accepting the action

## Memory

Memory system should have following characteristics and specs:

1. All diagrams and drawings in mermaid format
2. Consists of following elements:

- lode-map for ADR + Plan + Architecture links
- lode/tmp/ for temporary work, with folders per ADR/Plan
- lode/adr/ holding ADRs
- lode/plan/ holding plans and feature-sized backlog items
- lode/quirks-and-gotchas, collecting whole project findings, gotchas and quirks describing unexpected/live behaviour of system with optional extension of lode/quirks-and-gotchas/<system-component>.md for more complex systems
- lode/summary.md - holds project summary description. Should NEVER be a simple README.md - it's more technical than user-facing document
- lode/terminology.md - describes all the important names/verbs for understanding the documentation living within lode/ directory, with ELI5-like description for each
- lode/practices.md - describes project-specific actions, commands, necessary + optional opt-in tooling and workflows, divided into following categories:

a. Necessary and optional, opt-in tooling
b. First setup
c. Running
d. Testing

- lode/architecture/ - Describes project architecture as series of diagrams, on system level + each module gets its own sub-diagram as separate markdown file, on software level. Consists of:

a. system.md - Overall system diagram
b. <module>.md - Module-level software diagram

Template-less, specification made from aboce should be precise and strict enough to give similar designs.

### ADR

1. 6xW:

- What status of ADR (Proposed/Accepted/Superseded). Do not edit accepted ADR, with one exception - technology version bumped. Proposed ADR can be iterated model & description areas, but main topic stays.
- What to build (feature/fix)
- When (Now/Backlog)
- Whole description of feature, written as executable specification
- Which technologies should we pick? Presented technologies to pick by the developer with provided reasoning + researched by AI agent behind each selection.
- Which technologies should we drop? When technology was selected by developer after agent-made proposition list, rest, within same part, can be rejected. Developer is responsible for providing the reason of rejection of every other proposed technology. Even if agent writes down drop reason, developer owns the decision.

2. ADRs are diagram/model based - input for creating executable specification (test)
3. Each ADR entry should be written as specification, which, after applying logic verbatim, creates executable specification - test.
4. Each ADR should have linked relevant technology documentation in currently used version. When developer will ask for upgrades - edit ADR.
5. Superseding is the default way of handling changes in ADR.
6. ADR name format: `ADR-<date>-XXX.md`
7. Work steps are recorded in dedicated TASKLIST file, stored in `lode/adr/TASKLIST-ADR-<date>-XXX.md`

### Plan

1. Plan name format: PLAN-<date>-XXX.md
2. Feature backlogs carry following format: BL-<date>-XXX.md
3. Plan, when executing, can create one or several ADRs during work
4. Plans consist of:

- Phase to-do list, with attached one line serving as title
- High level description what should be built, for each phase
- High level model describing elements, connections and dependencies between phases

## Edit

Code editing cycle, performed with following steps:

- REASON
- LOCATE
- ANALYZE

a. ACCEPT
b. REJECT

- EDIT
- VERIFY (with following check-boxes)

a. LINT
b. TYPECHECK
c. SECURITY
d. FORMAT
e. TEST
f. LODE

Code editing cycle is the step by step protocol to follow.

Points a-d shall be done using specialized tools for currently used programming language.

SECURITY (c) - means the defensive strategies used in programming which enhance code security, as well as scanning using specialized tools

LODE (f) - verified against `lode/` itself

Editing of code primarily shall be done using AST, performed using `tree-sitter-edit` (https://gitlab.com/khazlabz/tree-sitter-edit) command, with text-diff based fallback.

Present to developer ANALYZE status as a table, with short reason for each element - first is agent

Outside of overall code editing cycle, smaller EDIT-VERIFY cycle is performed, when VERIFY stage doesn't pass.

Edits shall be done in cycles, in minimal viable manner to satisfy REASON and VERIFY steps.

When REASON and VERIFY cannot both be satisfied in more than 3 attempts, break the cycle and surface to the developer, in table form:

- Found problems
- Description of each problem
- Proposed solutions

Let the developer pick, giving complete, 1 paragraph long description and reasoning for each pain point

After VERIFY gate passes, present to developer, in tabular form:

1. Summary of what was done
2. Findings done along the work
3. Potential issues

As next, propose commit message and offer performing the commit after it passes manual developer check.

## Standards

### Code standards

Based off following main standards living in automotive/aviation/space industries:

1. MISRA C 2025 + C++ 2023, distilled from bought copies
2. NASA JPL's Power of Ten
3. TigerStyle
4. Zen of Python
5. YAGNI
6. Grug-brain development

Each of them shall be combined, de-duplicated and distilled into one, coherent set of coding rules - applicable universally across tech stacks, with distilled versions of each living in `refs/` directory

Distilled version of rule set above is subject to interpretation for each specific project worked on and language used for code - Language-specific coding practices should be applied as additions, verbatim, to rule set provided.

Hard rules described in documents like Power of Ten/MISRA should live as machine-checkable gates by utilizing targeted tests

Hard rules should be analyzed and machine-checkable gates should be enforced by using targeted tests, while styling-level propositions should live as part of coding rules.

As first principle for the rules, number one is: "Code with quality equal being maintainable by human without AI assistance, of junior level skill level" 

### Test standards

1. For standard-derived tests, one test=one rule
2. Tests are THE gates: executable specifications, described through ADR entries.
3. Testing is done mainly on system/integration level
4. Unit tests and E2E are used sporadically, when system/integration tests aren't sufficient to properly cover the needs; ask the developer when the current testing level won't suffice for advice.

## AGENTS.md
Not a skill, but a template to fill.

Contracts living as skills are mandatory to work on project; If not available - inform and offer installation

Follows loaded skills strictly

"Assisted-By: `name-of-agent` <email@ofagent.xyz>" as sole trailer of commits

