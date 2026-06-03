# Network Topology — Detailed Breakdown

## Layer 1: Edge (WAN → Router)

```
ISP WAN ──→ NanoPi R3S (OpenWrt) ──→ L2 Managed Switch
              10.10.10.1                  VLAN Trunk
              Firewall + NAT
              Inter-VLAN Routing
```

### NanoPi R3S — Port Assignments

| Port | Role |
|------|------|
| WAN | ISP connection |
| LAN1 | L2 Managed Switch (trunk, all VLANs) |

### OpenWrt Configuration Highlights

- **Firewall zones:** 4 zones (trusted, server, streaming, iot)
- **Inter-VLAN routing:** Controlled by firewall rules
- **DHCP:** Centralized on router per VLAN
- **DNS forwarding:** Points to Technitium DNS (10.10.20.22)

---

## Layer 2: Distribution (Managed Switch → APs)

The L2 Managed Switch carries all 4 VLANs as trunk lines to both APs.

### VLAN Assignments

| VLAN ID | Name | Subnet | Gateway | Purpose |
|---------|------|--------|---------|---------|
| 10 | Trusted | 10.10.10.0/24 | 10.10.10.1 | Personal devices, management |
| 20 | Server | 10.10.20.0/24 | 10.10.20.1 | Proxmox, LXCs, infrastructure |
| 30 | Streaming | 10.10.30.0/24 | 10.10.30.1 | Media clients (TV, AVR) |
| 40 | IoT | 10.10.40.0/24 | 10.10.40.1 | Smart home, CCTV, PoE devices |

### Switch Port Map

| Port | Device | VLAN Mode | Notes |
|------|--------|-----------|-------|
| 1 | NanoPi R3S Router | Trunk (all) | Uplink from router |
| 2 | AP1 (Xiaomi AX3600) | Trunk (all) | Entertainment zone |
| 3 | AP2 (Xiaomi AX3600) | Trunk (all) | Server/IoT zone |

---

## Layer 3: Access Points

### AP1 — Entertainment Zone

**Model:** Xiaomi AX3600 running OpenWrt (dumb AP mode)

**Uplink:** L2 Switch (trunk) → rack area

**LAN Clients (wired):**
- Sony Android TV → VLAN 10 (Trusted)
- Marantz SR5015 → VLAN 10 (Trusted)

**WiFi SSIDs:**

| SSID | Security | VLAN | Purpose |
|------|----------|------|---------|
| `nt-nw5` | WPA3-Personal (PSK) | 10 (Trusted) | Primary devices |
| `nt-nw-stm` | WPA2-Personal (PSK) | 30 (Streaming) | Media streaming |
| `nt-nw-iot` | Open (no key) | 40 (IoT) | Smart home devices |

### AP2 — Server / IoT Zone

**Model:** Xiaomi AX3600 running OpenWrt (dumb AP mode)

**Uplink:** L2 Switch (trunk) → rack area

**LAN Clients (wired):**

| Port | Device | VLAN | Purpose |
|------|--------|------|---------|
| LAN 1 | Node 1 (Proxmox HP Mini) | 20 (Server) | Virtualization host |
| LAN 2 | Dumb PoE Switch | 40 (IoT) | CCTV camera power |

**PoE Switch Downstream:**
- Hikvision NVR → CCTV recording, VLAN 40

> **Design note:** Both APs are "dumb" — no NAT, no DHCP. They bridge WiFi and wired clients directly to the managed switch VLANs. All routing and DHCP is handled by the NanoPi R3S.

---

## DNS Architecture

```
                    ┌──→ Local clients (split-horizon .lan resolution)
                    │
Internet ──→ Technitium DNS (10.10.20.22)
    ↑               │
    │               └──→ External resolution (forwarding)
    │
    └── Ad-blocking (dnsmasq-style blocklists)
```

### Technitium DNS (LXC 102)

- **Static IP:** 10.10.20.22
- **Storage:** NVMe
- **Functions:**
  - Local domain: `271224.xyz.lan` → resolves internal IPs
    - `chat.271224.xyz.lan` → 10.10.20.32 (CT 302 Open WebUI, LAN-only)
  - Ad-blocking: blocks known ad/malware domains
  - Forwarding: upstream DNS for external queries
  - Split-horizon: internal clients get local IPs, external get Cloudflare
