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
# Replay a recorded log
cangraceful can0 work/<device>-can.log
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
- `lode/terminology.md` — CAN terms and higher-layer protocol abbreviations.
- `lode/toolchain.md` — CAN adapter, SocketCAN setup, bit rates used.

## Dependencies

- `can-utils` (`candump`/`cansend`/`cangraceful`), `ip` (iproute2) with
  SocketCAN, `tcpdump`/Wireshark, and a SocketCAN-compatible CAN adapter.
