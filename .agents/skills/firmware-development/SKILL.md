---
name: "firmware-development"
description: "Use this skill for embedded firmware development in C, C++ or Rust: know the silicon (inventory + datasheets/errata) before coding, build reproducibly with a pinned toolchain, test on the host and in an emulator before flashing, flash with backup+verify and a recovery path — as a specialized path on top of the lode-programming backbone, which owns the lode/ folder, ADRs and their update cadence."
version: "1.0"
author: "Damian Zaręba"
license: "MIT"
tags:
  - firmware
  - embedded
  - c
  - cpp
  - rust
  - hardware
  - documentation
  - lode
---

# Skill: firmware-development

## Purpose
Build firmware for embedded targets in **C, C++ or Rust** safely and
reproducibly. This is the constructive twin of **firmware-reverse-engineering**:
that skill answers *what does the existing firmware do*, this one answers *how
do we build firmware that does what we want*. Both share the same hardware
knowledge, the same debug tooling and the same `lode/` file names, so a board
understood with one skill is directly buildable with the other.

**lode-programming is the backbone; this skill is a specialized path on it.**
Load lode-programming first and follow its cadence: an ADR the moment an
architectural decision is taken (before the code it justifies), and the
affected `lode/` files updated at the end of each cycle — one user
prompt/feature. This skill adds only the firmware-specific file names (see
*Lode files* below); it does not restate structure, ADR format or cadence.

The four pillars, in strict order:

1. **Know the silicon before writing a line.** Inventory the hardware, read the
   datasheet **and errata** for every part you touch, and write the memory and
   pin maps down before any code.
2. **Reproducible build.** One pinned toolchain, one build command, the linker
   script and flags owned in-repo, warnings as errors, size reported on every
   build.
3. **Test before you flash.** Logic is tested on the host (TDD), then in an
   emulator, then on the target — in that order. Flashing is the last, not the
   first, way to find out whether code works.
4. **Flash safely.** Back up whatever is on the chip, flash, verify, keep a
   known-good image, and always know the recovery path before you need it.

## When to Load
- Starting a new firmware project or adding a new target/board to one
- Writing or reviewing drivers, ISRs, DMA, clock or power configuration
- Choosing a toolchain, build system, SDK, RTOS, or language for a target
- Setting up host-side unit tests, emulator runs, or on-target debugging
- Flashing a board, writing a bootloader, or planning firmware updates
- Onboarding to an existing firmware codebase

## Shared references
Content that both firmware skills need lives in `../_shared/` and is linked,
never copied:

- **[../_shared/backup.md](../_shared/backup.md)** — dump + verify + checksum
  before writing anything.
- **[../_shared/datasheets.md](../_shared/datasheets.md)** — `anydoc`
  PDF→markdown flow and the datasheet/errata research loop.
- **[../_shared/dynamic-debugging.md](../_shared/dynamic-debugging.md)** —
  `openocd`, `gdb`, RTT/semihosting, UART console, QEMU.
- **[../_shared/usb.md](../_shared/usb.md)**,
  **[../_shared/ethernet.md](../_shared/ethernet.md)**,
  **[../_shared/can.md](../_shared/can.md)** — protocol framing, IDs and
  capture, when the target speaks one of them.

## Phase 0: Load lode, inventory hardware (prerequisite)
Load **lode-programming** first; in an existing repo read `lode/lode-map.md`
before anything else.

Then, identical to Phase 0 of firmware-reverse-engineering: ask the user once which
programmer/debug probe, soldering station, multimeter, logic analyzer,
oscilloscope and other tools exist, and record the answers in
`lode/toolchain.md`. For development additionally record:

- **Target board** — eval kit / dev board / custom PCB, revision, and whether
  it ships with firmware that must be backed up first.
- **Power** — bench supply or USB-only, current-limit available or not
  (matters for first power-on of custom hardware and for brown-out testing).
- **Debug probe firmware** — probe model *and* firmware version (ST-LINK,
  J-Link, CMSIS-DAP, Black Magic, probe-rs-compatible); it decides which
  `openocd`/`probe-rs` features work.
