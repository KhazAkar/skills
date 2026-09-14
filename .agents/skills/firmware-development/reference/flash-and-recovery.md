Reference for Phase 4 / section Flash safely of the workflow.

## Back up first

Follow **[../../_shared/backup.md](../../_shared/backup.md)** before replacing
an image already on the board. Keep the original dump read-only and record the
probe, target, voltage, command, and checksum in `lode/backups.md`.

## Flash and verify

OpenOCD:

```bash
openocd -f interface/<adapter>.cfg -f target/<chip>.cfg \
  -c "program build/<image>.elf verify reset exit"
```

Probe-rs:

```bash
probe-rs download --chip <chip> build/<image>.elf
probe-rs run --chip <chip> build/<image>.elf
```

Vendor ROM tools:

```bash
dfu-util -a <alt> -D build/<image>.bin
dfu-util -a <alt> -U work/readback.bin
stm32flash -w build/<image>.bin -v /dev/ttyUSB0
esptool.py --chip <chip> write_flash <offset> build/<image>.bin
esptool.py --chip <chip> verify_flash <offset> build/<image>.bin
```

The tool's verify operation is necessary but not sufficient: retain the exact
artifact and compute its hash:

```bash
sha256sum build/<image>.bin
printf '<sha256>  build/<image>.bin\n' >> lode/backups.md
```

Keep the last known-good image and its toolchain metadata. Never overwrite it
with a failed candidate.

## Bootloader ADR

Record these decisions before freezing the memory map:

```text
Status: Proposed
Context: <update, rollback, authenticity, and flash constraints>
Decision: single image or dual-slot A/B
Image header: {magic, version, size, CRC32/signature}
Activation: swap-on-boot or jump-to-active
Bootloader: ROM, custom, or MCUboot
Consequences: <space, update time, rollback, key management>
Alternatives: <rejected options and why>
```

Single-image designs are small but need a recovery path. A/B designs need
space for two images and an atomic validity marker. MCUboot is an OSS option
when its supported target and image format meet the requirements. The
bootloader owns the first flash sectors; reserve them in `MEMORY` and never
let application sections overlap them.

## Unbrick procedures

These operations can erase data or permanently change protection. Confirm the
backup and board identity first; use a spare board where possible.

### STM32

- Set `BOOT0` high and reset to enter the ROM bootloader.
- Use `stm32flash` over UART or the supported DFU transport.
- RDP level 1 to level 0 causes a mass erase.
- RDP level 2 is permanent; do not experiment on the only board.

### nRF52

```bash
nrfjprog --recover
probe-rs erase --chip <chip> --allow-erase-all
```

Both recovery paths erase everything, including application and settings.

### ESP32

- Hold `GPIO0` low while resetting to enter download mode.
- `esptool.py erase_flash` erases the complete flash; use only after backup.

### RP2040

- Hold `BOOTSEL` while connecting USB to expose UF2 mass storage.
- Copy the known-good `.uf2` only after confirming the board and image.

### AVR

Wrong fuse settings can lock out ISP. A high-voltage programmer may be
required to recover a fuse-locked part; plan one before changing fuses.

### Generic SWD/JTAG

Connect under reset when the application disables debug pins or immediately
crashes:

```text
reset_config srst_only connect_assert_srst
```

Use the adapter's reset wiring and the exact OpenOCD target configuration.

## Recovery record

Write `lode/recovery.md` before the first flash. Include boot pins, reset
sequence, voltage, cable, tool version, erase scope, image location, and the
data-loss warning. Test the path on a spare or sacrificial image before
claiming it is known-good.
