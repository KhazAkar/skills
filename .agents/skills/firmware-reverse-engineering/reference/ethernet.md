# Ethernet protocol reference

Reference for Ethernet work during firmware reversing. Most embedded
Ethernet targets expose an Ethernet MAC + PHY (often RMII/MII to an external
PHY, or integrated on the MCU). Reversing means mapping frames to firmware
handlers and capturing live traffic.

## Official standards

- **IEEE 802.3 (Ethernet)** — [IEEE Standard for Ethernet](https://standards.ieee.org/ieee/802.3/10422/) — defines the MAC, framing, CSMA/CD, and physical layers for 1 Mb/s to 400 Gb/s.
- **IEEE 802.3 Working Group** — [https://www.ieee802.org/3/](https://www.ieee802.org/3/) — current revisions and amendments (free download links from IEEE GET program).
- **IEEE 802.1Q** (VLAN tagging) — covered in the IEEE 802.1 working group pages.
- **RFC 826** (ARP) — [https://www.rfc-editor.org/rfc/rfc826](https://www.rfc-editor.org/rfc/rfc826).

The most recent consolidated base document is IEEE 802.3-2022.

## Automotive Ethernet

Automotive Ethernet uses **single-pair Ethernet (SPE)** PHYs optimized for
vehicle environments — full-duplex over a single unshielded/shielded twisted
pair, lower weight and cost than 100BASE-TX, and EMI-tuned for cars. The MAC/
framing is still IEEE 802.3; only the PHY changes, so everything in the frame
structure and capture sections above still applies.

Automotive Ethernet PHYs (all IEEE 802.3 amendments):

| PHY | IEEE amendment | Rate | Pair / topology | RE note |
|---|---|---|---|---|
| 100BASE-T1 | IEEE 802.3bw-2015 | 100 Mb/s | 1 pair, point-to-point, full-duplex, PAM3 (4B3B/3B2T) | The most common automotive Ethernet PHY; 15 m type A / 40 m type B. |
| 1000BASE-T1 | IEEE 802.3bp-2016 | 1 Gb/s | 1 pair, point-to-point, full-duplex, PAM3 | Requires shielded pair; 15 m type A / 40 m type B. |
| 10BASE-T1S | IEEE 802.3cg-2019 | 10 Mb/s | 1 pair, **multi-drop** bus (or point-to-point) | Multi-drop can replace CAN/CAN-FD/LIN in simple sensor/actuator nets. |
| 10BASE-T1L | IEEE 802.3cg-2019 | 10 Mb/s | 1 pair, point-to-point, up to 1000 m, PoDL | Industrial/long-reach; Ethernet-APL variant for hazardous areas. |
| 2.5/5/10GBASE-T1 | IEEE 802.3ch-2020 | 2.5/5/10 Gb/s | 1 pair, point-to-point, PAM4 | Multi-gig automotive (ADAS, infotainment). |
| 25GBASE-T1 | IEEE 802.3cy-2023 | 25 Gb/s | 1 pair, point-to-point, PAM4 | Latest multi-gig. |

Official standards:
- **100BASE-T1** — [IEEE 802.3bw](https://standards.ieee.org/ieee/802.3bw/5969/)
- **1000BASE-T1** — [IEEE 802.3bp](https://standards.ieee.org/ieee/802.3bp/5925/)
- **10BASE-T1S / 10BASE-T1L** — IEEE 802.3cg (10 Mb/s SPE + PoDL)
- **Multi-gig (2.5/5/10GBASE-T1)** — IEEE 802.3ch
- **OPEN Alliance SIG** — [https://www.opensig.org](https://www.opensig.org) — automotive Ethernet specifications and compliance (TC8, TC9, TC10) that layer on top of the IEEE PHYs.

### Capturing automotive Ethernet

- 100BASE-T1 / 1000BASE-T1 are **not** capturable with a standard RJ45 NIC.
  You need a 100BASE-T1 / 1000BASE-T1 media converter or a capture probe
  (e.g. an OPEN Alliance TC8-compliant tap, or a dual-PHY converter to
  100BASE-TX) that exposes a standard Ethernet interface to `tcpdump`/Wireshark.
- Once converted, capture and `scapy` work exactly as in the standard sections
  below — the on-wire frames are normal Ethernet.
- For a non-intrusive tap, place the media converter in-line between two ECUs
  and mirror to a capture port; record the setup in `lode/toolchain.md`.

### Why this matters for automotive firmware RE

- An automotive ECU often bridges CAN and Ethernet (a gateway ECU): a single
  firmware image may carry **both** a CAN stack and an automotive-Ethernet
  stack (AVB/TSN, SOME/IP, DoIP). Cross-reference with `reference/can.md`.
- Higher-layer automotive protocols on top of Ethernet to look for:
  **SOME/IP** (service-oriented middleware, often on UDP/TCP 30490+),
  **DoIP** (Diagnostics over IP, ISO 13400, TCP 13400), **AVB/TSN**
  (IEEE 802.1BA / 802.1Qav/qbv), and vendor-specific UDP.
- The PHY config (master/slave, link mode) is often a few MDIO registers in the
  firmware; grep for the PHY ID (OUI) and the 100/1000BASE-T1 clause numbers
  to find the PHY init code.

### Higher-layer protocols: SOME/IP and DoIP

The two most common application-layer protocols on top of automotive Ethernet,
and both worth reversing when a gateway ECU is the target.

#### SOME/IP (Scalable service-Oriented MiddlewarE over IP)

A serialization/RPC + publish-subscribe middleware from AUTOSAR. Application
method/event traffic runs over UDP or TCP on the per-service port advertised
by SOME/IP-SD (there is no universal default application port); service
discovery (SOME/IP-SD) runs on UDP port 30490 (multicast
224.224.224.245:30490 by default).

Official standards:
- **SOME/IP Protocol Specification** (AUTOSAR Foundation, PRS_SOMEIPProtocol) — [AUTOSAR PRS_SOMEIPProtocol (R23-11)](https://www.autosar.org/fileadmin/standards/R23-11/FO/AUTOSAR_FO_PRS_SOMEIPProtocol.pdf)
- **SOME/IP-SD (Service Discovery)** — AUTOSAR PRS_SOMEIPServiceDiscoveryProtocol
- **AUTOSAR Foundation** landing — [https://www.autosar.org/standards/foundation/](https://www.autosar.org/standards/foundation/)

Wire format (header is 16 bytes, big-endian):
```
| Message ID (Service ID 16 + Method/Event ID 16) | Length 32 |
| Client ID 16 | Session ID 16 |
| Protocol Version 8 | Interface Version 8 | Message Type 8 | Return Code 8 |
| Payload ... |
```
- **Message Type** distinguishes REQUEST (0x00), REQUEST_NO_RETURN (0x01),
  NOTIFICATION (0x02), RESPONSE (0x80), ERROR (0x81), etc.
- **Service ID** identifies a service; **Method/Event ID** the method or event
  within it. Method IDs < 0x8000 are methods, ≥ 0x8000 are events/fields.
- SOME/IP-SD uses Service ID 0xFFFF, Method ID 0x8100, with entries (Offer/
  Find/Subscribe) and options (IPv4/IPv6 endpoints).

Why it matters for RE: service IDs and method IDs are compiled into firmware
as constants; grep for them and label the dispatch table in Ghidra. A captured
Offer/Find exchange reveals every service the ECU exposes and on which port.

Capture with Wireshark (`someip` dissector) or `tshark`:
```bash
tshark -r work/<device>-eth.pcap -Y 'someip' -T fields -e someip.service_id -e someip.method_id -e someip.message_type
tshark -r work/<device>-eth.pcap -Y 'someip.service_id == 0xffff'
```

Replay/fuzz with scapy (contrib `automotive.someip`). Field names are
`srv_id`/`sub_id` (the service/method or event id); a simple request is
fully constructible without placeholders:
```python
from scapy.all import *
load_contrib("automotive.someip")
# Send a SOME/IP request: service 0x1234, method 0x0421, over UDP/IPv4.
# msg_type 0x00 = REQUEST; wrap with Ether/IP/UDP to send on the wire.
# Obtain the application service port from the captured SOME/IP-SD endpoint option; port
# 30490 is reserved for SOME/IP-SD itself, not application method traffic.
service_port = 30509  # example; replace with the port advertised in your captured SOME/IP-SD offer
pkt = Ether(src="00:11:22:33:44:55", dst="ff:ff:ff:ff:ff:ff") \
    / IP(dst="192.168.1.10") / UDP(dport=service_port) \
    / SOMEIP(srv_id=0x1234, sub_id=0x0421, client_id=0x0001,
            session_id=0x0001, proto_ver=0x01, iface_ver=0x01,
            msg_type=0x00) / Raw(load=b"\x00\x00\x00\x01")
sendp(pkt, iface="eth0")
```
For SOME/IP-SD (Service Discovery), load `automotive.someip_sd` and build the
offer with the `SDEntry_Service` / `SD` helper classes rather than a literal
`SOMEIPSD(...)` placeholder; see the scapy automotive test suite for the field
layout. Treat any SD snippet you have not run against your target as
illustrative pseudo-code until validated.

#### DoIP (Diagnostics over IP, ISO 13400)

Carries UDS (ISO 14229) diagnostic messages over TCP/UDP. Vehicle discovery
is over UDP 13400; diagnostic payloads run over TCP 13400.

Official standards:
- **ISO 13400-1** (general info & use cases) — [ISO 13400-1:2011](https://www.iso.org/standard/53765.html)
- **ISO 13400-2:2025** (transport protocol & network layer) — [ISO 13400-2:2025](https://www.iso.org/standard/87961.html)
- **ISO 13400-3:2016** (wired vehicle interface based on IEEE 802.3 100BASE-TX) — [ISO 13400-3:2016](https://www.iso.org/standard/68424.html)
- **ISO 13400-4:2016** (Ethernet-based high-speed data link connector) — [ISO 13400-4:2016](https://www.iso.org/standard/57317.html)

DoIP payload types (in the DoIP header, after a generic header):
- `0x0001` Vehicle Identification request / `0x0004` response
- `0x0002` Vehicle Announcement (broadcast on power-up)
- `0x0005` Routing Activation request / `0x0006` response (opens the TCP session)
- `0x8001`/`0x8002` Diagnostic message (carrying UDS) positive/negative ack

Why it matters for RE: a DoIP endpoint is effectively a remote UDS tester over
Ethernet — once you capture a Routing Activation + UDS exchange, you can replay
UDS services (ReadDataByIdentifier 0x22, ReadMemoryByAddress 0x23, the flash
sequence 0x34/0x36/0x37) without the CAN bus. Cross-reference with the UDS
section in `reference/can.md`; the UDS service bytes are identical.

Capture:
```bash
tshark -r work/<device>-eth.pcap -Y 'doip' -T fields -e doip.payload_type -e doip.source_logical_address -e doip.target_logical_address
tshark -r work/<device>-eth.pcap -Y 'tcp.port == 13400'
```

Record services/IDs discovered in `lode/diagnostics.md` (VID, ECU logical
addresses, supported UDS services) and the code path that services each.

## Why this matters for firmware RE

- Ethernet frames on the wire tell you what the device sends/receives, which
  often reveals protocols (ARP, DHCP, custom UDP/TCP) not visible in the
  strings alone.
- MAC address, VLAN tags, and Ethertype values are static data in firmware —
  good anchors for grep/Ghidra.
- A capture + a breakpoint on the MAC receive ISR is the fastest way to tie a
  frame to a code path.

## Frame structure (IEEE 802.3)

```
| Preamble | SFD | Dst MAC | Src MAC | 802.1Q (opt) | EtherType/Length | Payload | FCS |
  7 bytes    1    6         6         4 (if tagged)   2                 46–1500   4
```
- **Minimum frame** 64 bytes (including FCS); **maximum** 1518 (1518 with one
  VLAN tag; larger with jumbo frames or 802.1ad QinQ).
- **EtherType** identifies the upper protocol: `0x0800` IPv4, `0x0806` ARP,
  `0x86DD` IPv6, `0x8100` 802.1Q VLAN tag, `0x88E5` MACsec, vendor-specific for
  custom L2 protocols.
- **Length field** mode (≤1500) is the original 802.3 framing; **EtherType**
  mode (>1500) is Ethernet II. Most firmware uses Ethernet II.

## Capture (live)

Find the interface, then capture:
```bash
ip link                          # list interfaces, find the one to the target
ip -s link show eth0             # confirm link state and speed
sudo ethtool eth0                # link speed, duplex, driver, PHY info
sudo ethtool -S eth0             # per-counter stats (RX/TX errors, drops)

# Live capture to a pcap (promiscuous so you see all traffic on the segment)
sudo tcpdump -i eth0 -w work/<device>-eth.pcap
# Live capture in Wireshark: select eth0
wireshark -k -i eth0

# Filter at capture time to reduce noise (host MAC, VLAN, EtherType)
sudo tcpdump -i eth0 -w work/<device>-eth.pcap \
  'ether host <device-mac> and (vlan or not vlan)'
```

For a target you control, mirror its port on a managed switch (port mirroring /
SPAN) to a capture host so you see both directions without touching the target.

## Analysis (offline)

```bash
# Quick summary of conversations
tshark -r work/<device>-eth.pcap -q -z conv,eth
tshark -r work/<device>-eth.pcap -q -z endpoints,eth
# Filter by EtherType / VLAN
tshark -r work/<device>-eth.pcap -Y 'eth.type == 0x0806'   # ARP
tshark -r work/<device>-eth.pcap -Y 'vlan.id == 100'
# Dump a single frame in hex for cross-reference with xxd
tshark -r work/<device>-eth.pcap -x -c 1
```

## Craft / send / fuzz with scapy

`scapy` builds and sends frames at any layer — useful for replaying a captured
frame, probing a device's stack, or fuzzing a vendor EtherType. Always send on
the segment you control and against your own device.

```python
from scapy.all import *

# Build and send a raw Ethernet II frame with a custom EtherType
frame = Ether(src="00:11:22:33:44:55", dst="ff:ff:ff:ff:ff:ff", type=0x88B5) \
        / Raw(load=b"\x00\x01\x02\x03REVERSE")
sendp(frame, iface="eth0", count=3)

# Tagged VLAN frame
vlan = Ether(dst="ff:ff:ff:ff:ff:ff", src="00:11:22:33:44:55") \
        / Dot1Q(vlan=100) / IP(dst="192.168.1.10") / UDP(dport=1234) / Raw(load=b"PING")
sendp(vlan, iface="eth0")

# ARP probe / poison (against your own lab device)
arp = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="192.168.1.10", hwdst="ff:ff:ff:ff:ff:ff")
srp1(arp, iface="eth0", timeout=2)

# Replay a captured pcap frame-by-frame, modified
pkts = rdpcap("work/<device>-eth.pcap")
for p in pkts[:10]:
    p[Ether].src = "00:11:22:33:44:55"
    sendp(p, iface="eth0")

# Fuzz and send a vendor EtherType: keep the L2 header fixed and randomize the payload on each send.
# fuzz() leaves explicitly assigned fields unchanged, so set the Raw load to RandBin(8) (a random
# generator) rather than a literal b"\x00"*8 that fuzz() would preserve verbatim.
from scapy.all import fuzz, RandBin
for _ in range(16):
    sendp(Ether(src="00:11:22:33:44:55", dst="ff:ff:ff:ff:ff:ff", type=0x88B5) / Raw(load=RandBin(8)),
          iface="eth0")
```

`sendp` works at L2 (raw frames, any EtherType); `send` works at L3 and lets the
OS do routing. Use `srp1`/`srp` to send and capture replies on the same
interface. Sniff replies alongside a `tcpdump`/Wireshark capture so you can
correlate the sent frame with the device's response and the firmware path that
handled it.

## Cross-reference with firmware

- Find the MAC address (6 bytes, often the first frame's `Src MAC`) and grep
  the dump for it — it usually lives as a constant.
- Label the Ethernet MAC peripheral's MMIO descriptors and DMA descriptors in
  Ghidra; the receive path (ISR → descriptor ring → netif_rx equivalent) is
  where frames enter the stack.
- Custom EtherTypes or broadcast destinations are good anchors for RE.

## Record in the lode

- `lode/ethernet.md` — MAC address, PHY/MDIO setup, VLAN IDs, EtherTypes used,
  captured frames, and mapped code paths.
- `lode/diagnostics.md` — SOME/IP service/method IDs, DoIP logical addresses,
  and supported UDS services discovered.
- `lode/toolchain.md` — capture interface, switch SPAN config, tcpdump/Wireshark.

## Dependencies

- `tcpdump`/`tshark`/Wireshark, `ethtool`, `ip` (iproute2), `scapy`.
- A managed switch for port mirroring is optional but helpful.
- For automotive Ethernet, a 100BASE-T1 / 1000BASE-T1 media converter or
  capture tap (OPEN Alliance TC8).
