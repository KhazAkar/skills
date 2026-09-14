---
name: "firmware-reverse-engineering"
description: "Use this skill for firmware reverse-engineering work: dump and back up target firmware before anything else, research datasheets/erratas (PDFs converted to markdown) to understand the hardware, and document the process with the lode-programming methodology."
version: "1.0"
author: "Damian Zaręba"
license: "MIT"
tags:
  - firmware
  - reverse-engineering
  - embedded
  - hardware
  - documentation
  - lode
---

# Skill: firmware-reverse-engineering

## Purpose
Reverse-engineer embedded/firmware targets safely and methodically. The three
pillars are, in strict order:

1. **Back up everything first.** Never mutate the only copy of a device, flash
   image, or dump. Create read-only backups of firmware, EEPROM, fuses, config,
   and device state before any read/analysis/write attempt.
2. **Research datasheets and errata.** Identify every silicon part (MCU, flash,
   PMIC, radio, sensor) and read the manufacturer datasheet and errata before
   interpreting the binary. Convert reference PDFs to markdown so they are
   greppable, then search them for registers, addresses, and errata notes.
3. **Document as you go with lode-programming.** Maintain a `lode/` folder
   capturing the target, the silicon map, the toolchain, ADRs for every
   non-obvious decision, and the findings as they emerge.

## When to Load
- Dumping or analyzing firmware from a device
- Identifying unknown chips, register maps, or boot sequences
- Researching datasheets/erratas for parts on a target board
- Mapping a binary to its hardware peripherals
- Setting up toolchains (disassemblers, emulators, JTAG/SWD/UART)
- Onboarding a new target into an existing reversing effort

## Mandatory Workflow (in order)

### 1. Backup before all else
Before any operation that could read, write, or erase the target:

- **Identify the original artifact** (on-chip flash, external NOR/NAND, EEPROM,
  fuses, OTP, config pages, calibration data).
- **Create a read-only, checksummed backup** of every readable region into a
  separate `backups/` directory that is never written to again.
  - Record device identity, read method, programmer, voltage, and the command
    used (e.g. `flashrom -r backups/<device>-flash-<date>.bin --verify`).
  - Store a SHA-256 alongside every dump: `sha256sum backups/*.bin > backups/SHA256SUMS`.
- **Preserve fuses/OTP/calibration** separately; these are often one-way writes
  and the backup is the only way back.
- **Confirm the backup is restorable** (dry-run restore against a spare chip or
  an emulated target) before touching the live device further.

Work only from copies after this point. Treat the original backups as
write-once evidence.

### 2. Research the hardware (datasheets & erratas)
Firmware only makes sense in the context of its silicon. For each part on the
board:

- **Identify the part** from markings (top mark, package, package code).
- **Find the datasheet and errata** from the vendor. Errata are mandatory:
  undocumented workarounds, disabled silicon, and reserved registers are
  where weird behavior lives.
- **Convert PDFs to greppable markdown** using `anydoc` (or an equivalent
  PDF→markdown converter):
  ```bash
  anydoc datasheet-<part>.pdf > datasheets/<part>.md
  anydoc errata-<part>.pdf   > datasheets/<part>-errata.md
  ```
- **Grep around** the converted markdown for the things you actually need:
  ```bash
  grep -n -i -E 'register|0x[0-9a-f]{4}|MMIO|address|reset value|errata' datasheets/<part>.md
  grep -n -C3 'USART1_CR1' datasheets/<part>.md
  grep -n -C5 'ERRATA' datasheets/<part>-errata.md
  ```
- **Build a register/address map** from the datasheet (memory regions, peripheral
  bases, vector table, reset/boot address) and cross-reference it against the
  binary. Note any errata items that affect interpretation (e.g. a peripheral
  that must be accessed byte-wise).

Never reason about a register address without the matching datasheet entry.

### 3. Document as you go (lode-programming)
Load the **lode-programming** skill and keep the `lode/` folder current. For a
firmware effort the lode minimally contains:

```
lode/
├── summary.md              # Target device, board revision, goal of the effort
├── terminology.md          # Part numbers, acronyms, tool names
├── practices.md            # Read methods, voltages, toolchain, safety rules
├── lode-map.md             # Index of all lode files
└── decisions/             # ADRs
    └── [number]-[name].md
```

Recommended firmware-specific lode files (one topic per file, <250 lines):

- `silicon-map.md` — parts on the board, their packages, and datasheet links.
- `register-map.md` — peripheral bases, MMIO regions, and known registers.
- `memory-map.md` — flash regions, RAM, EEPROM/fuses, vector/boot addresses.
- `boot-sequence.md` — reset path from entry point to first user code.
- `backups.md` — what was dumped, from where, with which command + checksum.
- `toolchain.md` — programmer, disassembler, emulator, scripts, and versions.

Write an ADR for every non-obvious decision (tool choice, read voltage, assumed
reset vector, identification of a part from a partial marking).

## Safety Rules
- **Read before write.** Never write to a device you have not fully backed up.
- **Lowest safe voltage** for reads; document the voltage used.
- **Verify every dump** against the device immediately after reading.
- **Fuses/OTP/calibration are one-way** — back them up first and never re-flash
  without a known-good image.
- **Don't trust markings** as the sole identifier; cross-check package, pinout,
  and at least one datasheet register against the binary.
- **Errata change behavior.** Always read the errata, not just the datasheet.

## Datasheet/Errata Research Loop
1. Identify a part or a behavior you don't understand in the binary.
2. Locate the datasheet and errata PDFs.
3. Convert to markdown: `anydoc <file>.pdf`.
4. `grep` the markdown for registers, addresses, or errata keywords.
5. Record the finding in the matching lode file (`register-map.md`,
   `boot-sequence.md`, etc.) and cite the datasheet page/section.
6. Cross-reference the finding against the binary.

## Commands (Natural Language)
- *"Back up this device"* → dump every readable region, checksum, verify, log to
  `lode/backups.md`.
- *"Research <part>"* → fetch datasheet+errata, `anydoc` to markdown, grep for
  registers/errata, update `lode/silicon-map.md` and `lode/register-map.md`.
- *"What does the lode say about <peripheral>?"* → search lode files.
- *"Create ADR for <decision>"* → use the lode ADR template.

## Dependencies
- **lode-programming** — for the `lode/` documentation structure and ADRs.
- **anydoc** (or equivalent PDF→markdown converter) — to make datasheets/erratas
  greppable.
- A flash read tool (e.g. `flashrom`, vendor tools, JTAG/SWD) for backups.
