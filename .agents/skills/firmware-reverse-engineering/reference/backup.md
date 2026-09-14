# Backup before all else

Reference for Phase 1 of the workflow. Before any operation that could read,
write, or erase the target, create a read-only, checksummed backup of every
readable region.

## Identify the original artifact

- On-chip flash, external NOR/NAND, EEPROM, fuses, OTP, config pages,
  calibration data.
- Record device identity, read method, programmer, voltage, and the command
  used.

## Create a read-only backup

Use the lowest-invasive path that the Phase 0 hardware supports. Work into a
separate `backups/` directory that is never written to again.

External flash:
```bash
flashrom -r backups/<device>-flash-<date>.bin && flashrom -v backups/<device>-flash-<date>.bin
```

On-chip flash over JTAG/SWD via `openocd`:
```bash
# <flash-base> and <flash-size> come from the chip datasheet and `flash info 0`; never assume STM32 geometry.
# A correct file size and checksum only prove the dump is internally consistent; they do not prove it
# matches the chip. Read protection, transport errors, or a wrong region can still yield a full-sized
# bad dump. Verify the bytes against the device before any later write. Run dump_image and verify_image
# in ONE OpenOCD session with a single init; halt so the core never runs between dumping and verifying:
openocd -f interface/<adapter>.cfg -f target/<chip>.cfg -c "init; halt; dump_image backups/<device>-flash-<date>.bin <flash-base> <flash-size>; verify_image backups/<device>-flash-<date>.bin <flash-base> bin; shutdown"
# Abort before any live-device mutation if `verify_image` reports a mismatch. As an independent
# cross-check you may also dump a second time into a different file and compare byte-for-byte.
sha256sum backups/<device>-flash-<date>.bin
ls -l backups/<device>-flash-<date>.bin
```

Store a SHA-256 alongside every dump:
```bash
sha256sum backups/*.bin > backups/SHA256SUMS
```

## Preserve fuses/OTP/calibration separately

These are often one-way writes and the backup is the only way back. Read them
into separate files with the same checksum step above, never into the same file
as flash.

## Confirm restorable

Dry-run restore against a spare chip or an emulated target before touching the
live device further. Work only from copies after this point; treat the
original backups as write-once evidence.
