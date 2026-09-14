---
name: "firmware-reverse-engineering"
description: "Use this skill for firmware reverse-engineering work: inventory available hardware tools first, dump and back up target firmware before anything else, research datasheets/erratas (PDFs converted to markdown) to understand the hardware, and document the process with the existing lode-programming skill."
version: "1.2"
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
Reverse-engineer embedded/firmware targets safely and methodically. The skill
assumes the person running it owns the hardware they are working on and is
dumping/analyzing their own devices. The three pillars are, in strict order:

1. **Back up everything first.** Never mutate the only copy of a device, flash
   image, or dump. Create read-only backups of firmware, EEPROM, fuses, config,
   and device state before any read/analysis/write attempt.
2. **Research datasheets and errata.** Identify every silicon part (MCU, flash,
   PMIC, radio, sensor) and read the manufacturer datasheet and errata before
   interpreting the binary. Convert reference PDFs to markdown so they are
   greppable, then search them for registers, addresses, and errata notes.
3. **Document as you go with lode-programming.** Load and follow the existing
   **lode-programming** skill for the `lode/` folder, ADRs, and workflow. Do
   not redefine that structure here — extend it with firmware-specific files.

## When to Load
- Planning which read/analysis methods are feasible given available hardware
- Dumping or analyzing firmware from a device
- Identifying unknown chips, register maps, or boot sequences
- Researching datasheets/erratas for parts on a target board
- Mapping a binary to its hardware peripherals
- Setting up toolchains (disassemblers, emulators, JTAG/SWD/UART)
- Onboarding a new target into an existing reversing effort

## Phase 0: Inventory available hardware (prerequisite)
Before touching the device, find out which physical tools are available.
Available hardware determines what is feasible: a JTAG/SWD adapter enables
on-chip debug dumps; a logic analyzer enables bus capture; an oscilloscope
verifies power/reset sequencing; a soldering station enables rework and
fly-wires. Ask the user once and record the answers in `lode/toolchain.md`.

Ask at minimum about:

- **Programmer / debug probe** — JTAG adapter (with model name), SWD adapter,
  UART adapter, ISP/SPI flasher, test clip / programming foot
- **Soldering station** — iron and/or hot-air rework (for lifting parts,
  attaching fly wires, reworking footprints)
- **Multimeter** — continuity, voltage rails, identifying pull-ups/pull-downs
- **Logic analyzer** — capture bus traffic (UART, SPI, I2C, SWD/SWJ)
- **Oscilloscope** — power sequencing, reset/BOOT timing, clock presence
- **Other** — standalone chip programmer, microscope, UV/EEPROM eraser, etc.

Then:

- Map each planned step to a tool that is actually available.
- If a needed method lacks its tool, either source the tool or choose the
  next-best **non-invasive** read path. Record the choice as an ADR
  (using the lode-programming ADR template).
- Treat the inventory as a constraint on every later step: never assume a
  method is available without a tool to back it.

## Mandatory Workflow (in order)

### 1. Backup before all else
Before any operation that could read, write, or erase the target:

- **Identify the original artifact** (on-chip flash, external NOR/NAND, EEPROM,
  fuses, OTP, config pages, calibration data).
- **Create a read-only, checksummed backup** of every readable region into a
  separate `backups/` directory that is never written to again.
  - Record device identity, read method, programmer, voltage, and the command
    used. Use the lowest-invasive path that the Phase 0 hardware supports:
    - External flash: `flashrom -r backups/<device>-flash-<date>.bin && flashrom -v backups/<device>-flash-<date>.bin`
    - On-chip flash over JTAG/SWD via `openocd`, e.g.
      `openocd -f interface/<adapter>.cfg -f target/<chip>.cfg -c "init; halt; dump_image backups/<device>-flash-<date>.bin 0x08000000 0x100000; reset; shutdown"`
      then verify the size and checksum match the chip's expected flash size.
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
Load and follow the existing **lode-programming** skill for the `lode/` folder
structure, ADRs, and workflow — including its file-size limits, one-topic-per-
file rule, and ADR template. Do not redefine that structure here. Extend it with
firmware-specific files:

- `silicon-map.md` — parts on the board, their packages, and datasheet links.
- `register-map.md` — peripheral bases, MMIO regions, and known registers.
- `memory-map.md` — flash regions, RAM, EEPROM/fuses, vector/boot addresses.
- `boot-sequence.md` — reset path from entry point to first user code.
- `backups.md` — what was dumped, from where, with which command + checksum.
- `toolchain.md` — programmer, disassembler, emulator, scripts, versions, and
  the Phase 0 hardware inventory.

Write an ADR (using the lode-programming ADR template) for every non-obvious
decision (tool choice, read voltage, assumed reset vector, identification of a
part from a partial marking, a Phase 0 method chosen because the ideal tool
was unavailable).

### 4. Analyze the dump (static)
Once a verified copy exists, never touch the original backup for analysis —
work on a copy. Trips the binary with cheap, deterministic tools before
reaching for a disassembler/emulator:

