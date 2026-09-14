# CAN protocol reference

Reference for Controller Area Network (CAN) work during firmware reversing.
CAN is a multi-master, message-oriented serial bus used heavily in automotive
and industrial embedded systems. Devices ("nodes") transmit **frames** with an
**identifier** that also determines priority via **arbitration**. When reversing
a CAN node, you map frame IDs and payloads to firmware handlers and capture
live bus traffic.

## Official standards

- **ISO 11898-1:2024** — [ISO 11898-1:2024](https://www.iso.org/standard/86384.html) — data link layer and physical coding sublayer; specifies CAN CC (classic), CAN FD (flexible data rate), and CAN XL (extended data-field length) in one standard.
- **ISO 11898-2:2024** — [ISO 11898-2:2024](https://www.iso.org/standard/85120.html) — high-speed physical medium attachment (PMA) sublayer (CAN HS/FD/SIC/SIC XL transceivers).
- **ISO 11898-3:2006** — CAN low-speed/fault-tolerant (≤125 kbit/s); not recommended for new designs.
- **CAN in Automation (CiA)** — [https://www.can-cia.org/can-knowledge](https://www.can-cia.org/can-knowledge) — free knowledge base, guidelines (CiA 601 series), and higher-layer protocols (CANopen CC/FD).

ISO 11898-1:2024 superseded ISO 11898-1:2015 and now defines all three CAN
generations together.

## Why this matters for firmware RE

- CAN frame IDs are often compiled into firmware as constant tables (filter
  lists, mailbox configs) — good anchors for grep/Ghidra.
- Payload semantics (which byte means what) are usually a higher-layer
  protocol (CANopen, J1939, ISO-TP, UDS, or vendor-specific) defined in the
  firmware, not the CAN standard. Reverse the handler to recover it.
- A capture + a breakpoint on the CAN RX ISR ties a frame ID to a code path.

## CAN generations and frames

| Generation | ID width | Payload | Bit rate (nominal) | Standard |
|---|---|---|---|---|
| **CAN CC** (classic) | 11-bit (base) / 29-bit (extended) | 0–8 bytes | ≤1 Mbit/s | ISO 11898-1 |
| **CAN FD** | 11/29-bit | 0–64 bytes | ≤1 Mbit/s nominal, ≤5–8 Mbit/s data phase | ISO 11898-1:2024 |
| **CAN XL** | 11/29-bit | 0–2048 bytes | ≤1 Mbit/s nominal, ≤20 Mbit/s data phase | ISO 11898-1:2024 |

- **Arbitration**: lower numeric ID = higher priority. The identifier also
  serves as the message content tag (not a destination address).
- **Frame types**: Data, Remote (request a data frame), Error, Overload. Remote
  frames are deprecated in CAN FD/XL.
- **FD bit rate switching**: the arbitration phase runs at the nominal rate,
  then the data phase can switch to a higher rate — capture devices must
  support FD with BRS (bit rate switch) to decode correctly.

## Capture (live, via SocketCAN)

Most modern Linux kernels expose CAN interfaces through SocketCAN, which makes
them regular network interfaces — capture works with `can-utils`, `ip`,
`tcpdump`, and Wireshark just like Ethernet.

```bash
# Bring the CAN interface up at the target's nominal bit rate
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up
ip -s link show can0                  # confirm state, RX/TX counters

# Live terminal view of all frames
candump can0
# With timestamps and a log file
candump -ta can0 | tee work/<device>-can.log
# Compact (binary) log for later replay
candump -L can0 > work/<device>-can.cnd

# Capture to a pcap for Wireshark (SocketCAN = Linux cooked / can-raw)
sudo tcpdump -i can0 -w work/<device>-can.pcap
wireshark work/<device>-can.pcap
```

For CAN FD with bit rate switching, set both rates:
```bash
sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on
sudo ip link set can0 up
# candump must request FD decoding
candump -ta can0
```

For automotive targets you usually need a CAN adapter (e.g. USB-to-CAN,
SocketCAN-compatible like `can0`, or a logic-analyzer decode at the physical
layer). USBtin / PCAN / KVASER / LAWICEL-compatible adapters all create
SocketCAN interfaces on Linux.

## Send / fuzz (owner-side)

```bash
# Send a classic frame with an 11-bit ID and 8-byte payload
cansend can0 123#DEADBEEF01234567
# Send a CAN FD frame (FF flag, BRS, ESI)
cansend can0 123##1DEADBEEF01234567890ABCDEF
# Replay a recorded compact (candump -L) log; canplayer reads the .cnd file
canplayer -I work/<device>-can.cnd
# Random/brute IDs to discover listeners
for id in $(seq 0 0x7FF); do cansend can0 $(printf '%03X' $id)#00; done
```

## Analysis (offline)

```bash
# tshark: filter by CAN ID (classic 11-bit)
tshark -r work/<device>-can.pcap -Y 'can.id == 0x123'
# FD frame, by ID and format
tshark -r work/<device>-can.pcap -Y 'canfd.id == 0x123'
# Dump a frame in hex
tshark -r work/<device>-can.pcap -x -c 1
```

## Craft / send / fuzz with scapy

`scapy` supports CAN via the `CAN` layer (Linux SocketCAN), so you can build,
send, and sniff frames in Python — useful for targeted fuzzing of a frame ID
or replaying a captured payload with modifications.

```python
from scapy.all import *

# Send a classic 11-bit-ID data frame (8-byte payload)
frame = CAN(identifier=0x123, length=8, data=b"\xde\xad\xbe\xef\x01\x23\x45\x67")
sendp(frame, iface="can0")

# 29-bit extended ID (set the named 'extended' flag)
ext = CAN(identifier=0x18DAF110, flags='extended', length=8, data=b"\x02\x10\x00\x00\x00\x00\x00\x00")
sendp(ext, iface="can0")

# Sniff for a short window and print matching frames
pkts = sniff(iface="can0", timeout=5,
             lfilter=lambda p: p.haslayer(CAN) and p[CAN].identifier == 0x123)
for p in pkts:
    p.show()

# Replay a captured SocketCAN pcap with a modified payload
pkts = rdpcap("work/<device>-can.pcap")
for p in pkts:
    if p.haslayer(CAN):
        p[CAN].data = b"\xAA\xBB\xCC\xDD\xEE\xFF\x00\x11"[: p[CAN].length]
        sendp(p, iface="can0")

# Fuzz: walk a range of IDs with a fixed payload to discover listeners
for ident in range(0x700, 0x7FF):
    sendp(CAN(identifier=ident, length=1, data=b"\x00"), iface="can0")
```

For CAN FD, use the `CANFD` class (it sets the `fd_frame` fd_flag) with a
longer `data`; for bit-rate-switch add the named `bit_rate_switch` fd_flag:
```python
fd = CANFD(identifier=0x123, length=64, data=b"\x00"*64, fd_flags='fd_frame+bit_rate_switch')
sendp(fd, iface="can0")
```
Use `cansend`/`candump` for ad-hoc work and `scapy` for scripted fuzzing and
payload mutation.

## Higher-layer protocols: ISO-TP and UDS

CAN frames carry at most 8 bytes (CAN CC) / 64 (CAN FD) / 2048 (CAN XL).
Diagnostics and flashing need far more, so two standards layer on top.

### ISO-TP (ISO 15765-2, DoCAN transport)

A transport protocol that segments a long message into multiple CAN frames with
a small Protocol Control Information (PCI) header.

Official standards:
- **ISO 15765-2:2016** — [ISO 15765-2:2016](https://www.iso.org/standard/66574.html) — transport protocol and network layer services (the widely-deployed edition).
- **ISO 15765-2:2024** — current edition (DoCAN, supersedes 2016).
- **ISO 15765-1** — general information and use cases.

Frame types (PCI first nibble = type):

| Type | PCI nibble | Use |
|---|---|---|
| Single Frame (SF) | 0 | Payload ≤ 7 bytes (normal addressing). |
| First Frame (FF) | 1 | Start of a multi-frame message; carries total length. |
| Consecutive Frame (CF) | 2 | Subsequent segments; 4-bit rolling SN. |
| Flow Control (FC) | 3 | Receiver pacing: FS flag, Block Size, STmin. |

- A multi-frame transfer: FF → receiver sends FC → sender streams CF blocks.
- Max payload 4095 bytes (classic) / 2^32-1 (2016+ escape / CAN FD).
- Addressing: normal (CAN ID only) vs extended (first data byte = target
  address). Six addressing modes are defined.

Why it matters for RE: the ISO-TP state machine in firmware (FF/CF/FC
handling, STmin timers) is a fixed, well-known structure — once you find the
CAN IDs used for request/response, the segmenter/desegmenter code is a strong
anchor. Flash downloads ride on ISO-TP.

Linux exposes ISO-TP as a socket family (`PF_CAN`, `SOCK_DGRAM`), so you can
send/receive whole messages without manual segmentation:
```bash
# Open an ISO-TP socket (request CAN ID 0x7E0, response 0x7E8)
# isotpsend reads the payload from STDIN, not positional args.
printf '22F190' | isotpsend -s 0x7E0 -d 0x7E8 can0   # UDS ReadDataByIdentifier (DID 0xF190 = VIN)
isotprecv -s 0x7E0 -d 0x7E8 can0
# Sniff ISO-TP messages (reassembled) alongside raw CAN
isotpsniffer -s 0x7E0 -d 0x7E8 can0
```

scapy also has an ISO-TP layer (`ISOTP`) for scripted sends/mutations.

### UDS (Unified Diagnostic Services, ISO 14229)

The application-layer diagnostic protocol; runs over ISO-TP/DoCAN on CAN and
over DoIP on Ethernet. A tester sends a request, the ECU responds positive
(`SID | 0x40`) or negative (`0x7F`, with a negative response code).

Official standards:
- **ISO 14229-1:2020** (Application layer) — [ISO 14229-1:2020](https://www.iso.org/standard/72439.html) — the data-link-independent core.
- **ISO 14229-1:2026** — forthcoming edition — [ISO 14229-1](https://www.iso.org/standard/87962.html)
- **ISO 14229-3** — UDS on CAN (replaces the old ISO 15765-3).
- **ISO 14229-5** — UDS on IP (DoIP application layer).

Key services (SID = Service ID, first request byte):

| SID | Service | RE note |
|---|---|---|
| 0x10 | DiagnosticSessionControl | Extended/programming sessions unlock more services. |
| 0x11 | ECUReset | Reset types; a soft reboot you can trigger. |
| 0x22 | ReadDataByIdentifier | Read DIDs — VIN, ECU part number, software version, fingerprints. |
| 0x23 | ReadMemoryByAddress | Read arbitrary memory if the ECU allows it (huge for RE). |
| 0x27 | SecurityAccess | Seed/key challenge-response; reversing the key algo is often the goal. |
| 0x31 | RoutineControl | Start/stop routines (factory tests, erase, flash). |
| 0x34/0x36/0x37 | RequestDownload/TransferData/RequestTransferExit | The flash-download sequence. |
| 0x2E | WriteDataByIdentifier | Write DIDs (config, calibration). |
| 0x14 | ClearDiagnosticInformation | Clear DTCs. |
| 0x19 | ReadDTCInformation | Read diagnostic trouble codes. |

Negative Response Codes (NRC) to know: `0x10` generalReject, `0x11` serviceNotSupported,
`0x22` conditionsNotCorrect, `0x24` requestSequenceError, `0x31` requestOutOfRange,
`0x33` securityAccessDenied, `0x35` invalidKey, `0x36` exceededNumberOfAttempts,
`0x72` generalProgrammingFailure, `0x78` responsePending (request correctly received,
response is still being prepared — keep waiting).

Why it matters for RE: UDS over CAN is the standard path to read memory
(0x23), pull firmware fingerprints (0x22 DIDs), and trigger the flash
sequence (0x34/0x36/0x37). `0x27` SecurityAccess is often the lock on a
programming session — reversing the seed/key algorithm is a common RE goal
and a good ADR candidate. The handler table (SID → function) is a fixed
structure in firmware.

Send UDS over ISO-TP with `isotpsend`:
```bash
# Enter extended diagnostic session
printf '1003' | isotpsend -s 0x7E0 -d 0x7E8 can0
# Read VIN (DID 0xF190)
printf '22F190' | isotpsend -s 0x7E0 -d 0x7E8 can0
# Read ECU identification (DID 0xF810)
printf '22F810' | isotpsend -s 0x7E0 -d 0x7E8 can0
# Request SecurityAccess seed (subfunction 0x01)
printf '2701' | isotpsend -s 0x7E0 -d 0x7E8 can0
```

`pyuds` / `udsonstan` libraries script the full UDS session over ISO-TP for
fuzzing and automated reads; capture with `candump`/Wireshark and correlate
SID responses to the firmware handler.

## Cross-reference with firmware

- Find CAN ID constants in the dump (11-bit IDs as 16-bit aligned values, 29-bit
  IDs as 32-bit) and grep the dump; mailbox/filter tables are good anchors.
- In Ghidra, label the CAN peripheral's MMIO registers from the datasheet and
  trace the RX ISR → filter check → handler table.
- Recover the higher-layer protocol (CANopen object dictionary, J1939 PGN,
  ISO-TP segmentation, UDS service IDs, or vendor-specific) from the handler.

## Record in the lode

- `lode/can.md` — bus generation (CC/FD/XL), bit rates, ID table, payload
  semantics per ID, captured frames, and mapped code paths.
- `lode/diagnostics.md` — ISO-TP request/response IDs, UDS SIDs supported,
  SecurityAccess seed/key behavior, and flash sequence.
- `lode/terminology.md` — CAN terms and higher-layer protocol abbreviations.
- `lode/toolchain.md` — CAN adapter, SocketCAN setup, bit rates used.

## Dependencies

- `can-utils` (`candump`/`cansend`/`canplayer`), `ip` (iproute2) with
  SocketCAN, `tcpdump`/Wireshark, `scapy` (CAN layer), and a SocketCAN-
  compatible CAN adapter.
