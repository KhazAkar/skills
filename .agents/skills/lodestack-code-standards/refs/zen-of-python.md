# Zen of Python (PEP 20) - distilled digest

Source: Tim Peters, PEP 20 - public, freely quotable.
Distillation: which aphorisms fold into the universal set, and how.

- **Errors should never pass silently** -> universal rule, verbatim
  spirit. "Unless explicitly silenced" = the recorded reason.
- **Explicit is better than implicit** -> folds into one-word-one-
  meaning, minimal logical interface, no hidden control flow.
- **Simple is better than complex** -> small units, boring over
  clever, YAGNI.
- **Readability counts** -> upgraded: maintainability counts -
  readability is necessary, not sufficient.
- **Special cases aren't special enough to break the rules** ->
  deviations are ADR receipts, not silent exceptions. "Although
  practicality beats purity" = the receipt exists *because*
  practicality sometimes wins - the ADR records the trade.
- **There should be one obvious way to do it** -> boring over
  clever; match the file's existing style (lodestack-edit).
- **Sparse is better than dense** -> smallest scope, declare near
  use, minimal interface surface.
- **Now is better than never / never is often better than right
  now** -> YAGNI both ways: don't defer needed work, don't build
  speculative work.
