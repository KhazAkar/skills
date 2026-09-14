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

# Fuzz a vendor EtherType: random payloads under a fixed header
from scapy.all import fuzz
fuzz(Ether(src="00:11:22:33:44:55", dst="ff:ff:ff:ff:ff:ff", type=0x88B5) / Raw(load=b"\x00"*8))
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
- `lode/toolchain.md` — capture interface, switch SPAN config, tcpdump/Wireshark.

## Dependencies

- `tcpdump`/`tshark`/Wireshark, `ethtool`, `ip` (iproute2), `scapy`.
- A managed switch for port mirroring is optional but helpful.
- For automotive Ethernet, a 100BASE-T1 / 1000BASE-T1 media converter or
  capture tap (OPEN Alliance TC8).