- **`binwalk`** — scan for embedded filesystems, compressed kernels, uImages,
  CPIO/SquashFS/JFFS2, certificates, and known headers. Extract interesting
  regions to a working dir, never into `backups/`:
  ```bash
  cp backups/<device>-flash-<date>.bin work/<device>.bin
  binwalk work/<device>.bin
  binwalk -e work/<device>.bin          # extracts to work/_<device>.bin.extracted/
  binwalk -e --matryoshka work/<device>.bin   # recurse into nested containers
  ```
  Log every signature hit and its offset in `lode/memory-map.md`.

- **`xxd`** — inspect raw bytes at known offsets (vectors, headers, magic
  strings) and compare regions between dumps:
  ```bash
  xxd work/<device>.bin | head -n 16                  # first bytes / vector table
  xxd -s 0x0 -l 0x40 work/<device>.bin               # specific offset + length
  xxd -r patch.hex > work/<device>.patched.bin        # apply a hex patch
  ```

- **`strings`** — pull human-readable clues (version banners, build paths,
  URLs, keys, error messages) and orient the search:
  ```bash
  strings -n 6 work/<device>.bin > work/<device>.strings
  strings -a -n 6 work/<device>.bin | grep -iE 'version|build|http|root|pass'
  strings -tx work/<device>.bin                       # with hex offsets
  ```

These three are complementary: `binwalk` finds *structure*, `strings` finds
*meaning*, `xxd` confirms *exactly* what bytes live where. Cross-reference any
finding against the datasheet register/memory map before drawing conclusions.
Record findings in `lode/memory-map.md` and `lode/boot-sequence.md`.

For deeper static analysis, two more:

- **Cross binutils** (`objdump`/`readelf`/`nm`) — fast symbol, section, and
  disassembly triage without loading a full decompiler. Use the toolchain prefix
  matching the chip (e.g. `arm-none-eabi-`, `aarch64-linux-gnu-`,
  `riscv64-unknown-elf-`, `mipsel-`):
  ```bash
  arm-none-eabi-readelf -h -S -l work/<device>.elf            # headers, sections, segments
  arm-none-eabi-nm -n work/<device>.elf | sort              # symbols, sorted by address
  arm-none-eabi-objdump -d work/<device>.elf > work/<device>.disasm
  # Raw blob with no ELF header — set the arch and base address explicitly:
  arm-none-eabi-objdump -D -b binary -m arm --adjust-vma=0x08000000 work/<device>.bin | head -n 200
  ```
  If the blob is an ELF, prefer `readelf`/`nm` for ground truth; if it's a raw
  flash dump, feed `objdump` the `-b binary -m <arch> --adjust-vma=<base>` so
  addresses line up with the datasheet memory map.

- **Ghidra** — the workhorse for non-trivial firmware. Import the image, set the
  processor/language to match the chip, set the base address and define memory
  regions from the datasheet map, then auto-analyze. Cross-reference the
  decompiler against `lode/register-map.md`: label MMIO accesses, define
  structs for peripheral register blocks, and rename functions by behavior.
  For repeatable/automated work, use the headless analyzer:
  ```bash
  analyzeHeadless work/ghidra-proj <proj> -import work/<device>.bin \
    -processor ARM:LE:32:v7 -loader BaseAddressLoader -csim 0x08000000 \
    -postScript annotate-peripherals.py
  # Re-running with the same project name is incremental; commit results via:
  #   -deleteProject false ... ; results land in work/ghidra-proj
  ```
  Export labeled symbols back out so the lode register/symbol maps stay in sync.

### 5. Interact with the device (dynamic)
Static analysis tells you what the firmware *can* do; dynamic observation tells
you what it *does*. Always run dynamic steps against the backed-up image or a
spare chip; never mutate the only good copy.

- **`openocd` (JTAG/SWD) — beyond dumping.** Once the core is reachable, drive
  it through a session. Easiest path: start the openocd daemon and talk to it
  over its telnet command interface (port 4444) so you can iterate without
  relaunching:
  ```bash
  # Start the daemon against the Phase 0 adapter + chip
  openocd -f interface/<adapter>.cfg -f target/<chip>.cfg
  # In another shell, attach to the command interface
  telnet localhost 4444
  > reset init            # reset and stop the core at a known state
  > halt                  # stop the core (idempotent)
  > reg                   # dump all core registers
  > reg pc                # read just the program counter
  > reg pc 0x08000000     # set a register (e.g. point PC at flash base)
  > mdw 0x08000000 0x10   # read 16 words at an address
  > mww 0x40023800 0x1    # write a word to MMIO (per datasheet register map)
  > step                  # single-step one instruction
  > resume                # continue running
  > bp 0x08000100 2 hw    # set a hardware breakpoint
  > resume ; ... ; halt   # run to breakpoint, then inspect
  > flash info 0          # list flash bank details
  > flash write_image build/<device>.elf  ; flash verify_image build/<device>.elf
  > shutdown
  ```
  For printf-style output without a UART, use semihosting or RTT:
  ```bash
  openocd -f interface/<adapter>.cfg -f target/<chip>.cfg \
    -c "init; reset init; rtt setup work/<device>-rtt.log 0x20000000 0x1000; rtt start; reset run"
  # RTT logs stream to the host file while the target runs.
  ```
  Record the adapter, target config, and any register/MMIO writes you make in
  `lode/toolchain.md`; treat dynamic writes as a decision worth an ADR.

