# Analyze the dump (static)

Reference for Phase 4 of the workflow. Once a verified copy exists, never
touch the original backup for analysis — work on a copy.

## Cheap, deterministic triage first

```bash
cp backups/<device>-flash-<date>.bin work/<device>.bin
```

### `binwalk` — structure

Scan for embedded filesystems, compressed kernels, uImages, CPIO/SquashFS/JFFS2,
certificates, and known headers. Extract interesting regions to a working dir,
never into `backups/`:
```bash
binwalk work/<device>.bin
binwalk -e work/<device>.bin                # extracts to work/_<device>.bin.extracted/
binwalk -e --matryoshka work/<device>.bin   # recurse into nested containers
```
Log every signature hit and its offset in `lode/memory-map.md`.

### `strings` — meaning

Pull human-readable clues (version banners, build paths, URLs, keys, error
messages) and orient the search:
```bash
strings -n 6 work/<device>.bin > work/<device>.strings
strings -a -n 6 work/<device>.bin | grep -iE 'version|build|http|root|pass'
strings -tx work/<device>.bin                # with hex offsets
```

### `xxd` — exactly what bytes live where

Inspect raw bytes at known offsets (vectors, headers, magic strings) and
compare regions between dumps:
```bash
xxd work/<device>.bin | head -n 16                  # first bytes / vector table
xxd -s 0x0 -l 0x40 work/<device>.bin                # specific offset + length
# Apply a hex patch IN PLACE on a copy: redirecting stdout makes a sparse file
# missing the untouched firmware bytes. Patch the copy directly instead.
cp work/<device>.bin work/<device>.patched.bin
xxd -r patch.hex work/<device>.patched.bin
```

These three are complementary: `binwalk` finds *structure*, `strings` finds
*meaning*, `xxd` confirms *exactly* what bytes live where. Cross-reference any
finding against the datasheet register/memory map before drawing conclusions.
Record findings in `lode/memory-map.md` and `lode/boot-sequence.md`.

## Deeper static analysis

### Cross binutils (`objdump`/`readelf`/`nm`)

Fast symbol, section, and disassembly triage without loading a full decompiler.
Use the toolchain prefix matching the chip (e.g. `arm-none-eabi-`,
`aarch64-linux-gnu-`, `riscv64-unknown-elf-`, `mipsel-`):
```bash
arm-none-eabi-readelf -h -S -l work/<device>.elf            # headers, sections, segments
arm-none-eabi-nm -n work/<device>.elf | sort              # symbols, sorted by address
arm-none-eabi-objdump -d work/<device>.elf > work/<device>.disasm
# Raw blob with no ELF header — set the arch and base address explicitly:
arm-none-eabi-objdump -D -b binary -m arm -M force-thumb --adjust-vma=0x08000000 work/<device>.bin | head -n 200
```
If the blob is an ELF, prefer `readelf`/`nm` for ground truth; if it's a raw
flash dump, feed `objdump` the `-b binary -m <arch> --adjust-vma=<base>` so
addresses line up with the datasheet memory map. For Cortex-M (Thumb-only)
cores, add `-M force-thumb` so Thumb halfwords decode as Thumb, not ARM.

### Ghidra

The workhorse for non-trivial firmware. Import the image, set the
processor/language to match the chip, set the base address and define memory
regions from the datasheet map, then auto-analyze. Cross-reference the
decompiler against `lode/register-map.md`: label MMIO accesses, define structs
for peripheral register blocks, and rename functions by behavior.

For repeatable/automated work, use the headless analyzer:
```bash
analyzeHeadless work/ghidra-proj <proj> -import work/<device>.bin \
  -processor ARM:LE:32:v7 -loader BinaryLoader -loader-baseAddr 0x08000000 \
  -postScript annotate-peripherals.py
# Omit -deleteProject to keep results in work/ghidra-proj. Re-running with the
# same project name and -process <device>.bin (no -import) reanalyzes the
# existing domain file instead of importing a second copy.
```
Export labeled symbols back out so the lode register/symbol maps stay in sync.
