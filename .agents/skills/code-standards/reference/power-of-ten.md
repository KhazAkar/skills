# The Power of Ten — Rules for Developing Safety Critical Code

Source: https://spinroot.com/gerard/pdf/P10.pdf — Gerard J. Holzmann,
NASA/JPL Laboratory for Reliable Software, Pasadena, CA. Fetched
2026-11-07 and converted to Markdown: wording preserved, layout
normalized, PDF conversion noise fixed ("210" restored to 2^10,
footnotes dropped). This snapshot backs the distillation in
[SKILL.md](../SKILL.md); where the two disagree, the distilled skill
text wins for Damian's repos.

## Why so few rules

Most serious software development projects use coding guidelines.
These guidelines are meant to state what the ground rules are for the
software to be written: how it should be structured and which language
features should and should not be used. Curiously, there is little
consensus on what a good coding standard is. Among the many that have
been written there are remarkably few patterns to discern, except that
each new document tends to be longer than the one before it. The
result is that most existing guidelines contain well over a hundred
rules, sometimes with questionable justification. Some rules,
especially those that try to stipulate the use of white-space in
programs, may have been introduced by personal preference; others are
meant to prevent very specific and unlikely types of error from
earlier coding efforts within the same organization. Not surprisingly,
the existing coding guidelines tend to have little effect on what
developers actually do when they write code. The most dooming aspect
of many of the guidelines is that they rarely allow for comprehensive
tool-based compliance checks. Tool-based checks are important, since
it is often infeasible to manually review the hundreds of thousands
of lines of code that are written for larger applications.

The benefit of existing coding guidelines is therefore often small,
even for critical applications. A verifiable set of well-chosen
coding rules could, however, make critical software components more
thoroughly analyzable, for properties that go beyond compliance with
the set of rules itself. To be effective, though, the set of rules
has to be small, and must be clear enough that it can easily be
understood and remembered. The rules will have to be specific enough
that they can be checked mechanically. To put an easy upper-bound on
the number of rules for an effective guideline, I will argue that we
can get significant benefit by restricting to no more than ten rules.
Such a small set, of course, cannot be all-encompassing, but it can
give us a foothold to achieve measurable effects on software
reliability and verifiability. To support strong checking, the rules
are somewhat strict — one might even say Draconian. The trade-off,
though, should be clear. When it really counts, especially in the
development of safety critical code, it may be worth going the extra
mile and living within stricter limits than may be desirable. In
return, we should be able to demonstrate more convincingly that
critical software will work as intended.

The choice of language for safety critical code is in itself a key
consideration. At many organizations, JPL included, critical code is
written in C, with its extensive tool support: strong source code
analyzers, logic model extractors, metrics tools, debuggers, test
support tools, and mature, stable compilers. For fairly pragmatic
reasons, then, these rules primarily target C and attempt to optimize
the ability to more thoroughly check the reliability of critical
applications written in C.

## Rule 1 — simple control flow

**Rule:** Restrict all code to very simple control flow constructs —
do not use goto statements, setjmp or longjmp constructs, and direct or
indirect recursion.

**Rationale:** Simpler control flow translates into stronger
capabilities for verification and often results in improved code
clarity. The banishment of recursion is perhaps the biggest surprise
here. Without recursion, though, we are guaranteed to have an acyclic
function call graph, which can be exploited by code analyzers, and can
directly help to prove that all executions that should be bounded are
in fact bounded. (This rule does not require that all functions have a
single point of return — there are enough cases where an early error
return is the simpler solution.)

## Rule 2 — fixed loop bounds

**Rule:** All loops must have a fixed upper-bound. It must be
trivially possible for a checking tool to prove statically that a
preset upper-bound on the number of iterations of a loop cannot be
exceeded. If the loop-bound cannot be proven statically, the rule is
considered violated.

**Rationale:** The absence of recursion and the presence of loop bounds
prevents runaway code. The rule does not apply to iterations that are
meant to be non-terminating (e.g., in a process scheduler); in those
cases the reverse rule applies: it should be statically provable that
the iteration cannot terminate. One way to support the rule is to add
an explicit upper-bound to all loops that have a variable number of
iterations; when the upper-bound is exceeded an assertion failure is
triggered, and the function containing the failing iteration returns
an error.

## Rule 3 — no dynamic memory allocation after initialization

**Rule:** Do not use dynamic memory allocation after initialization.

**Rationale:** Memory allocators, such as malloc, and garbage
collectors often have unpredictable behavior that can significantly
impact performance. A notable class of coding errors also stems from
mishandling of memory allocation and free routines: forgetting to free
memory or continuing to use memory after it was freed, attempting to
allocate more memory than physically available, overstepping
boundaries on allocated memory, etc. Forcing all applications to live
within a fixed, pre-allocated, area of memory can eliminate many of
these problems and make it easier to verify memory use. In the absence
of recursion (Rule 1), an upper-bound on the use of stack memory can
be derived statically, making it possible to prove that an application
will always live within its pre-allocated memory means.

## Rule 4 — short functions

**Rule:** No function should be longer than what can be printed on a
single sheet of paper in a standard reference format with one line per
statement and one line per declaration. Typically, this means no more
than about 60 lines of code per function.

