Reference for Phase 5 / section Debug output of the workflow.

## UART printf

Retarget newlib's `_write` to a project UART:

```c
int _write(int fd, const void *buf, size_t len)
{
    (void)fd;
    const uint8_t *bytes = buf;
    for (size_t i = 0; i < len; ++i) {
        uart_putc(bytes[i]);
    }
    return (int)len;
}
```

Link small C programs with:

```text
--specs=nano.specs
```

Set the baud, framing, pins, and console capture command in `lode/toolchain.md`.
Bound or disable logging in release builds without changing application
behavior.

## Semihosting

Newlib semihosting uses:

```text
--specs=rdimon.specs
```

Initialize monitor handles before output:

```c
extern void initialise_monitor_handles(void);

int main(void)
{
    initialise_monitor_handles();
    puts("hello");
}
```

Semihosting hangs without a debugger, halts the core on I/O, and is unsuitable
for field firmware. Use only in a deliberately marked debug image.

## RTT

For C, include the SEGGER RTT source and place its control block in RAM:

```c
#include "SEGGER_RTT.h"

SEGGER_RTT_WriteString(0, "boot\n");
```

With OpenOCD, the shared dynamic-debugging reference has the session commands:
**[../../_shared/dynamic-debugging.md](../../_shared/dynamic-debugging.md)**.
Record the control-block address and RAM region in `lode/toolchain.md`.

Rust can use `rtt-target`:

```rust
let channels = rtt_target::rtt_init! {
    up: { 0: { size: 1024, mode: NoBlockSkip, name: "log" } }
};
channels.up.0.write_str("boot\n");
```

## Rust defmt

Use deferred formatting over RTT:

```toml
[dependencies]
defmt = "<version>"
defmt-rtt = "<version>"
```

```rust
#[defmt::panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! {
    defmt::error!("panic: {}", defmt::Debug2Format(info));
    loop {}
}

defmt::info!("boot");
```

Run with the probe:

```bash
probe-rs run --chip <chip> build/<image>.elf
```

Control verbosity through cargo features or `DEFMT_LOG`:

```bash
DEFMT_LOG=info probe-rs run --chip <chip> build/<image>.elf
```

Keep the same logging level and transport assumptions in the release test.

## Trade-offs

| Transport | Cost | Needs probe | Timing impact | Works in field |
|---|---|---:|---:|---:|
| UART | low | no | low to moderate | yes |
| Semihosting | low | yes | very high; halts core | no |
| RTT | low | yes | low | no |
| defmt/RTT | low | yes | very low formatting cost | no |

UART consumes pins and bandwidth but is the most portable field signal. RTT
needs a live debug probe and a RAM control block. Semihosting is for controlled
debugging only.

## Release discipline

Test the release build you flash. A debug-only `printf`, semihosting path, or
feature flag can change timing, memory layout, watchdog behavior, and linker
garbage collection. Record the exact image hash and logging configuration in
`lode/backups.md`.
