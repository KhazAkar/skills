Reference for Phase 2 / section Reproducible build of the workflow.

## Pin the toolchain

Record exact versions in `lode/build.md`, and make the version check part of
the documented build:

```bash
arm-none-eabi-gcc --version
arm-none-eabi-ld --version
rustc --version
cargo --version
```

Pin the GNU Arm release in the project bootstrap or container. Do not rely on
the host's default `arm-none-eabi-gcc`; require the expected major and minor
version:

```bash
arm-none-eabi-gcc --version | grep '<gcc-version>'
```

Pin Rust with `rust-toolchain.toml`:

```toml
[toolchain]
channel = "<stable-version>"
targets = [
  "thumbv7em-none-eabihf",
  "thumbv7m-none-eabi",
]
components = ["rust-src", "llvm-tools-preview"]
```

Keep SDK, CMSIS, HAL, PAC, linker scripts, and build tools in the same
revision-controlled dependency policy. Record host OS and build container
image when a release must be reproducible.

## CMake toolchain

Keep the target toolchain separate from the host compiler. This skeleton
intentionally uses a static-library `try_compile` so CMake never links a
host-style executable while configuring:

```cmake
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR cortex-m4)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(CMAKE_C_COMPILER arm-none-eabi-gcc)
set(CMAKE_CXX_COMPILER arm-none-eabi-g++)
set(CMAKE_ASM_COMPILER arm-none-eabi-gcc)
set(CMAKE_OBJCOPY arm-none-eabi-objcopy)
set(CMAKE_SIZE arm-none-eabi-size)

set(CMAKE_C_FLAGS_INIT
    "-mcpu=<cpu> -mthumb -mfloat-abi=<soft|softfp|hard>")
set(CMAKE_CXX_FLAGS_INIT
    "-mcpu=<cpu> -mthumb -mfloat-abi=<soft|softfp|hard>")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-T${CMAKE_SOURCE_DIR}/linker.ld")
```

Configure from a clean build directory:

```bash
cmake -S . -B build-target -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=cmake/<target>.cmake
cmake --build build-target
```

The `-mcpu`, `-mthumb`, and `-mfloat-abi` values must match the silicon and
FPU configuration. Copy them into `lode/build.md`; do not infer them from an
IDE project.

## Warnings and section garbage collection

Use one flags block as the baseline for C:

```text
-Wall -Wextra -Werror
-ffunction-sections -fdata-sections
-Wl,--gc-sections -Wl,-Map=<build>/<image>.map
```

For C++ add:

```text
-fno-exceptions -fno-rtti
```

Apply compile flags to C and C++ targets, and linker flags only at link time.
Add language and target-specific flags through the build system, not by
editing generated command lines. Treat an exception to `-Werror` as an ADR.

## GNU linker script

Start from the `lode/memory-map.md` and replace every placeholder. Reserve
bootloader sectors before setting application `ORIGIN`:

```ld
MEMORY
{
  FLASH (rx)  : ORIGIN = <flash-origin>, LENGTH = <flash-length>
  RAM   (rwx) : ORIGIN = <ram-origin>,   LENGTH = <ram-length>
}

_estack = ORIGIN(RAM) + LENGTH(RAM);

SECTIONS
{
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } > FLASH

  .text :
  {
    . = ALIGN(4);
    *(.text .text.*)
    *(.rodata .rodata.*)
    KEEP(*(.init))
    KEEP(*(.fini))
    . = ALIGN(4);
    _etext = .;
  } > FLASH

  _sidata = LOADADDR(.data);
  .data : AT(_etext)
  {
    . = ALIGN(4);
    _sdata = .;
    *(.data .data.*)
    . = ALIGN(4);
    _edata = .;
  } > RAM

  .bss :
  {
    . = ALIGN(4);
    _sbss = .;
    *(.bss .bss.*)
    *(COMMON)
    . = ALIGN(4);
    _ebss = .;
  } > RAM
}
```

Startup code copies `_sidata` to `_sdata` through `_edata` and clears
`_sbss` through `_ebss`. Check the map file for overflow and section placement.
Use `NOLOAD` for retained RAM only when reset behavior and backup power are
documented.

## Rust target setup

Provide the target memory description in `memory.x`:

```ld
MEMORY
{
  FLASH : ORIGIN = <flash-origin>, LENGTH = <flash-length>
  RAM   : ORIGIN = <ram-origin>,   LENGTH = <ram-length>
}
```

Configure cargo and the runner:

```toml
[build]
target = "<thumb-target>"

[target.<thumb-target>]
runner = "probe-rs run --chip <chip>"
rustflags = [
  "-C", "link-arg=-Tlink.x",
]
```

Use `cortex-m-rt` for the vector table and reset entry. Keep `memory.x` and
`.cargo/config.toml` in the repository. Build `#![no_std]` application crates
with a pinned target and an explicitly selected PAC/HAL version.

## Size and map review

```bash
arm-none-eabi-size -A build/<image>.elf
arm-none-eabi-nm --size-sort --print-size build/<image>.elf | tail -n 30
cargo size --release -- -A
```

Read the `.map` file from the largest sections first: `.text`, `.rodata`,
`.data`, and `.bss`. Then inspect the biggest symbols:

```bash
less build/<image>.map
arm-none-eabi-nm --size-sort build/<image>.elf | tail -n 30
```

Record flash/RAM totals, largest symbols, and remaining headroom in
`lode/build.md`. A size regression needs a measured reason, not a guess.

## Reproducibility check

Build twice from the same source, or build once from a fresh clone:

```bash
cmake --build build-target
cp build-target/<image>.bin work/image-1.bin
cmake --fresh -S . -B build-target -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=cmake/<target>.cmake
cmake --build build-target
sha256sum work/image-1.bin build-target/<image>.bin
```

For Rust, repeat with `cargo build --release` and hash the release `.bin`.
Remove timestamps, absolute paths, and generated host paths from output where
possible:

```text
-ffile-prefix-map=<checkout>=.
--remap-path-prefix <checkout>=.
```

If hashes differ, compare the map, section bytes, build IDs, timestamps, and
tool versions before declaring the build reproducible.
