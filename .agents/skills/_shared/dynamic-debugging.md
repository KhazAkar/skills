# Interact with the device (dynamic)

Reference for Phase 5 of the workflow. Static analysis tells you what the
firmware *can* do; dynamic observation tells you what it *does*. Always run
dynamic steps against the backed-up image or a spare chip; never mutate the
only good copy.

## `openocd` (JTAG/SWD) — beyond dumping

Once the core is reachable, drive it through a session. Easiest path: start
the openocd daemon and talk to it over its telnet command interface (port 4444)
so you can iterate without relaunching:
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
  -c "init; reset init; rtt setup 0x20000000 0x1000 \"RTT\"; rtt start; rtt server 0 9090; reset run"
# rtt setup takes <control-block-address> <size> <id>, NOT a log path.
# `rtt server 0 9090` exposes channel 0 on TCP 9090; capture it on the host:
#   nc localhost 9090 | tee work/<device>-rtt.log
```

Record the adapter, target config, and any register/MMIO writes you make in
`lode/toolchain.md`; treat dynamic writes as a decision worth an ADR.

## UART console — the cheapest live signal

Most boards expose a UART (boot log, U-Boot shell, kernel panic, vendor shell).
Identify the pins with a multimeter (GND = continuity to ground; TX = idle-high
output; RX = input), then capture and interact:
```bash
stty -F /dev/ttyUSB0 115200 cs8 -cstopb -parenb -ixon -ixoff   # raw 8N1
picocom -b 115200 /dev/ttyUSB0            # interactive console (Ctrl-A Ctrl-X to quit)
screen /dev/ttyUSB0 115200                # alternative terminal
picocom -b 115200 /dev/ttyUSB0 | tee work/<device>-uart-boot.log   # capture boot log
```
Common UART baud rates to try: 9600, 38400, 57600, 115200, 230400. Save raw
boot output to `lode/boot-sequence.md` and note any shell/prompt strings in
`lode/terminology.md`.

## `gdb` over `openocd`

Wire the openocd GDB server (port 3333 by default) to a cross GDB for
source/symbol-level stepping:
```bash
# openocd already running with its GDB server
arm-none-eabi-gdb build/<device>.elf \
  -ex "target remote localhost:3333" \
  -ex "monitor reset halt" \
  -ex "break main" -ex "continue"
```

## QEMU — run/step suspect code off the hardware

For a position-independent ELF or a userland binary, use user-mode QEMU; for
bare-metal/RTOS images, use system-mode QEMU with a matching machine and a
serial console. Either way, attach GDB so you can set breakpoints and
single-step without the board:
```bash
# User mode (e.g. an ARM Linux ELF)
qemu-arm -g 1234 work/<device>.elf
arm-none-eabi-gdb work/<device>.elf -ex "target remote :1234"

# System mode (bare-metal/RTOS blob). lm3s6965evb maps flash at 0x00000000,
# so do NOT force $pc to an STM32-style 0x08000000—let the reset vector run.
qemu-system-arm -M lm3s6965evb -kernel work/<device>.bin -serial stdio -S -gdb tcp::1234
arm-none-eabi-gdb work/<device>.bin \
  -ex "target remote :1234"
# If you need a flash base of 0x08000000, pick a QEMU machine whose memory map
# places flash there (or load via -device/loader) instead of overriding $pc.
```
If QEMU's machine model doesn't match the target, emulation still works for
architecture-level triage of standalone functions; record the mismatch and its
limitations as an ADR.

Record every dynamic session (commands issued, register/memory state, UART
output) in the matching lode file so the next session starts from current
truth, not memory.
