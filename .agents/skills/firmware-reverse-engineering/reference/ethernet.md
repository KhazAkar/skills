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

- `tcpdump`/`tshark`/Wireshark, `ethtool`, `ip` (iproute2). A managed switch
  for port mirroring is optional but helpful.
