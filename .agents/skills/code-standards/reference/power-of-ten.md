# The Power of Ten — rationale digest

Paraphrased digest of G. J. Holzmann, "The Power of 10: Rules for
Developing Safety-Critical Code", IEEE Computer, June 2006, as hosted
by the author at https://spinroot.com/gerard/pdf/P10.pdf. Compiled
2026-11-07 for review-time and ADR-time reference. This file carries
our wording, not the source's; short quotes are attributed. Read the
paper for the original prose. The distilled rules in
[SKILL.md](../SKILL.md) win over both.

## Why ten rules

Most coding standards fail structurally, not for lack of effort: they
bloat past a hundred rules, mix personal taste with real safeguards,
and cannot be checked by tools, so developers ignore them. Holzmann's
counter-thesis: a small set (capped at ten), clear enough to remember
and precise enough to check mechanically, buys measurable reliability
and analyzability. The strictness is the trade for being able to
prove things about the code. The rules target C because its analysis
tooling is mature: analyzers, model extractors, debuggers, stable
compilers.

## The rules and why each earns its place

1. **Simple control flow.** No goto, no setjmp/longjmp, no recursion.
   Simple flow checks better and reads better; banning recursion makes
   the call graph acyclic, which analyzers exploit to prove that
   things meant to be bounded really are. A single exit point is not
   required; an early error return is often the simpler structure.
2. **A fixed upper bound on every loop.** If a checking tool cannot
   prove the iteration cap statically, the rule is violated.
   Non-terminating loops are the exception and must be provably
   non-terminating. The practical trick: give variable-iteration loops
   an explicit cap; exceeding it trips an assertion and returns an
   error.
3. **No dynamic allocation after initialization.** Allocators are
   unpredictable in time and error-prone in use (leaks,
   use-after-free, overruns, over-allocation). Pre-allocated memory
   plus the recursion ban makes both heap and stack usage statically
   provable.
4. **Functions short enough to print.** About 60 lines, one action per
   line. A function should be one reviewable, verifiable logical
   unit; excessive length is a smell of poor structure.
5. **Assertion density: at least two per function.** Assertions are
   side-effect-free Boolean checks of conditions that should never
   occur, with a recovery action (typically returning an error) on
   failure. They must be non-trivial: an assertion a tool can prove
   can never fail does not count. The cited industrial statistic: unit
   tests find roughly one defect per 10 to 100 lines written, and
   assertion density raises the interception odds.
6. **Smallest possible scope for data.** Out of scope means out of
   reach: nothing can reference or corrupt what it cannot see. Fewer
   assignment sites mean faster diagnosis, and reusing one variable
   for unrelated purposes muddies debugging.
7. **Check every return value; validate every parameter.** The most
   violated rule. When ignoring a return is genuinely equivalent to
   handling it (printf, close), make the choice explicit with a (void)
   cast or a justifying comment; otherwise check it.
8. **Preprocessor discipline.** Includes and simple macros only: no
   token pasting, variadic macros, or recursive macros; conditional
   compilation kept to a justified minimum, flagged by a checker.
   Ten #ifdef directives can mean 2^10 code variants, each needing
   its own testing.
9. **Restricted pointers.** One level of dereference, no hidden
   dereferences in macros or typedefs, no function pointers. Deep and
   dynamic indirection defeats static analysis, including the proof
   that recursion is absent.
10. **Zero warnings, strictest tools, from day one.** Pedantic
    compiler settings, warning-free builds, and at least one
    state-of-the-art static analyzer run daily. Even a seemingly bogus
    warning is a signal: rewrite the code until the tool understands
    it, because "invalid" warnings have a track record of being right
    in less obvious ways.

## Why the set hangs together

Rules 1 and 2 buy transparent, analyzable control flow; rule 3
removes an entire failure class; rules 4 to 7 are widely accepted good
style and carry much of design-by-contract; rules 8 and 9 keep the
code legible to tools; rule 10 makes compliance mechanical rather
than aspirational. JPL used the rules experimentally for
mission-critical software with encouraging results. In Holzmann's
words: "The rules act like the seat-belt in your car: initially they
are perhaps a little uncomfortable, but after a while their use
becomes second-nature and not using them becomes unimaginable."
