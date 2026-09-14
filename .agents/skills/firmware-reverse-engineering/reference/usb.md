# USB protocol reference

Reference for USB work during firmware reversing. USB is layered: a physical
device exposes one or more **configurations**, each with one or more
**interfaces**, each with a set of **endpoints**. Transactions move over
**pipes** bound to endpoints, and each endpoint has a **transfer type** and a
**direction**. When reversing a USB device, you are mapping descriptors to
behavior and capturing traffic on the bus.

## Official standards

- **USB 2.0 Specification** (Revision 2.0; the canonical spec for Low/Full/High
  speed devices) — [USB-IF document library](https://www.usb.org/document-library/usb-20-specification)
- **USB 3.x / USB4** specifications and class specs — [USB-IF document library index](https://www.usb.org/documents?search=&tid_2%5B0%5D=40&items_per_page=50)
- **USB Type-C / USB Power Delivery** — [USB-IF documents](https://www.usb.org/documents) (filter by topic)
- **USB class codes** (registry of `bDeviceClass`/`bInterfaceClass` values) — [USB-IF class codes](https://www.usb.org/defined-class-codes)

When a section below says "per the spec", it means the USB 2.0 spec unless
noted; USB 3.x adds SuperSpeed transfer and a dual-bus model on top of USB 2.0.

## Why this matters for firmware RE

- Descriptors in firmware tell you what the device *claims* to be (VID/PID,
  class, endpoints, max packet size) — often before you ever capture traffic.
- Endpoint layout tells you which pipes carry control, bulk, interrupt, or
  isochronous traffic, so you know where the interesting data flows.
- Capture ties firmware code paths to actual wire traffic, so a `strings`/Ghidra
  hit maps to a real URB on the bus.

## Speeds and modes

- **Speeds** — Low (1.5 Mbps), Full (12 Mbps), High (480 Mbps), SuperSpeed (5
  Gbps), SuperSpeed+ (10 Gbps). The first three share the USB 2.0 model;
  SuperSpeed is a different physical layer with separate RX/TX lanes and no
  polling. Most embedded targets are Low/Full/High.
- **Device modes**
  - **Host** — controls the bus, enumerates devices, schedules transactions.
  - **Device (peripheral)** — the target under reversing; responds to SETUP
    requests and services endpoints.
  - **OTG / Dual-role** — can switch host/device; negotiated over the ID pin and
    HNP/SRP. Common on MCUs with a USB OTG peripheral.
  - Some chips are **Host-only** or **Device-only**; check the datasheet's USB
    peripheral section before assuming dual-role.

## Descriptors (the static map)

Read these from the firmware first; they often live as constant tables in
flash. Hierarchy:

- **Device** — `idVendor` (VID), `idProduct` (PID), `bcdDevice` (often a
  firmware-version encoded in BCD), `bcdUSB` (USB version), `bMaxPacketSize0`
  (EP0 max packet: 8/64 for Low/Full, 512 for SuperSpeed), `bNumConfigurations`.
- **Configuration** — `bNumInterfaces`, power draw (`bMaxPower` in 2 mA units,
  so `0x32` = 100 mA), `bmAttributes` (self-powered bit 6, remote-wakeup bit 5).
- **Interface** — `bInterfaceNumber`, `bAlternateSetting`, class/subclass/protocol
  (may be 0xFF = vendor-specific).
- **Endpoint** — `bEndpointAddress` (number + direction: bit 7 = IN),
  `bmAttributes` (transfer type in bits 0:1), `wMaxPacketSize`, `bInterval`.
- **String** — indexed, language-tagged; `iManufacturer`, `iProduct`,
  `iSerialNumber` point here. Often leaks vendor/firmware-version strings.

Class codes to watch for in `bDeviceClass`/`bInterfaceClass`:

- `0x00` — defined at interface level (most common).
- `0x08` — Mass Storage (MSC). Look for SCSI commands wrapped in BOT/CBI.
- `0x03` — HID. Reports, report descriptors; `strings`/Ghidra hits here map to
  report parsing.
- `0x0A` / `0x02` — CDC (USB serial/console, often a vendor shell or flash
  download channel).
- `0xFF` — Vendor-specific. Custom protocols; the interesting case for RE.

## Transfer types (per endpoint)

| Type | bmAttributes | Use | RE note |
|---|---|---|---|
| **Control** | 0x00 | EP0, SETUP requests, descriptors | Enumeration + class requests; structured and well-defined. |
| **Isochronous** | 0x01 | Streaming, no retransmit (audio/video) | Hard to fuzz/capture cleanly; bounded latency, lossy. |
| **Bulk** | 0x02 | Large, reliable data (MSC, CDC data) | Where the payload lives; grep firmware for the EP size and toggle handling. |
| **Interrupt** | 0x03 | Small, polled (HID, notifications) | `bInterval` sets poll rate; often the control/status channel. |

## Standard and class requests (EP0 control)

Standard SETUP requests (per USB 2.0 spec, table 9-4): `GET_DESCRIPTOR`,
`SET_ADDRESS`, `SET_CONFIGURATION`, `GET_STATUS`, `CLEAR_FEATURE`, `SET_FEATURE`,
`SET_INTERFACE`, `SYNCH_FRAME`.

Class requests map to behavior:
- HID — `GET_REPORT`, `SET_REPORT`, `GET_IDLE`, `SET_IDLE`, `GET_PROTOCOL`.
- MSC — `BBB_RESET` (`0xFF21`), `GET_MAX_LUN`.
- CDC — `SET_LINE_CODING`, `GET_LINE_CODING`, `SET_CONTROL_LINE_STATE`.

A class request handler in firmware is a good anchor point for RE.

## Enumeration (what the host does)

1. Device connect → host detects pull-up/speed.
2. Host issues `SET_ADDRESS` (default 0 → assigned).
3. Host issues `GET_DESCRIPTOR(Device)`.
4. Host reads configurations and selects one (`SET_CONFIGURATION`).
5. Host binds drivers per interface; class requests flow.

When reversing, watch enumeration first — most protocol negotiation happens
here and reveals endpoint layout.

## Capture (the dynamic map)

### Identify the device
```bash
lsusb                      # list all devices, VID:PID
lsusb -v -d <VID>:<PID>     # full descriptor tree for one device
lsusb -t                   # tree view with speed and driver binding
```
`lsusb -v` output is the ground truth for what the device advertises; compare
it against the descriptor tables you found statically in the dump.

### Capture traffic with usbmon

`usbmon` exposes USB traffic as a debugfs bus that Wireshark can read live or
from a file:
```bash
sudo modprobe usbmon
ls /sys/kernel/debug/usb/usbmon/      # 0t (all), 1t..Nt (per bus)
# Live capture in Wireshark: select usbmonN for the device's bus number
# Command-line capture to a pcap:
sudo cat /sys/kernel/debug/usb/usbmon/0t > work/<device>-usb.pcap &
# Capture, then replay in Wireshark:
wireshark work/<device>-usb.pcap
```

For targeted capture, find the bus number from `lsusb` (the `Bus 001` line →
`usbmon1`), then filter Wireshark by `usb.device_address == <addr>` after
`SET_ADDRESS`.

### Replay / fuzz with `usbredirparser` or a script
For owner-side protocol RE, replay captured URBs and watch the device's
response on the UART/console captured in `reference/dynamic-debugging.md`.
Record endpoint, transfer type, and payload for each interesting transaction
in `lode/usb.md`.

## Cross-reference with firmware

- Find descriptor tables in the dump (grep for the VID/PID bytes, the USB
  signature, or known string descriptors) and record them in `lode/usb.md`.
- In Ghidra, label the USB peripheral's MMIO registers from the datasheet and
  trace which code builds SETUP responses vs. services bulk endpoints.
- Map each captured transaction back to a code path: the function that reads a
  particular OUT endpoint is the request handler for that channel.

## Record in the lode

- `lode/usb.md` — VID/PID, speeds/modes, descriptor dump, endpoint table,
  class, captured transactions, and the code path each maps to.
- `lode/terminology.md` — USB terms and class abbreviations used on the target.
- `lode/toolchain.md` — `usbmon`/Wireshark setup and any USB capture hardware.

## Dependencies

- `lsusb` (usbutils), `usbmon` + `tcpdump`/Wireshark, and optionally a USB
  analyzer or USB-serial/SPI bridge for the physical side.
