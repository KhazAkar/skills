# Research the hardware (datasheets & erratas)

Reference for Phase 2 of the workflow. Firmware only makes sense in the
context of its silicon.

## Identify the part

From markings (top mark, package, package code). Don't trust markings as the
sole identifier; cross-check package, pinout, and at least one datasheet
register against the binary.

## Find the datasheet and errata

From the vendor. Errata are mandatory: undocumented workarounds, disabled
silicon, and reserved registers are where weird behavior lives. Errata change
behavior — always read the errata, not just the datasheet.

## Convert PDFs to greppable markdown

Using `anydoc` (or an equivalent PDF→markdown converter):
```bash
anydoc datasheet-<part>.pdf > datasheets/<part>.md
anydoc errata-<part>.pdf   > datasheets/<part>-errata.md
```

## Grep around the converted markdown

For the things you actually need:
```bash
grep -n -i -E 'register|0x[0-9a-f]{4}|MMIO|address|reset value|errata' datasheets/<part>.md
grep -n -C3 'USART1_CR1' datasheets/<part>.md
grep -n -C5 'ERRATA' datasheets/<part>-errata.md
```

## Build a register/address map

From the datasheet (memory regions, peripheral bases, vector table, reset/boot
address) and cross-reference it against the binary. Note any errata items that
affect interpretation (e.g. a peripheral that must be accessed byte-wise).

Never reason about a register address without the matching datasheet entry.

## Datasheet/Errata Research Loop

1. Identify a part or a behavior you don't understand in the binary.
2. Locate the datasheet and errata PDFs.
3. Convert to markdown: `anydoc <file>.pdf`.
4. `grep` the markdown for registers, addresses, or errata keywords.
5. Record the finding in the matching lode file (`register-map.md`,
   `boot-sequence.md`, etc.) and cite the datasheet page/section.
6. Cross-reference the finding against the binary.
