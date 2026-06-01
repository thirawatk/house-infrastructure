# Proxmox LXC Inventory

All containers run on **Node 1** (HP EliteDesk 800 G3 Mini) under Proxmox VE.

---

## Infrastructure Layer

### CT 101 — Cloudflared

| | |
|---|---|
| **Purpose** | Cloudflare Tunnel — exposes internal services to the internet |
| **OS** | Debian minimal |
| **Storage** | NVMe (`local-e3000-512gb`) |
| **Network** | VLAN 20 (Server) |
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
| **Network** | VLAN 20 |
| **Role** | Translates `*.271224.xyz` → `*.271224.xyz.lan` on internal ports |
| **Upstream** | Cloudflare Tunnel (CT 101) |

### CT 105 — Jump Server

| | |
|---|---|
| **Purpose** | SSH bastion / management gateway into internal network |
| **OS** | Debian minimal |
| **Storage** | NVMe |
| **Network** | VLAN 20 |
| **Access** | Public key auth only, restricted source IPs |
| **Services** | SSH (port 22), web-based management tools |

---

## Application Layer

### CT 301 — Hermes Agent ⭐

| | |
|---|---|
| **Purpose** | AI agent platform — 5 profiles for automation, analysis, monitoring |
| **OS** | Ubuntu/Debian |
| **Storage** | NVMe |
| **Network** | VLAN 20 |
| **Memory** | Self-hosted Hindsight API (127.0.0.1:8888) + PostgreSQL 16 |
| **Profiles** | buddy, investor, trader, monitor, financialanalyst |
| **Gateways** | Telegram (primary), CLI |

#### Profile Details

| Profile | Model | Special |
|---------|-------|---------|
| buddy | minimax/m2.5-free | Primary orchestrator |
| investor | various (OpenRouter) | Investment analysis, multi-model |
| trader | various (OpenRouter) | Market monitoring |
| monitor | various (OpenRouter) | Infrastructure monitoring |
| financialanalyst | gemma-4-31b-it:free | Shared Tae + Nhoo |
| **Memory** | Hindsight API | Per-user banks via Telegram ID |

### CT 401 — BentoPDF

| | |
|---|---|
| **Purpose** | Self-hosted PDF editing and manipulation |
| **Storage** | NVMe |
| **Network** | VLAN 20 |

### CT 402 — Paperless-NGX

| | |
|---|---|
| **Purpose** | Document management engine (OCR, tagging, search) |
| **OS Storage** | NVMe |
| **Data Storage** | 1TB SATA SSD (`ssd-vault`) |
| **Network** | VLAN 20 |
| **Document Volume** | Bind-mounted from `ssd-vault` |

### CT 403 — Joplin Server

| | |
|---|---|
| **Purpose** | Private note-syncing backend (OneNote replacement) |
| **OS Storage** | NVMe |
| **Data Storage** | 1TB SATA SSD (`ssd-vault`) — database |
| **Network** | VLAN 20 |
| **Clients** | Joplin mobile/desktop apps |

---

## Storage Summary

| Storage Pool | CTs | Contents |
|---|---|---|
| `local-e3000-512gb` (NVMe) | 101, 102, 103, 105, 301, 401 | All OS roots + app containers |
| `local-samsung-1tb` (SATA ssd-vault) | 402, 403 | Paperless docs + Joplin database |

---

## Network Diagram (Logical)

```
VLAN 20 (Server Zone — 10.10.20.0/24)
─────────────────────────────────────
                    │
          ┌─────────┼──────────────────────────┐
          │         │                          │
     Technitium   Caddy                   Cloudflare
     DNS (.22)   (reverse proxy)          Tunnel (101)
          │         │                          │
          │    ┌────┴────┐                     │
          │    │         │                ┌────┴────┐
          │  Paperless  Joplin          Hermes    Jump
          │  (402)     (403)            (301)     Server
          │                                │      (105)
          │                           ┌────┴────┐
          │                           │Hindsight│
          │                           │API :8888│
          │                           └────┬────┘
          │                           ┌────┴────┐
          │                           │PostgreSQL│
          │                           │+pgvector │
          │                           └─────────┘
          │
     ┌────┴────┐
     │ BentoPDF│
     │  (401)  │
     └─────────┘
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

# Backup a container
vzdump <CTID> --compress zstd --mode snapshot

# Check storage
pvesm status
df -h
```

---

## Backup Strategy

| What | Method | Frequency |
|------|--------|-----------|
| LXC configs | `vzdump` (zstd, snapshot) | Weekly |
| Paperless documents | `rsync` to external | Daily |
| Joplin database | `pg_dump` | Daily |
| Hindsight/PostgreSQL | `pg_dump` | Daily |
| Proxmox host config | `tar /etc/pve` | Weekly |