- **Spare unit** — is there a second board to brick? If not, the recovery path
  in Phase 4 is mandatory before the first flash.

Tools gate methods: never plan a test or flash step you lack the hardware for.
Record the fallback as an ADR.

## Mandatory Workflow (in order)
Each phase is summarized here; commands and templates live in `reference/`
and `../_shared/`. Load the linked file when you actually perform the phase.
The `lode/` files each phase feeds are listed under *Lode files* below.

### 1. Know the silicon
For the MCU and every peripheral IC you will drive, follow the
datasheet/errata loop in **[../_shared/datasheets.md](../_shared/datasheets.md)**
*before* writing the driver — errata routinely change the register sequence a
driver must use. Produce or update:

- `lode/silicon-map.md` — parts, packages, datasheet + errata links.
- `lode/memory-map.md` — flash/RAM regions, vector table, boot address; this
  is the single source for the linker script.
- `lode/pinmux.md` — every used pin: function, alternate-function number,
  direction, pull, speed, and which peripheral instance owns it.
- `lode/register-map.md` — peripheral bases and the registers you actually
  touch, each cited to a datasheet section.


Never write a register address that is not in `register-map.md` with a
datasheet citation.

### 2. Reproducible build
The build must be reproducible by a human with no AI and no IDE: a pinned
toolchain, a single documented build command, the linker script and all flags
in the repository, `-Werror` (or `#![deny(warnings)]` in CI) and a size
report on every build. Decide language and build system per project and write
the ADR *before* creating the build files:

- **C** — `arm-none-eabi-gcc` / `riscv64-unknown-elf-gcc` or `clang`, CMake
  with a toolchain file, C11 or newer.
- **C++** — same toolchain, C++17 or newer, `-fno-exceptions -fno-rtti` unless
  an ADR says otherwise, no dynamic allocation after init.
- **Rust** — stable toolchain pinned in `rust-toolchain.toml`, `#![no_std]`,
  `embedded-hal` traits, a PAC/HAL crate, `probe-rs` for flash/debug, `defmt`
  for logging. `cargo build --release` is the build command.

Output: `lode/build.md` — toolchain versions, the build command, linker
script location, flags and why, how to read the size/map report.

See **[reference/toolchain-and-build.md](reference/toolchain-and-build.md)**
for toolchain pinning, CMake toolchain files, linker script skeleton, flags,
`size`/map-file reading, Rust `memory.x`/`.cargo/config.toml`, and the
"build twice, compare hashes" reproducibility check.

### 3. Test before you flash
Follow TDD (the lode-programming/AMDD practice): the test comes before the
code, on the host first. Structure firmware so that application logic depends
on a thin HAL seam (C/C++ interface or Rust trait) that can be replaced by a
fake on the host.

Order of test environments, cheapest first:

1. **Host unit tests** — logic, protocol parsers, state machines, math.
   Unity/CMock or CppUTest for C, GoogleTest/Catch2 for C++, `cargo test` on
   the host target for Rust (`no_std` crates tested via a `std` test feature).
2. **Emulator** — QEMU or Renode for boot, vector table, linker script and
   peripheral wiring, and for CI runs without hardware.
3. **On-target smoke test** — the smallest binary that proves clock, UART/RTT
   output and the watchdog work on the real board.
4. **Hardware-in-the-loop** — only when the Phase 0 inventory has the tool
   (logic analyzer, scope, bench supply) to observe the result.

Output: `lode/testing.md` — how to run each level, what it covers, what it
cannot cover.

See **[reference/testing.md](reference/testing.md)** for the HAL seam pattern
in C, C++ and Rust, host test frameworks, QEMU/Renode invocation, and the
on-target smoke test.

