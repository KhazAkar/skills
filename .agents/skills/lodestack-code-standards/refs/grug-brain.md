# Grug-brain development — distilled digest

Source: grugbrain.dev — public essay. Per the assembly decision,
the underlying RULES are distilled, not the prose voice.

- **Complexity is the demon** → the enemy is not bugs, it is the
  complexity that hides them. Folds into: small units, boring over
  clever, YAGNI, minimal interface.
- **Say no early** → declining a feature/complexity is cheapest at
  proposal time — the ANALYZE REJECT verdict and the backlog exist
  for this.
- **The big-brain trap** → clever abstractions impress their author
  and cost every later reader. A junior must be able to maintain
  the code; the trap is measured against that junior.
- **Factor fear, not elegance** → refactor when the pain is real,
  not when the shape could be prettier. No drive-by refactors
  (lodestack-edit port).
- **Tests you run locally are the real tests** → a test suite that
  needs a ceremony isn't a gate. Folds into test-standards:
  executable specifications.
- **Boring technology** → dependencies are decisions; proven-boring
  beats novel-clever.