**Rationale:** Each function should be a logical unit in the code that
is understandable and verifiable as a unit. It is much harder to
understand a logical unit that spans multiple screens or multiple
pages when printed. Excessively long functions are often a sign of
poorly structured code.

## Rule 5 — assertion density

**Rule:** The assertion density of the code should average to a
minimum of two assertions per function. Assertions are used to check
for anomalous conditions that should never happen in real-life
executions. Assertions must always be side-effect free and should be
defined as Boolean tests. When an assertion fails, an explicit
recovery action must be taken, e.g., by returning an error condition
to the caller of the function that executes the failing assertion.
Any assertion for which a static checking tool can prove that it can
never fail or never hold violates this rule.

**Rationale:** Statistics for industrial coding efforts indicate that
unit tests often find at least one defect per 10 to 100 lines of code
written. The odds of intercepting defects increase with assertion
density. Assertions can be used to verify pre- and post-conditions of
functions, parameter values, return values of functions, and
loop-invariants. Because assertions are side-effect free, they can be
selectively disabled in performance-critical code. A typical use:

```c
if (!c_assert(p >= 0) == true) {
    return ERROR;
}
```

with the assertion defined as a macro that prints file and line on
failure (a no-op print on embedded processors), so that the assertion
turns into a pure Boolean test that enables error recovery.

## Rule 6 — smallest scope

**Rule:** Data objects must be declared at the smallest possible level
of scope.

**Rationale:** This rule supports a basic principle of data-hiding. If
an object is not in scope, its value cannot be referenced or corrupted.
Similarly, if an erroneous value of an object has to be diagnosed, the
fewer the number of statements where the value could have been
assigned, the easier it is to diagnose the problem. The rule
discourages the re-use of variables for multiple, incompatible
purposes, which can complicate fault diagnosis.

## Rule 7 — check return values and parameters

**Rule:** The return value of non-void functions must be checked by
each calling function, and the validity of parameters must be checked
inside each function.

**Rationale:** This is possibly the most frequently violated rule. In
its strictest form, even the return value of printf and close
statements must be checked. If the response to an error would
rightfully be no different than the response to success, there is
little point in explicitly checking a return value; in those cases it
can be acceptable to explicitly cast the function return value to
(void), thereby indicating that the programmer explicitly decides to
ignore a return value. In more dubious cases, a comment should explain
why a return value is irrelevant. Often, it will be easier to comply
with the rule than to explain why non-compliance might be acceptable.

## Rule 8 — limited preprocessor use

**Rule:** The use of the preprocessor must be limited to the inclusion
of header files and simple macro definitions. Token pasting, variable
argument lists (ellipses), and recursive macro calls are not allowed.
All macros must expand into complete syntactic units. The use of
conditional compilation directives is often also dubious, but cannot
always be avoided; there should rarely be justification for more than
one or two conditional compilation directives even in large software
development efforts, beyond the standard boilerplate that avoids
multiple inclusion of the same header file. Each such use should be
flagged by a tool-based checker and justified in the code.

**Rationale:** The C preprocessor is a powerful obfuscation tool that
can destroy code clarity and befuddle many text based checkers. Note
that with just ten conditional compilation directives, there could be
up to 2^10 possible versions of the code, each of which would have to
be tested — causing a huge increase in the required test effort.

## Rule 9 — restricted pointers

**Rule:** The use of pointers should be restricted. Specifically, no
more than one level of dereferencing is allowed. Pointer dereference
operations may not be hidden in macro definitions or inside typedef
declarations. Function pointers are not permitted.

**Rationale:** Pointers are easily misused, even by experienced
programmers. They can make it hard to follow or analyze the flow of
data in a program, especially by tool-based static analyzers. Function
pointers can seriously restrict the types of checks that can be
performed by static analyzers; for instance, if function pointers are
used, it can become impossible for a tool to prove absence of
recursion.

## Rule 10 — zero warnings, strict tools

**Rule:** All code must be compiled, from the first day of
development, with all compiler warnings enabled at the compiler's most
pedantic setting. All code must compile with these settings without
any warnings. All code must be checked daily with at least one, but
preferably more than one, state-of-the-art static source code analyzer
and should pass the analyses with zero warnings.

**Rationale:** There simply is no excuse for any software development
effort not to make use of this readily available technology. The rule
of zero warnings applies even in cases where the compiler or the
static analyzer gives an erroneous warning: if the tool gets confused,
the code causing the confusion should be rewritten so that it becomes
more trivially valid. Many developers have been caught in the
assumption that a warning was surely invalid, only to realize much
later that the message was in fact valid for less obvious reasons.

## Closing

The first two rules guarantee the creation of a clear and transparent
control flow structure that is easier to build, test, and analyze. The
absence of dynamic memory allocation (Rule 3) eliminates a class of
problems related to the allocation and freeing of memory and the use
of stray pointers. Rules 4 to 7 are fairly broadly accepted as
standards for good coding style; the discipline of "design by
contract" can partly be found in rules 5 to 7.

The ten rules are being used experimentally at JPL in the writing of
mission critical software, with encouraging results. After overcoming
a healthy initial reluctance to live within such strict confines,
developers often find that compliance with the rules does tend to
benefit code clarity, analyzability, and code safety. The rules act
like the seat-belt in your car: initially they are perhaps a little
uncomfortable, but after a while their use becomes second-nature and
not using them becomes unimaginable.