### 4. Flash safely
Before the first flash of any board that already contains firmware, run the
backup procedure in **[../_shared/backup.md](../_shared/backup.md)** and log it
in `lode/backups.md`. Then, every flash: **flash → verify → record the image
hash**. Keep the last known-good image alongside the backups. Know the
recovery path (BOOT pins, ROM bootloader, mass erase, readout-protection
unlock) *before* you need it and write it in `lode/recovery.md`.

Any product that will be updated in the field needs a bootloader decision
(single image + ROM bootloader, dual-slot with image CRC/signature, or a
vendor/OSS bootloader such as MCUboot) recorded as an ADR before the memory
map is frozen — the bootloader owns the first flash sectors.

See **[reference/flash-and-recovery.md](reference/flash-and-recovery.md)** for
flash+verify commands per probe (`openocd`, `probe-rs`, vendor ROM
bootloaders), the dual-slot bootloader outline, and the unbrick procedures per
chip family with their data-loss warnings.

## Lode files
Structure, ADR format and update cadence come from **lode-programming**.
Firmware adds these files (shared with firmware-reverse-engineering where the
name matches), each fed by the phase noted:

- `silicon-map.md`, `register-map.md`, `memory-map.md`, `boot-sequence.md`,
  `backups.md`, `toolchain.md` — same meaning as in the RE skill.
- `pinmux.md` — pin assignments (Phase 1).
- `build.md` — toolchain, build command, flags, size (Phase 2).
- `testing.md` — test levels and how to run them (Phase 3).
- `recovery.md` — how to unbrick this exact board (Phase 4).
- `clock-tree.md` — oscillator sources, PLL settings, bus clocks, and the
  order they must be brought up in (only if the project configures clocks
  itself; YAGNI otherwise).

Decisions that get an ADR when taken: language, build system, SDK vs bare
register access, bare-metal vs RTOS, bootloader strategy, logging transport,
an errata workaround, a safety/MISRA deviation. Iterating on one ADR while
the cycle is in flight is normal — that is the architecture part of AMDD.

## Driver and Runtime Rules
Firmware bugs that survive host tests are almost always in this list. Apply
them from the first commit, not after the first field failure:

- **MMIO is `volatile`** (C/C++) or goes through the PAC's `read()/write()/
  modify()` (Rust). Never cache a status register in a plain variable.
- **ISRs are short**: set a flag or push to a queue, return. No blocking, no
  allocation, no printf. Shared state between ISR and main is `volatile` +
  atomic (or a `critical_section`/`Mutex<RefCell>` in Rust).
- **Watchdog on from day one**, kicked from the main loop, never from a timer
  ISR (that defeats it).
- **Brown-out / reset cause** read and logged at boot; it is the only clue you
  get for field resets.
- **No dynamic allocation after init** unless an ADR justifies it.
- **Clocks and power before peripherals**: enable the peripheral clock, then
  configure, then enable the peripheral — in that order, per the datasheet.
- **DMA + cache**: on cores with a data cache, clean/invalidate around DMA
  buffers or place them in non-cacheable memory; document which in an ADR.
- **Errata first**: before blaming your driver, grep the errata for the
  peripheral (see the datasheet loop).

See **[reference/driver-patterns.md](reference/driver-patterns.md)** for
register-access idioms in C, C++ and Rust, ISR/shared-state patterns, DMA and
cache coherency, watchdog and reset-cause handling, and clock bring-up order.

## Debug Output
Pick one logging transport per project and record it as an ADR: UART is the
cheapest and works with any terminal; semihosting is free but halts the core
on every message; RTT (`openocd rtt`, `probe-rs`) is fast and needs only the
debug probe; `defmt` (Rust) is RTT with deferred formatting. Never ship a
build whose only difference from the debug build is `printf` being compiled
out — test what you flash.

See **[reference/debug-output.md](reference/debug-output.md)** for wiring each
transport in C/C++ and Rust and the trade-offs; the `openocd`/`gdb`/UART
commands themselves are in
**[../_shared/dynamic-debugging.md](../_shared/dynamic-debugging.md)**.

## Safety and Coding Standards
If the firmware is safety-relevant or a customer requires it, adopt a coding
standard early — retrofitting is far more expensive than starting with it:

- **C** — MISRA C:2012 (with Amendments), enforced with a static analyzer
  (`cppcheck --addon=misra`, or a commercial checker). Every deviation is an
  ADR.
- **C++** — MISRA C++:2023 or AUTOSAR C++14; the same deviation rule.
- **Rust** — no MISRA equivalent yet; use `#![forbid(unsafe_code)]` outside
  the HAL layer, `clippy` with `pedantic`, and document every `unsafe` block
  with a `// SAFETY:` comment.