- **API token:** Use `?token=` parameter for programmatic access
- **⚠️ Gotcha:** Never create a local A record for a subdomain that also needs to be served via Cloudflare Tunnel externally — local resolution bypasses the tunnel, causing 522 for external users. Use a different subdomain externally (e.g., `chatui` instead of `chat`).

### Caddy Reverse Proxy (LXC 103)

- **Role:** Terminates TLS, proxies `*.271224.xyz` → internal services
- **Upstream:** Cloudflare Tunnel (LXC 101) for public access
- **Key mappings:**
  - `hermes.271224.xyz` → CT 301:9119 (Hermes Dashboard SPA, direct)
  - `monitor.271224.xyz` → CT 501:8080 (Grafana + dashboard pages)
  - `chatui.271224.xyz` → CT 302:3000 (Open WebUI)
  - `joplin.271224.xyz` → CT 403 (Joplin Server)
  - `paperless.271224.xyz` → CT 402 (Paperless-NGX)
- **Internal DNS:** `chat.271224.xyz.lan` → 10.10.20.32 (Technitium .lan zone, LAN-only)
- **Reload:** `caddy reload --config /etc/caddy/Caddyfile` (NOT systemctl)
- **⚠️ Domain gotcha:** `chat.271224.xyz` had a local A record → private IP → external users got 522. Fixed by using `chatui.271224.xyz` externally (no local override → routes through Cloudflare Tunnel).

### Cloudflare Tunnel (LXC 101)

- **Role:** Securely exposes selected internal services to the internet
- **No open ports:** Outbound-only tunnel to Cloudflare
- **DNS:** Manages `271224.xyz` DNS records

---

## Firewall Rules (Summary)

### Inter-VLAN Policies

| Source → Dest | Policy | Rationale |
|---------------|--------|-----------|
| Trusted → Server | ✅ Allow | Management access to LXCs |
| Trusted → IoT | ✅ Allow | Control smart home |
| Trusted → Streaming | ✅ Allow | Media control |
| IoT → Trusted | ❌ Deny | IoT can't reach personal devices |
| IoT → Server | ❌ Deny (selective) | Restricted to NVR needs |
| IoT → Internet | ✅ Allow (restricted) | NTP, firmware updates only |
| Streaming → Internet | ✅ Allow | Netflix, etc. |
| Server → All | ✅ Allow | Infrastructure needs full access |

---

## IP Address Allocation

### Static Infrastructure IPs

| IP | Device | Purpose |
|----|--------|---------|
| 10.10.10.1 | NanoPi R3S | Router/Gateway (VLAN 10) |
| 10.10.20.1 | Router (VLAN 20 subif) | Gateway (VLAN 20) |
| 10.10.20.11 | Proxmox Node 1 | Hypervisor host (pve1.271224.xyz.lan) |
|| 10.10.20.22 | LXC 102 | Technitium DNS |
|| 10.10.20.32 | LXC 302 | Open WebUI (chatui.271224.xyz) |
|| 10.10.20.44 | LXC 404 | Autocaliweb (CWA) |
|| 10.10.20.51 | LXC 501 | Monitor |
| 10.10.30.1 | Router (VLAN 30 subif) | Gateway (VLAN 30) |
| 10.10.40.1 | Router (VLAN 40 subif) | Gateway (VLAN 40) |

### DHCP Ranges

| VLAN | Range | Lease |
|------|-------|-------|
| 10 | 10.10.10.100 – 10.10.10.200 | 12 hours |
| 20 | 10.10.20.100 – 10.10.20.200 | 24 hours |
| 30 | 10.10.30.100 – 10.10.30.200 | 12 hours |
| 40 | 10.10.40.100 – 10.10.40.200 | 1 hour (short-lived IoT) |

---

## Future Expansion

### Planned Changes

1. **Node 2 (Frigate NVR):** Dedicated Proxmox node for AI-powered CCTV analysis
   - DAS storage via USB-C passthrough
   - Intel QuickSync for hardware-accelerated inference

2. **Additional LXCs** (as needed):
   - Home automation hub
   - Media server
   - Backup target

3. **Rack expansion:** Currently 12U; may expand to 16U if DAS grows