- **UART console — the cheapest live signal.** Most boards expose a UART
  (boot log, U-Boot shell, kernel panic, vendor shell). Identify the pins with
  a multimeter (GND = continuity to ground; TX = idle-high output; RX = input),
  then capture and interact:
  ```bash
  stty -F /dev/ttyUSB0 115200 cs8 -cstopb -parenb -ixon -ixoff   # raw 8N1
  picocom -b 115200 /dev/ttyUSB0            # interactive console (Ctrl-A Ctrl-X to quit)
  screen /dev/ttyUSB0 115200                # alternative terminal
  picocom -b 115200 /dev/ttyUSB0 | tee work/<device>-uart-boot.log   # capture boot log
  ```
  Common UART baud rates to try: 9600, 38400, 57600, 115200, 230400. Save raw
  boot output to `lode/boot-sequence.md` and note any shell/prompt strings in
  `lode/terminology.md`.

- **`gdb` over `openocd`.** Wire the openocd GDB server (port 3333 by
  default) to a cross GDB for source/symbol-level stepping:
  ```bash
  # openocd already running with its GDB server
  arm-none-eabi-gdb build/<device>.elf \
    -ex "target remote localhost:3333" \
    -ex "monitor reset halt" \
    -ex "break main" -ex "continue"
  ```

- **QEMU — run/step suspect code off the hardware.** For a position-independent
  ELF or a userland binary, use user-mode QEMU; for bare-metal/RTOS images, use
  system-mode QEMU with a matching machine and a serial console. Either way,
  attach GDB so you can set breakpoints and single-step without the board:
  ```bash
  # User mode (e.g. an ARM Linux ELF)
  qemu-arm -g 1234 work/<device>.elf
  arm-none-eabi-gdb work/<device>.elf -ex "target remote :1234"

  # System mode (bare-metal/RTOS blob at flash base)
  qemu-system-arm -M lm3s6965evb -kernel work/<device>.bin -serial stdio -S -gdb tcp::1234
  arm-none-eabi-gdb work/<device>.bin \
    -ex "target remote :1234" -ex "set $pc=0x08000000"
  ```
  If QEMU's machine model doesn't match the target, emulation still works for
  architecture-level triage of standalone functions; record the mismatch and
  its limitations as an ADR.

Record every dynamic session (commands issued, register/memory state, UART
output) in the matching lode file so the next session starts from current
truth, not memory.

## Safety Rules
- **Read before write.** Never write to a device you have not fully backed up.
- **Lowest safe voltage** for reads; document the voltage used.
- **Verify every dump** against the device immediately after reading.
- **Fuses/OTP/calibration are one-way** — back them up first and never re-flash
  without a known-good image.
- **Don't trust markings** as the sole identifier; cross-check package, pinout,
  and at least one datasheet register against the binary.
- **Errata change behavior.** Always read the errata, not just the datasheet.
- **Tools gate methods.** Don't plan a read/analysis method you lack the
  hardware to perform; fall back to a non-invasive path or source the tool.

## Datasheet/Errata Research Loop
1. Identify a part or a behavior you don't understand in the binary.
2. Locate the datasheet and errata PDFs.
3. Convert to markdown: `anydoc <file>.pdf`.
4. `grep` the markdown for registers, addresses, or errata keywords.
5. Record the finding in the matching lode file (`register-map.md`,
   `boot-sequence.md`, etc.) and cite the datasheet page/section.
6. Cross-reference the finding against the binary.

## Commands (Natural Language)
- *"Inventory my hardware"* → run Phase 0, record answers in
  `lode/toolchain.md`.
- *"Back up this device"* → dump every readable region, checksum, verify, log to
  `lode/backups.md`.
- *"Research <part>"* → fetch datasheet+errata, `anydoc` to markdown, grep for
  registers/errata, update `lode/silicon-map.md` and `lode/register-map.md`.
- *"What does the lode say about <peripheral>?"* → search lode files.
- *"Create ADR for <decision>"* → use the lode ADR template.

## Dependencies
- **lode-programming** — loaded and followed for the `lode/` documentation
  structure and ADRs.
- **anydoc** (or equivalent PDF→markdown converter) — to make datasheets/erratas
  greppable.
- **Backup tools** — `flashrom` for external flash; `openocd` for on-chip
  flash over JTAG/SWD (adapter depends on Phase 0 inventory).
- **Static analysis** — `binwalk` (signature scan/extract), `strings`
  (printable extraction), `xxd` (hex dump/patch); all standard on most
  reversing setups.
- **Cross toolchain** — `objdump`/`readelf`/`nm` and `gdb` matching the target
  arch (e.g. `arm-none-eabi-*`) for disassembly, symbols, and live debugging.
- **Ghidra** — headless or GUI decompiler/disassembler for non-trivial firmware.
- **UART terminal** — `picocom`/`screen` (+ `stty`) for console capture.
- **QEMU** — user- and system-mode emulation/stepping for off-hardware triage.
