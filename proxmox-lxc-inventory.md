# Proxmox LXC Inventory

All containers run on **Node 1** (HP EliteDesk 800 G3 Mini, i5-6500, 32GB RAM) under Proxmox VE.
All containers are **unprivileged** with **nesting=1, keyctl=1**.
DNS: **10.10.20.22** (Technitium). Domain: **271224.xyz.lan**. Timezone: **Asia/Bangkok**.
Last updated: 2026-06-14.

---

## Complete LXC List (Live)

| CT | Name | OS | Cores | RAM | Root | IP | Status |
|----|------|-----|-------|-----|------|-----|--------|
|| 101 | cloudflared | Debian | 1 | 512M | 4G NVMe | dhcp | ✅ running |
|| 102 | technitiumdns | Debian | 1 | 512M | 4G NVMe | **10.10.20.22** | ✅ running |
|| 103 | caddy | Debian | 1 | 512M | 4G NVMe | dhcp | ✅ running |
|| 105 | jump-ubuntu | Debian | 1 | 512M | 4G NVMe | dhcp | ✅ running |
|| 301 | hermes-ubuntu | Ubuntu | 2 | 4096M | 8G NVMe | dhcp | ✅ running |
|| 302 | openwebui | Ubuntu | 2 | 2048M | 10G NVMe | **10.10.20.32** | ✅ running |
|| 401 | bentopdf | Debian | 1 | 1024M | 4G NVMe | dhcp | ✅ running |
|| 402 | paperless | Debian | 2 | 2048M | 8G NVMe + SATA bind | dhcp | ✅ running |
||| 404 | kavita | Debian | 1 | 2048M | 6G NVMe + SATA bind | **10.10.20.44** | ✅ running |
|| 501 | monitor | Ubuntu | 1 | 2048M | 8G NVMe | **10.10.20.51** | ✅ running |

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
| buddy | openrouter/owl-alpha | 2135517501 | Primary orchestrator |
| investor | openrouter/owl-alpha | 2135517501 | Investment analysis, multi-model |
| trader | openrouter/owl-alpha | 2135517501 | Market monitoring |
| monitor | openrouter/owl-alpha | 2135517501 | Infrastructure monitoring |
| financialanalyst | openrouter/owl-alpha | 2135517501 + 8748834444 | Shared Tae + Nhoo |
| **Memory** | Hindsight API | Per-user banks | PostgreSQL + pgvector, BGE-M3 embeddings |

### CT 302 — Open WebUI

| | |
|---|---|
| **Purpose** | Open WebUI — web interface for Hermes FA profile (and other LLM frontends) |
| **OS** | Ubuntu 24.04 |
| **CPU** | 2 cores |
| **RAM** | 2048 MB |
| **Storage** | NVMe (10GB) |
| **Network** | Static IP **10.10.20.32**, VLAN 20 |
| **Domain (external)** | `chatui.271224.xyz` (via Cloudflare Tunnel → Caddy → CT 302:3000) |
| **Docker** | Open WebUI container + FA API server reverse proxy |

> **Why `chatui` externally?** The original `chat.271224.xyz` had a local Technitium A record pointing to private IP (10.10.20.32), bypassing the Cloudflare Tunnel → external users got 502. `chatui.271224.xyz` has no local override → routes through Cloudflare Tunnel correctly. No internal `.lan` record exists — chatui is internet-only.

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

### CT 404 — Kavita 📚

| | |
|---|---|
| **Purpose** | Kavita eBook server — reading, OPDS, OneDrive sync |
| **OS** | Debian (unprivileged, nesting=1, keyctl=1) |
| **RAM** | 2048 MB |
| **Swap** | 512 MB |
| **Root** | 6GB NVMe (`local-e3000-512gb:subvol-404-disk-0`) |
| **Mount Points** | `mp0: /ssd-vault/calibre/library/` → `/mnt/calibre/library` |
| | `mp1: /ssd-vault/calibre-sync/` → `/var/www/webdav` |
| **Network** | Static IP **10.10.20.44**, VLAN 20, bridge=lan |
| **Domain** | `kavita.271224.xyz` (Caddy → CT 404:5000) |
| **Docker** | `jvmilazz0/kavita:0.8.4` (update to 0.9.0.x available) |
| **Source** | Replaced Calibre-Web-Automated (CWA) on 2026-06-05 |

