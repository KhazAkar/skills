Reference for Phase 3 / section Test before you flash of the workflow.

## HAL seams

Keep application logic independent of MMIO. In C, inject a function-pointer
table:

```c
struct hal {
    uint32_t (*ticks)(void);
    int (*uart_write)(const uint8_t *, size_t);
    void (*watchdog_kick)(void);
};

int app_step(const struct hal *hal, const uint8_t *input, size_t length);
```

The target supplies wrappers around the real HAL. Host tests supply fakes that
record calls and return deterministic values. Link-time substitution is also
valid when the seam is stable and the test build links fake object files.

In C++, use an abstract interface for runtime substitution:

```cpp
struct Clock {
  virtual ~Clock() = default;
  virtual uint32_t ticks() = 0;
};
```

For zero-overhead firmware, prefer a template policy:

```cpp
template<class Hal>
int app_step(Hal& hal, Span<const uint8_t> input);
```

Rust application code should depend on `embedded-hal` traits. Test with fake
implementations or `embedded-hal-mock`:

```rust
fn poll<S: embedded_hal::digital::InputPin>(pin: &mut S) -> bool {
    pin.is_high().unwrap_or(false)
}
```

## C unit tests

Unity/CMock with Ceedling keeps test, fake, and runner generation explicit:

```yaml
:paths:
  :test:
    - +:test/**
  :source:
    - src/**
  :include:
    - include/**
:plugins:
  :enabled:
    - cmock
```

```bash
ceedling test:all
ceedling test:unit:<module>
```

Use CMock for HAL calls and assert both return values and call ordering. Keep
hardware register tests separate from state-machine tests.

## C++ unit tests

CppUTest works well for small embedded codebases:

```bash
cmake -S . -B build-host -DBUILD_HOST_TESTS=ON
cmake --build build-host
ctest --test-dir build-host --output-on-failure
```

GoogleTest and Catch2 are also valid CMake host frameworks. Keep target
sources and host fakes in distinct targets so host-only libraries never enter
the firmware link.

## Rust unit tests

Let the crate be `no_std` on the target and `std` under `cargo test`:

```toml
[dev-dependencies]
embedded-hal-mock = "<version>"
```

```rust
#![cfg_attr(not(test), no_std)]

#[cfg(test)]
mod tests {
    #[test]
    fn parser_rejects_short_frame() {
        assert!(super::parse(&[0x01]).is_err());
    }
}
```

Run on the host target explicitly (`.cargo/config.toml` defaults to the thumb
target, which cannot run tests):

```bash
cargo test --target x86_64-unknown-linux-gnu
```

Use `cargo test` for pure logic and trait-driven peripherals; it cannot prove
that target MMIO addresses, interrupt vectors, or linker placement are right.

## Emulator checks

QEMU can exercise reset, vector, linker, and selected peripheral paths:

```bash
qemu-system-arm -M <board> -kernel build/<image>.elf \
  -nographic -semihosting-config enable=on,target=native
```

Useful board models include `lm3s6965evb` and `mps2-an385`. Board coverage is
limited: unsupported clocks, GPIO, ADC, timers, DMA, external memories, and
vendor-specific peripherals may be stubs or absent. Record every mismatch.

Renode lets a test script assemble a machine and observe peripherals:

```text
using sysbus
mach create
machine LoadPlatformDescription @platforms/cpus/cortex-m.repl
sysbus LoadELF @build/<image>.elf
start
```

Run a `.resc` file with `renode <file>.resc`. Renode/QEMU prove only modeled
behavior; neither substitutes for silicon timing, electrical levels, analog
signals, cache effects, or a real probe.

## On-target smoke test

The smallest real-board test must prove:

1. clock initialization and a known-good frequency;
2. UART or RTT hello output;
3. watchdog initialization and a main-loop kick;
4. a visible LED or GPIO heartbeat;
5. reset-cause capture at boot.

Capture the output and record board revision, probe, image hash, supply
voltage, and timeout. Do not add a test that depends on unavailable inventory.

## HIL boundary

Use hardware-in-the-loop only when Phase 0 inventory includes the board,
probe, power, and measurement equipment needed by the test. Keep the test
script and exact wiring in `lode/testing.md`.

| Level | Catches | Cannot catch |
|---|---|---|
| Host unit | logic, parsers, state machines, error paths | MMIO, vectors, timing, electrical faults |
| QEMU/Renode | boot shape, linker, modeled peripherals | unmodeled silicon, analog, cache, real timing |
| On-target smoke | clock, pins, output, watchdog, reset | broad behavior, rare races, system integration |
| HIL | wiring, timing, buses, power interactions | uninstrumented paths and unmeasured faults |

Each level must state what it cannot catch; a green host suite is not evidence
that flashing is safe.
