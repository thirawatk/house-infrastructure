# Proxmox LXC Inventory

All containers run on **Node 1** (HP EliteDesk 800 G3 Mini) under Proxmox VE.
All containers are **unprivileged** with **nesting=1, keyctl=1**.
DNS: **10.10.20.22** (Technitium). Domain: **271224.xyz.lan**. Timezone: **Asia/Bangkok**.

---

## Complete LXC List (Live)

| CT | Name | OS | Cores | RAM | Root | IP | Status |
|----|------|-----|-------|-----|------|-----|--------|
| 101 | cloudflared | Debian | 1 | 512M | 4G NVMe | dhcp | ✅ running |
| 102 | technitiumdns | Debian | 1 | 512M | 4G NVMe | **10.10.20.22** | ✅ running |
| 103 | caddy | Debian | 1 | 512M | 4G NVMe | dhcp | ✅ running |
| 105 | jump-ubuntu | Debian | 1 | 512M | 4G NVMe | dhcp | ✅ running |
| 301 | hermes-ubuntu | Ubuntu | 2 | 4096M | 8G NVMe | dhcp | ✅ running |
| 401 | bentopdf | Debian | 1 | 1024M | 4G NVMe | dhcp | ✅ running |
| 402 | paperless | Debian | 2 | 2048M | 8G NVMe + SATA bind | dhcp | ✅ running |
| 403 | joplin-server | Debian | 1 | 1024M | 4G NVMe + SATA bind | dhcp | ✅ running |
| 404 | autocaliweb | Debian | 1 | 2048M | 6G NVMe + SATA bind | **10.10.20.44** | ✅ running |
| 501 | monitor | Ubuntu | 1 | 2048M | 8G NVMe | **10.10.20.51** | ✅ running |

---

## Infrastructure Layer

### CT 101 — Cloudflared

| | |
|---|---|
| **Purpose** | Cloudflare Tunnel — exposes internal services to the internet |
| **OS** | Debian minimal |
| **Storage** | NVMe (`local-e3000-512gb`) |
| **Network** | VLAN 20 (Server), DHCP |
| **Key Config** | Outbound-only tunnel to Cloudflare, no open inbound ports |
| **Public DNS** | `271224.xyz` → tunnel → internal services |

### CT 102 — Technitium DNS

| | |
|---|---|
| **Purpose** | Local DNS server with ad-blocking and split-horizon resolution |
| **OS** | Debian minimal |
| **Storage** | NVMe |
| **Network** | Static IP **10.10.20.22**, VLAN 20 |
| **Key Features** | Ad-blocking, split-horizon (`271224.xyz.lan` → internal IPs) |
| **Forwarders** | Cloudflare / Google DNS |

### CT 103 — Caddy

| | |
|---|---|
| **Purpose** | Production reverse proxy — TLS termination + internal routing |
| **OS** | Debian minimal |
| **Storage** | NVMe |
| **Network** | VLAN 20, DHCP |
| **Role** | Translates `*.271224.xyz` → `*.271224.xyz.lan` on internal ports |
| **Upstream** | Cloudflare Tunnel (CT 101) |

### CT 105 — Jump Server

| | |
|---|---|
| **Purpose** | SSH bastion / management gateway into internal network |
| **OS** | Debian minimal |
| **Storage** | NVMe |
| **Network** | VLAN 20, DHCP |
| **Access** | Public key auth only, restricted source IPs |
| **Services** | SSH (port 22), web-based management tools |

---

## Application Layer

### CT 301 — Hermes Agent ⭐

| | |
|---|---|
| **Purpose** | AI agent platform — 5 profiles for automation, analysis, monitoring |
| **OS** | Ubuntu |
| **CPU** | 2 cores |
| **RAM** | 4096 MB |
| **Storage** | NVMe (8GB) |
| **Network** | VLAN 20, DHCP |
| **Memory** | Self-hosted Hindsight API (127.0.0.1:8888) + PostgreSQL 16 |
| **Profiles** | buddy, investor, trader, monitor, financialanalyst |
| **Gateways** | Telegram (primary), CLI |

#### Profile Details

| Profile | Model | Telegram ID | Special |
|---------|-------|-------------|---------|
| buddy | minimax/m2.5-free | 2135517501 | Primary orchestrator |
| investor | various (OpenRouter) | 2135517501 | Investment analysis, multi-model |
| trader | various (OpenRouter) | 2135517501 | Market monitoring |
| monitor | various (OpenRouter) | 2135517501 | Infrastructure monitoring |
| financialanalyst | gemma-4-31b-it:free | 2135517501 + 8748834444 | Shared Tae + Nhoo |
| **Memory** | Hindsight API | Per-user banks | PostgreSQL + pgvector |

### CT 401 — BentoPDF

| | |
|---|---|
| **Purpose** | Self-hosted PDF editing and manipulation |
| **RAM** | 1024 MB |
| **Storage** | NVMe |
| **Network** | VLAN 20 |

### CT 402 — Paperless-NGX

| | |
|---|---|
| **Purpose** | Document management engine (OCR, tagging, search) |
| **RAM** | 2048 MB |
| **OS Storage** | NVMe (8GB) |
| **Data Storage** | 1TB SATA SSD (`ssd-vault`) — bind-mounted |
| **Network** | VLAN 20 |
| **Document Volume** | Bind-mounted from `ssd-vault` |

