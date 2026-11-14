# MISRA C++:2023 — distilled digest (PENDING)

Status: **pending distillation from the bought copy.**
Paraphrase-only — never verbatim rule text (MISRA copyright).

Purpose of this digest: the subset of MISRA C++:2023 that folds into
the universal rule set (SKILL.md), the rules that become
`gate: analyzer` entries, and the C++-specific verbatim additions
for Reference.md. C++:2023 is the edition aligned with modern C++
(C++17) — its rules on smart pointers, exceptions and RAII may
soften or scope the native-scope memory rules for modern codebases.

Skeleton to fill from the bought copy:
- rules that duplicate existing universal rules (dedupe into the set)
- rules that are new universal candidates
- rules that are C++-specific additions (go to Reference.md)
- where C++:2023 permits what the native-scope rules restrict —
  record as scoped interpretation, not silent weakening