- **Process** — if ISO 26262 / IEC 61508 / IEC 62304 apply, requirements
  tracing and test coverage evidence are project deliverables, not
  afterthoughts. Record the target level (ASIL/SIL/Class) in an ADR.

See **[reference/safety-and-misra.md](reference/safety-and-misra.md)** for the
analyzer setup, the deviation ADR shape, the rules that bite embedded code
most, and the Rust equivalents.

## RTOS Decision
Bare-metal super-loop vs RTOS (FreeRTOS, Zephyr, RTIC/Embassy in Rust) is a
project-level ADR, taken once, with the concurrency needs written down. This
skill deliberately does not teach RTOS internals; when an RTOS is chosen, load
its own documentation and record the chosen kernel, version and configuration
in `lode/build.md`.

## Safety Rules
- **Back up before the first flash** of any board that already has firmware.
- **Verify every flash** against the image immediately after writing.
- **Never flash without a known recovery path** written in `lode/recovery.md`.
- **Fuses/option bytes/readout protection are one-way or destructive** — an
  ADR before touching them, and never on the only board.
- **Datasheet + errata before driver.** No register write without a cited
  entry in `lode/register-map.md`.
- **Tests before target.** Host and emulator first; the board is the last
  test environment, not the first.
- **Tools gate methods.** Don't plan a debug or test step you lack the
  hardware for; record the fallback as an ADR.
- **A cycle is not done until the lode reflects it.** ADRs precede the code
  they justify; the affected `lode/` files are updated before the cycle ends.

## Commands (Natural Language)
- *"Inventory my hardware"* → run Phase 0, record in `lode/toolchain.md`.
- *"Set up the build for <chip>"* → Phase 2: toolchain pin, build system,
  linker script from `lode/memory-map.md`, `lode/build.md`, ADR.
- *"Write a driver for <peripheral>"* → datasheet+errata loop, entry in
  `lode/register-map.md`, host test first, then the driver.
- *"Flash the board"* → backup (first time), flash, verify, hash into
  `lode/backups.md`.
- *"How do I unbrick this?"* → `lode/recovery.md`.
- *"What does the lode say about <topic>?"* → search lode files.
- *"Create ADR for <decision>"* → use the lode ADR template.

## Dependencies
- **lode-programming** — the backbone: `lode/` structure, ADRs, update
  cadence, TDD/AMDD and YAGNI. Loaded in Phase 0.
- **firmware-reverse-engineering** — sibling skill; shares `../_shared/` and
  the lode file names. Load it when the board already carries firmware you
  need to understand.
- **anydoc** (or equivalent PDF→markdown converter) — datasheets/errata.
- **Toolchains** — `arm-none-eabi-gcc`/`clang`, `riscv64-unknown-elf-gcc`,
  CMake + Ninja; Rust stable with the target installed (`rustup target add
  thumbv7em-none-eabihf`), `cargo-binutils`, `probe-rs`, `defmt`.
- **Test** — Unity/CMock or CppUTest, GoogleTest/Catch2, `cargo test`, QEMU
  (`qemu-system-arm`/`riscv32`), Renode.
- **Flash/debug** — `openocd`, cross `gdb`, `probe-rs`, vendor ROM-bootloader
  tools (`dfu-util`, `stm32flash`, `esptool`), UART terminal (`picocom`).
- **Static analysis** — `cppcheck` (with the MISRA addon), `clang-tidy`,
  `cargo clippy`.