### CT 403 — Joplin Server

| | |
|---|---|
| **Purpose** | Private note syncing backend (OneNote replacement) |
| **RAM** | 1024 MB |
| **OS Storage** | NVMe (4GB) |
| **Data Storage** | 1TB SATA SSD (`ssd-vault`) — database bind-mount |
| **Network** | VLAN 20 |
| **Clients** | Joplin mobile/desktop apps |

### CT 404 — Autocaliweb (CWA) 📚

| | |
|---|---|
| **Purpose** | Calibre-Web-Automated — eBook library management + WebDAV sync |
| **OS** | Debian (unprivileged, nesting=1, keyctl=1) |
| **RAM** | 2048 MB |
| **Swap** | 512 MB |
| **Root** | 6GB NVMe (`local-e3000-512gb:subvol-404-disk-0`) |
| **Mount Points** | `mp0: /ssd-vault/calibre/library/` → `/mnt/calibre/library` |
| | `mp1: /ssd-vault/calibre-sync/` → `/var/www/webdav` |
| **Network** | Static IP **10.10.20.44**, VLAN 20, bridge=lan |
| **Tags** | community-script, ebooks |
| **Source** | [community-scripts/ProxmoxVE](https://github.com/community-scripts/ProxmoxVE) |

### CT 501 — Monitor 📊

| | |
|---|---|
| **Purpose** | Infrastructure monitoring |
| **OS** | Ubuntu (unprivileged, nesting=1, keyctl=1) |
| **CPU** | 1 core |
| **RAM** | 2048 MB |
| **Swap** | 512 MB |
| **Root** | 8GB NVMe (`local-e3000-512gb:subvol-501-disk-0`) |
| **Network** | Static IP **10.10.20.51**, VLAN 20, bridge=lan |
| **Tags** | monitoring, network |

---

## Storage Summary

| Storage Pool | CTs | Contents |
|---|---|---|
| `local-e3000-512gb` (NVMe) | 101, 102, 103, 105, 301, 401 | All OS roots |
| `local-e3000-512gb` (NVMe) | 402, 403, 404, 501 | OS roots (larger) |
| `local-samsung-1tb` (SATA ssd-vault) | 402, 403 | Paperless docs + Joplin database |
| `local-samsung-1tb` (SATA ssd-vault) | 404 | Calibre library + WebDAV sync |

---

## Network Diagram (Logical)

```
VLAN 20 (Server Zone — 10.10.20.0/24)
─────────────────────────────────────
                    │
     ┌──────────────┼──────────────────────────────┐
     │              │                              │
  Cloudflare     Caddy (.23)                  Technitium
  Tunnel (101)   (reverse proxy)              DNS (.22)
     │              │                              │
     │    ┌─────────┼──────────┐                   │
     │    │         │          │              ┌────┴────┐
     │  Paperless  Joplin   Monitor          Jump      BentoPDF
     │  (402)     (403)     (501)           (105)     (401)
     │    │         │       .20.51            │
     │    │    ssd-vault  NVMe              │
     │    │    bind-mount                   │
     │                                    ┌──┴──────────┐
     │                                    │  Hermes     │
     │                                    │  (301)      │
     │                                    │  NVMe 8G    │
     │                                    └──┬──────────┘
     │                                   ┌───┴────┐
     │                                   │Hindsight│
     │                                   │API :8888│
     │                                   └───┬────┘
     │                                   ┌───┴────┐
     │                                   │PostgreSQL
     │                                   │+pgvector
     │                                   └────────┘
     │
  ┌──┴──────────┐
  │ Autocaliweb │
  │  (404) CWA  │
  │  .20.44     │
  │  ssd-vault  │
  │  bind-mount │
  └─────────────┘
```

---

## Management Commands

```bash
# List all containers
pct list

# Enter a container
pct enter <CTID>

# Start/Stop
pct start <CTID>
pct stop <CTID>

# Container config
pct config <CTID>

# Backup a container
vzdump <CTID> --compress zstd --mode snapshot

# Live migrate (if stop not needed)
pct migrate <CTID> <target-node> --online

# Check storage
pvesm status
df -h

# Reboot from host
pct reboot <CTID>
```

---

## IP Allocation (Static)

| IP | CT | Name | Purpose |
|----|-----|------|---------|
| 10.10.20.22 | 102 | technitiumdns | DNS server |
| 10.10.20.44 | 404 | autocaliweb | Calibre-Web-Automated |
| 10.10.20.51 | 501 | monitor | Infrastructure monitoring |

> All other containers use DHCP. Consider assigning static IPs via DHCP reservations on the Technitium DNS/DHCP server for consistency.

---

## Backup Strategy

| What | Method | Frequency |
|------|--------|-----------|
| LXC configs | `vzdump` (zstd, snapshot) | Weekly |
| Paperless documents | `rsync` to external | Daily |
| Joplin database | `pg_dump` | Daily |
| Hindsight/PostgreSQL | `pg_dump` | Daily |
| Calibre library | `rsync` (ssd-vault) | Daily |
| Proxmox host config | `tar /etc/pve` | Weekly |
