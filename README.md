# 🏰 The Sovereign Fortress — Home Infrastructure

> Complete network and server infrastructure documentation for a smart home lab in Thailand.

![Network Topology Diagram](diagrams/network-topology.png)

## 📋 Table of Contents

- [Overview](#overview)
- [Network Architecture](#network-architecture)
- [Hardware Inventory](#hardware-inventory)
- [Proxmox Virtualization](#proxmox-virtualization)
- [Hermes Agent Platform](#hermes-agent-platform)
- [Rack Layout](#rack-layout)

---

## Overview

| | |
|---|---|
| **Location** | Thailand (Asia/Bangkok) |
| **Public Domain** | `271224.xyz` |
| **Local Domain** | `271224.xyz.lan` |
| **Network Philosophy** | VLAN-segmented, security-first, self-hosted |
| **Primary Compute** | HP EliteDesk 800 G3 Mini (x86, Intel QuickSync) |

### Network Summary

| VLAN | Subnet | Zone | Purpose |
|------|--------|------|---------|
| 10 | 10.10.10.0/24 | Trusted | Personal devices, management |
| 20 | 10.10.20.0/24 | Server | Proxmox, LXCs, infrastructure |
| 30 | 10.10.30.0/24 | Streaming | Media clients (TV, Marantz) |
| 40 | 10.10.40.0/24 | IoT | Smart home, CCTV, PoE devices |

---

## Network Architecture

### Topology Flow

```
ISP WAN
  └── NanoPi R3S (OpenWrt Router/Firewall)
        └── L2 Managed Switch (VLAN Trunking)
              ├── AP1 (Xiaomi AX3600 — Dumb AP)
              │     ├── LAN: Sony Android TV, Marantz SR5015
              │     └── WiFi:
              │           ├── "nt-nw5" (WPA3-PSK) → VLAN 10
              │           ├── "nt-nw-stm" (WPA2-PSK) → VLAN 30
              │           └── "nt-nw-iot" (Open) → VLAN 40
              │
              └── AP2 (Xiaomi AX3600 — Dumb AP)
                    ├── LAN Port 1: Node 1 (Proxmox — HP EliteDesk)
                    └── LAN Port 2: Dumb PoE Switch
                          └── Hikvision NVR (CCTV Recording)
```

### Edge Routing

- **Device:** NanoPi R3S
- **OS:** OpenWrt (standalone)
- **Role:** Core router, firewall, inter-VLAN routing
- **IP:** 10.10.10.1

### DNS Infrastructure

- **Server:** Technitium DNS at `10.10.20.22` (LXC 102)
- **Features:** Ad-blocking + split-horizon DNS
- **Public domain:** `271224.xyz` via Cloudflare Tunnels (LXC 101)
- **Internal domain:** `271224.xyz.lan` local resolution
- **Reverse Proxy:** Caddy (LXC 103) — translates external `.xyz` to internal services
- **Domain gotcha:** If a public domain has a local A record pointing to private IP, external users bypass the Cloudflare Tunnel → 502. Fix: use a different subdomain externally (e.g., `chatui.271224.xyz` instead of `chat.271224.xyz`).

### Wireless

| AP | Model | Role | SSIDs | Firmware |
|----|-------|------|-------|----------|
| AP1 | Xiaomi AX3600 | Entertainment zone | nt-nw5, nt-nw-stm, nt-nw-iot | OpenWrt 25.12.2 |
| AP2 | Xiaomi AX3600 | Server / IoT zone | (used as trunk for LXCs) | OpenWrt 25.12.2 |

Both APs run OpenWrt as dumb APs — no NAT, no DHCP (handled by router). Both online as of 2026-07.

---

## Hardware Inventory

### Node 1 — Proxmox Virtualization Engine

| Spec | Detail |
|------|--------|
| **Model** | HP EliteDesk 800 G3 Mini |
| **CPU** | Intel Core i5-6500 (4c/4t) @ 3.20GHz with QuickSync iGPU |
| **RAM** | 32 GB DDR4 (~13 GB used by workloads) |
| **PVE Version** | Proxmox VE 9.1.9 — single node (`node1`), no VMs, LXC-only |
| **OS Drive** | 512GB Hiksemi E3000 M.2 NVMe SSD (`local-e3000-512gb`) |
| **Data Drive** | 1TB Samsung 870 EVO SATA SSD (`local-samsung-1tb` + `ssd-vault-backup`) |
| **NIC 1** | Onboard 1 GbE → Proxmox management / Web GUI |
| **NIC 2** | Added 2.5 GbE → Production LAN bridge (all LXC traffic) |

### Node 2 — Frigate NVR (Planned)

| Spec | Detail |
|------|--------|
| **Model** | HP EliteDesk 800 G3 Mini (identical twin) |
| **Role** | Frigate NVR — local AI object detection for CCTV |
| **Storage** | Multi-bay SATA DAS enclosure via USB-C passthrough |

### Network Gear

| Device | Role | Location |
|--------|------|----------|
| NanoPi R3S | OpenWrt router/firewall | Rack |
| L2 Managed Switch | VLAN trunking, core switching | Rack |
| Xiaomi AX3600 (AP1) | Dumb AP — entertainment | Near living room |
| Xiaomi AX3600 (AP2) | Dumb AP — server zone | Near rack |
| Dumb PoE Switch | Powers CCTV cameras | Near rack |

### Connected Clients

| Device | Connection | VLAN |
|--------|-----------|------|
| Sony Android TV | AP1 LAN | Trusted (10) |
| Marantz SR5015 | AP1 LAN | Trusted (10) |
| Hikvision NVR | PoE Switch (AP2) | IoT (40) |

---

## Proxmox Virtualization

### LXC Inventory

All containers run on **Node 1** (`node1`). OS/root on NVMe unless noted. **12 LXCs, all running, all VLAN 20.**

| CT ID | Name | Purpose | vCPU | RAM | Rootfs | IP |
|-------|------|---------|-----:|----:|--------|----|
| 101 | cloudflared | Cloudflare Tunnels (public → local) | 1 | 512 MB | 2G NVMe | 10.10.20.21 |
| 102 | technitiumdns | Local DNS (ad-block + split-horizon) | 1 | 512 MB | 2G NVMe | 10.10.20.22 |
| 103 | caddy | Production reverse proxy (.xyz → .lan) | 1 | 2 GB | 6G NVMe | 10.10.20.23 |
| 301 | hermes-ubuntu | Hermes AI agent platform (9 profiles) | 4 | 12 GB | 100G NVMe | 10.10.20.31 |
| 302 | openwebui | Open WebUI for FA profile web access | 2 | 2 GB | 10G NVMe | 10.10.20.32 |
| 401 | bentopdf | Self-hosted PDF editing | 1 | 2 GB | 4G NVMe | 10.10.20.41 |
| 402 | paperless | Document management (Paperless-NGX) | 1 | 3 GB | 12G NVMe | 10.10.20.42 |
| 403 | joplin-server | Joplin sync server (Memory Palace) | 1 | 1 GB | 8G NVMe | 10.10.20.43 |
| 404 | autocaliweb | Calibre-Web-Automated (eBook library + WebDAV) | 1 | 2 GB | 6G NVMe | 10.10.20.44 |
| 501 | monitor | Prometheus + Grafana monitoring | 1 | 2 GB | 8G NVMe | 10.10.20.51 |
| 502 | neo4j-life-graph | Neo4j graph DB (Life Graph astrology) | 2 | 2 GB | 12G NVMe | 10.10.20.52 |
| 503 | hermes-mcp | Hermes infra MCP server (FastMCP, port 8080) | 1 | 1 GB | 8G NVMe | 10.10.20.53 |

**Totals:** 17 vCPU allocated (4.25x oversubscribed on 4 cores), 30 GB RAM allocated of 32 GB.

**Removed:** CT 105 (`jump-ubuntu`) deleted — 10.10.20.25 freed. SSH now goes direct to hosts.

> **Note:** Heavy local LLM stacks (Ollama) have been intentionally deprecated to preserve host compute resources. Open WebUI (CT 302) connects to Hermes FA's API server instead.

### Storage Pools

| Pool | Type | Disk | Size | Used | Purpose |
|------|------|------|------|-----:|---------|
| `local-e3000-512gb` | zfspool | Hiksemi E3000 NVMe | 477 GB | 18% | OS, LXC root filesystems |
| `local-samsung-1tb` | zfspool | Samsung 870 EVO SATA | 945 GB | 3.4% | App data, Paperless docs, Calibre library, databases |
| `ssd-vault-backup` | dir | Samsung 870 EVO SATA | 945 GB | 3.4% | `vzdump` backup target (added 2026) |
| `local` | dir | NVMe | 385 GB | 0.3% | ISO images, snippets |

### Future

- **Node 2 + DAS:** Frigate NVR with USB-C passthrough for CCTV recording
- **Additional LXCs:** As needed — home automation hub, media server, backup target

### ⚠️ Backup Status: Partially Mitigated

**Progress since 2026-06:** `ssd-vault-backup` dir storage now exists on the Samsung 870 EVO — `vzdump` targets are available. **However, no backup jobs are scheduled yet** (`/etc/pve/jobs.cfg` is empty, no vzdump cron).

**Remaining gaps:**

1. **No scheduled jobs** — CT roots are not being backed up automatically
2. **Same-disk risk** — `ssd-vault-backup` lives on the same Samsung SSD as app data. CT roots (NVMe → Samsung) ARE protected against NVMe failure, but Samsung-hosted app data (Paperless, Calibre) has no off-disk copy
3. **No off-site copy** — theft/fire/flood still = total loss

**Still recommended (either option):**

| Option | Capacity | Purpose | Approx. Cost |
|--------|----------|---------|-------------|
| **USB external HDD/SSD** (2-4TB) | 2-4 TB | Physically separate `vzdump` target + `rsync` offsite | ~฿1,500-3,500 |
| **Expand DAS** (add disk to Node 2 enclosure) | 4+ TB | Shared backup target across both nodes | ~฿2,000-4,000 |

**What should get backed up:**
- 12 LXC configs + root filesystems via `vzdump` (zstd compressed) — ~20-40GB total
- Paperless documents via `rsync`
- Hindsight/PostgreSQL via `pg_dump`
- Proxmox host config via `tar /etc/pve`

---

## Hermes Agent Platform

Runs in **LXC 301** on Proxmox Node 1.

### Profiles

9 profiles, all running on Hermes Agent **v0.18.0**. Models are multi-provider (OpenRouter, Xiaomi, DeepSeek, Mistral, Z.AI, Moonshot, custom endpoints) and rotate — check live config for current assignments.

| Profile | User(s) | Purpose |
|---------|---------|---------|
| **default** | Tae | System-wide config, cross-profile ops |
| **buddy** | Tae | Primary agent, orchestrator |
| **financialanalyst** | Tae + Nhoo | Shared investment analysis (FA bot) |
| **investor** | Tae | Investment research |
| **trader** | Tae | Market monitoring, paper trading |
| **monitor** | Tae | Infrastructure monitoring (@TaeMonitoringbot) |
| **astrology** | Tae | Life Graph astrology consultations |
| **midwife-consultant** | Tae | Midwife consultation profile |
| **book-reviewer** | Tae | Book review pipeline |

### Memory System

- **Provider:** Self-hosted Hindsight API (`127.0.0.1:8888`)
- **Mode:** `local_external` with external PostgreSQL 16 + pgvector
- **Embedding:** `BAAI/bge-m3` (1024-dim, multilingual, Thai + English support)
- **Storage:** `local-samsung-1tb` (dedicated volume)
- **Banks:** 12 banks (9 Tae profiles + Nhoo's banks), per-profile isolation
- **Layer 3:** Joplin Memory Palace (CT 403) — shared cross-profile knowledge
- **Hermes Version:** v0.18.0

### Supporting Services

| CT | Service | Role |
|----|---------|------|
| 302 | Open WebUI | Web frontend → Hermes FA API (10.10.20.32) |
| 502 | neo4j-life-graph | Graph DB backing Life Graph astrology (10.10.20.52) |
| 503 | hermes-mcp | Infra MCP server — Proxmox/service tools for all gateways (10.10.20.53:8080) |

### Infrastructure Services

| Service | Telegram ID | Role |
|---------|-------------|------|
| Tae | `2135517501` | Primary user, all profiles |
| Nhoo | `8748834444` | Wife, FA profile access |
| FA Bot | `8897627710` | Financial analyst profile |

---

## Rack Layout (12U Cabinet)

```
[1U]  PDU (Power Distribution Unit)
[1U]  Blank Patch Panel (Cat6 CCTV drops)
[1U]  L2 Managed Switch
[1U]  Cantilever Shelf: ISP Modem + NanoPi R3S Router
[1U]  Cantilever Shelf: Node 1 + Node 2 HP Minis
[3U]  4-Point Shelf: DAS Storage Tower Enclosure
[1U]  Cantilever Shelf: Dumb PoE Switch (CCTV)
[1U]  Blank Ventilation / Airflow Panel
[2U]  UPS (Battery Backup) — base
```

### Cabinet Specs

- **Height:** 12U vertical
- **Min Depth:** 600mm (for DAS cable clearance + ventilation)
- **DAS Mounting:** Vertical orientation (hard drive platter health) with 4-point bridge shelf to prevent sagging

---

## 🔗 See Also

- [Network Topology](network-topology.md) — Detailed VLAN and subnet breakdown
- [Hardware Inventory](hardware-inventory.md) — Full bill of materials
- [Proxmox LXC Inventory](proxmox-lxc-inventory.md) — Container specs and configs

---

*Last updated: 2026-07-26 (verified live against node1 — 12 LXCs, PVE 9.1.9)*