#### Kavita + OneDrive Sync (2026-06-06)

| | |
|---|---|
| **Source** | `onedrive:Personal_stuff/e-book/` (7.9GB, 580 files) |
| **Local** | `/mnt/calibre/library/` (bind-mounted to container `/books`) |
| **Tool** | rclone v1.74.2 |
| **Schedule** | Every 6 hours via `/etc/cron.d/rclone-onedrive-sync` |
| **Config** | `/root/.config/rclone/rclone.conf` — drive_id: `847FBA794A95EBF0`, drive_type: personal |
| **Login** | lottez / Th!2awatKVT |
| **Notes** | rclone 1.74+ requires `drive_id` for OneDrive personal. Get via Graph API `/me/drive`. Write config directly to file, NOT via `rclone config update` (re-triggers OAuth). Token JSON may be URL-encoded — use `urllib.parse.unquote()` first. |

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
| `local-e3000-512gb` (NVMe) | 402, 404, 501 | OS roots (larger) |
| `local-samsung-1tb` (SATA ssd-vault) | 402 | Paperless docs |
| `local-samsung-1tb` (SATA ssd-vault) | 404 | Kavita eBook library (synced from OneDrive) + WebDAV sync |

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
     │  Paperless  Monitor          Jump      BentoPDF
     │  (402)     (501)            (105)     (401)
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
     │  ┌─────────────┐    ┌──────────────┐
Autocaliweb │    │  kavita     │
  │  │  .20.32     │    │  (404)      │
  │  │  NVMe 10G   │    │  Docker     │
     │  │  NVMe 10G   │    │  ssd-vault   │
     │  └─────────────┘    │  bind-mount  │
     │                     └──────────────┘
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
|| 10.10.20.22 | 102 | technitiumdns | DNS server |
|| 10.10.20.32 | 302 | openwebui | Open WebUI (chatui.271224.xyz) |
|| 10.10.20.44 | 404 | kavita | Kavita eBook server (Docker) |
|| 10.10.20.51 | 501 | monitor | Infrastructure monitoring |

> All other containers use DHCP. Consider assigning static IPs via DHCP reservations on the Technitium DNS/DHCP server for consistency.

---

## Backup Strategy

| What | Method | Frequency |
|------|--------|-----------|
|| LXC configs | `vzdump` (zstd, snapshot) to `ssd-vault-backup` | Weekly |
|| Paperless documents | `rsync` to external | Daily |
|| Hindsight/PostgreSQL | `pg_dump` | Daily |
|| Kavita library | rclone sync from OneDrive (source of truth) | Every 6 hours |
|| Proxmox host config | `tar /etc/pve` | Weekly |

> **Note:** ZFS pools don't support `backup` content type for `vzdump`. Workaround: `/ssd-vault/backups/proxmox` directory added as `dir` storage type (`ssd-vault-backup`), supports backup content type and auto-prunes to keep-last=3.

---

## Resource Allocation Summary

**Node 1 total: 32GB RAM, i5-6500 (4C/4T)**

| CT | Name | RAM | Cores |
|----|------|-----|-------|
| 101 | cloudflared | 512 MB | 1 |
| 102 | technitiumdns | 512 MB | 1 |
| 103 | caddy | 512 MB | 1 |
| 105 | jump-ubuntu | 512 MB | 1 |
| 301 | hermes-ubuntu | 4096 MB | 2 |
| 302 | openwebui | 2048 MB | 2 |
| 401 | bentopdf | 1024 MB | 1 |
| 402 | paperless | 2048 MB | 2 |
| 404 | kavita | 2048 MB | 1 |
| 501 | monitor | 2048 MB | 1 |
| **Total allocated** | | **17,408 MB (17 GB)** | **13 shares** |
| **Host total** | | **32 GB** | **4 physical cores** |
| **Headroom** | | **~15 GB free** | — |
