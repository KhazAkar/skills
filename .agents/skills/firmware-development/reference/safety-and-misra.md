Reference for Phase 2 / section Safety and coding standards of the workflow.

## When it applies

Adopt this process when a customer contract or project standard requires it,
or when the product is safety-relevant under an ASIL, SIL, or software class.
Record the applicable customer standard and target level in an ADR before
writing deviations.

## C analysis

Cppcheck's MISRA addon needs the checker and rule text file. Rule texts are
not redistributable; obtain them through the licensed project process:

```bash
cppcheck --enable=all --addon=misra \
  --rule-texts=<file> --project=<compile_commands.json>
```

Keep the rule-text file outside source control unless its license permits
inclusion. Run the same compiler defines and include paths as the target
build. Treat warnings as review inputs, not as a reason to suppress broadly.

## C and C++ analysis

Use `clang-tidy` with the project compilation database:

```bash
clang-tidy src/<file>.cpp \
  -checks='-*,cert-*,bugprone-*' \
  -p=build-host
```

For C++, MISRA C++:2023 and AUTOSAR C++14 are common standards. Select one in
the ADR, document checker coverage, and do not claim compliance from a small
subset of checks.

## Rules that embedded code hits often

| Risk | Compliant idiom |
|---|---|
| implicit conversion | use fixed-width types, explicit casts, and checked ranges |
| `goto` | structured cleanup or one documented cleanup label with deviation |
| recursion | bounded iterative state machines |
| dynamic memory | static storage or an audited fixed pool initialized early |
| unions | tagged structs or a documented, controlled representation |
| ignored return value | check and handle every status, or cast to `(void)` with rationale |

Also review integer promotions, signed/unsigned comparisons, volatile access,
shift widths, enum ranges, interrupt sharing, and initialization order.
`-Wall -Wextra -Werror` complements, but does not replace, MISRA analysis.

## Deviation ADR

Use the lode-programming ADR format and include the rule identity:

```text
Status: Accepted
Context: <requirement and code path>
Rule ID: <MISRA-C/C++ rule>
Justification: <why the compliant alternative is infeasible>
Scope: <files, functions, target, and lifetime>
Mitigation: <bounds, review, test, static check, and runtime guard>
Decision: <exact permitted deviation>
Consequences: <residual risk and maintenance condition>
Alternatives: <considered compliant alternatives>
Evidence: <tests, coverage, analysis output, and reviewer>
```

Keep the deviation narrow. A project-wide suppression is not a deviation
record.

## Rust equivalents

Keep application crates safe by default:

```rust
#![forbid(unsafe_code)]
```

Place unavoidable HAL or PAC interop in a small, reviewed crate. Every unsafe
block has a `// SAFETY:` comment explaining the invariant:

```rust
// SAFETY: the peripheral singleton guarantees exclusive access.
unsafe { write_register(value) };
```

Run clippy with a strict baseline:

```bash
cargo clippy --all-targets --all-features -- \
  -W clippy::pedantic -D warnings
```

Ferrocene is a qualified Rust toolchain option for ISO 26262 and IEC 61508
work. Qualification needs project evidence and process controls; using Rust
alone does not establish a safety claim.

## Process evidence

- Trace requirements to design elements, tests, and released artifacts.
- Keep unit, emulator, target, and HIL coverage evidence with the test record.
- Record the applicable ASIL, SIL, or software class in an ADR.
- Pin analyzer versions and preserve command lines and reports.
- Review every suppression and deviation at the required safety level.
- Make safety claims only for the scope that was analyzed and tested.
