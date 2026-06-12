# OpenWrt AP Configuration — Xiaomi AX3600

Dual AP setup for home network. Both run OpenWrt as dumb APs (no NAT, no DHCP).

## Network Overview

| VLAN | Name | Subnet | Purpose |
|------|------|--------|---------|
| 1 | Management | 192.168.2.0/24 | AP management access |
| 10 | Trusted | 10.10.10.0/24 | Personal devices |
| 20 | Server | 10.10.20.0/24 | Proxmox, LXCs |
| 30 | Streaming | 10.10.30.0/24 | Media devices |
| 40 | IoT | 10.10.40.0/24 | Smart home, CCTV |

## AP Summary

| AP | IP | Location | Role |
|----|----|----------|------|
| AP1 | 192.168.2.2 | Living room | Entertainment zone |
| AP2 | 192.168.2.3 | Server rack | Server/IoT zone |

## WiFi SSIDs

| SSID | VLAN | Security | Purpose |
|------|------|----------|---------|
| nt-nw5 | Trusted (10) | WPA3 (sae-mixed) | Primary devices |
| nt-nw | Trusted (10) | WPA2/3 (psk-mixed) | Legacy devices |
| nt-nw-stm | Streaming (30) | WPA3 (sae-mixed) | Media streaming |
| nt-nw-iot | IoT (40) | Open | Smart home devices |

## Key Differences (AP1 vs AP2)

| Feature | AP1 | AP2 |
|---------|-----|-----|
| 5GHz channel | 48 (HE40) | 120 (HE80) |
| 2.4GHz radio | Enabled | Enabled |
| Streaming bridge | br-lan.30 + lan1 + lan2 | br-lan.30 + lan3 |
| Management IP | 192.168.2.2 | 192.168.2.3 |

## Files

```
ap1/
├── wireless    # WiFi config (3 radios, 4 SSIDs)
├── network     # VLAN bridging, management interface
├── firewall    # Zone rules (trust, server, streaming, iot)
└── dhcp        # DHCP relay settings

ap2/
├── wireless    # WiFi config (3 radios, 4 SSIDs)
├── network     # VLAN bridging, management interface
├── firewall    # Zone rules
└── dhcp        # DHCP relay settings
```

## Recovery Notes

If AP config gets corrupted:
1. Backup files are in this repo
2. SCP to AP: `scp ap2/* root@192.168.2.3:/etc/config/`
3. Restart: `/etc/init.d/network restart && /etc/init.d/wifi restart`

## Passwords

- WiFi: `thirawat` (trusted), `thirawatstm` (streaming)
- SSH root: (same as WiFi or set via LuCI)

---
*Last updated: 2026-06-12*
