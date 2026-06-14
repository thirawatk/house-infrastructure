# Hardware Inventory

Last updated: 2026-06-14

## Compute

### Node 1 — Proxmox Virtualization Host

| Attribute | Specification |
|-----------|---------------|
| **Model** | HP EliteDesk 800 G3 Mini |
| **Form Factor** | Ultra Small Form Factor (USFF) |
| **CPU** | Intel Core i5-6500 (4C/4T, 3.2GHz, Skylake) with Intel QuickSync iGPU |
| **RAM** | 32 GB |
| **OS Storage** | 512GB Hiksemi E3000 M.2 NVMe SSD |
| **Data Storage** | 1TB Samsung EVO 960 SATA SSD |
| **NIC 1** | Onboard Intel 1 GbE → Proxmox management |
| **NIC 2** | Expansion 2.5 GbE → Production LAN bridge |
| **Hypervisor** | Proxmox VE |
| **LXC Count** | 10 containers |
| **Location** | Rack (cantilever shelf, side-by-side with Node 2) |

#### Storage Pools

| Pool Name | Disk | Size | Contents |
|-----------|------|------|----------|
| `local-e3000-512gb` | Hiksemi E3000 NVMe M.2 | 512 GB | Proxmox OS, LXC root filesystems |
| `local-samsung-1tb` (ssd-vault) | Samsung EVO 960 SATA SSD | 1 TB | App data, document DBs, Hindsight |

#### NIC Mapping

| NIC | Bridge | VLAN | Purpose |
|-----|--------|------|---------|
| eno1 (onboard 1G) | vmbr0 | Management | Proxmox Web GUI, SSH |
| enp0s25 (added 2.5G) | vmbr1 | Trunk | All LXC traffic |

---

### Node 2 — Frigate NVR / HA Secondary

| Attribute | Specification |
|-----------|---------------|
| **Model** | HP EliteDesk 800 G3 Mini (identical to Node 1) |
| **CPU** | Intel Core i5-6500 (4C/4T, 3.2GHz, Skylake) with Intel QuickSync |
| **RAM** | 32 GB |
| **OS Storage** | 256GB SATA SSD |
| **Data Storage** | 2TB M.2 NVMe SSD |
| **Role** | Frigate NVR (AI object detection for CCTV) + HA secondary node |
| **GPU** | Intel QuickSync iGPU (passthrough for Frigate AI inference) |
| **Location** | Rack (cantilever shelf, side-by-side with Node 1) |

---

### DAS — External Storage (Idle)

| Attribute | Specification |
|-----------|---------------|
| **Type** | Multi-bay 2.5"/3.5" SATA desktop tower enclosure |
| **Capacity** | 4 TB |
| **Connection** | USB-C → Proxmox USB passthrough |
| **Status** | **Idle** — available for backup/bulk storage |
| **Potential Uses** | Proxmox backup target, Frigate video retention, bulk data, Kavita library overflow |
| **Location** | Rack (vertically mounted, platter health) |

---

## Cluster Resources Summary

| Resource | Node 1 | Node 2 | Total |
|----------|--------|--------|-------|
| CPU | i5-6500 (4C/4T) | i5-6500 (4C/4T) | **8C/8T** |
| RAM | 32 GB | 32 GB | **64 GB** |
| NVMe | 512 GB | 2 TB | **2.5 TB** |
| SATA SSD | 1 TB | 256 GB | **1.25 TB** |
| DAS | — | — | **4 TB** |
| **Total Storage** | | | **~7.75 TB** |

---

## Network

### Router / QDevice

| Attribute | Specification |
|-----------|---------------|
| **Model** | NanoPi R3S |
| **OS** | OpenWrt (standalone) |
| **CPU** | Rockchip RK3328 (ARM) |
| **RAM** | 1 GB DDR4 |
| **NIC 1** | USB 3.0 → 1 GbE (WAN) |
| **NIC 2** | Native 1 GbE (LAN/trunk) |
| **Primary Role** | Core router, firewall, inter-VLAN routing, DHCP |
| **Secondary Role** | **QDevice** (corosync-qnetd) for 2-node Proxmox cluster quorum |
| **Location** | Rack (cantilever shelf, next to ISP modem) |

### Managed Switch

| Attribute | Specification |
|-----------|---------------|
| **Layer** | L2 Managed |
| **Ports** | 8+ GbE (with VLAN support) |
| **Features** | 802.1Q VLAN tagging, trunking |
| **Role** | Core switching, VLAN distribution |
| **Location** | Rack (1U, native mount) |

### Access Points

#### AP1 — Entertainment Zone

| Attribute | Specification |
|-----------|---------------|
| **Model** | Xiaomi AX3600 |
| **OS** | OpenWrt (dumb AP mode) |
| **WiFi** | WiFi 6 (AX), dual-band |
| **Backhaul** | Wired (GbE trunk) |
| **Location** | Living room area |
| **SSIDs** | nt-nw5 (WPA3), nt-nw-stm (WPA2), nt-nw-iot (open) |

**Wired Clients:**
- Sony Android TV (VLAN 10)
- Marantz SR5015 AVR (VLAN 10)

#### AP2 — Server / IoT Zone

| Attribute | Specification |
|-----------|---------------|
| **Model** | Xiaomi AX3600 |
| **OS** | OpenWrt (dumb AP mode) |
| **WiFi** | WiFi 6 (AX), dual-band |
| **Backhaul** | Wired (GbE trunk) |
| **Location** | Near rack |
| **SSIDs** | *(configured for server/IoT use)* |

**Wired Clients:**
- Node 1 Proxmox (VLAN 20, direct LAN port)
- Dumb PoE Switch → Hikvision NVR (VLAN 40)

### PoE Switch (Dumb)

| Attribute | Specification |
|-----------|---------------|
| **Type** | Unmanaged PoE Switch |
| **Standard** | 802.3af/at |
| **Role** | Power Hikvision CCTV cameras |
| **Location** | Rack (cantilever shelf) |

---

## Client Devices

| Device | Connection | IP Range | VLAN | Purpose |
|--------|-----------|----------|------|---------|
| Sony Android TV | AP1 LAN (wired) | 10.10.10.x | 10 | Entertainment |
| Marantz SR5015 | AP1 LAN (wired) | 10.10.10.x | 10 | Audio/Video Receiver |
| Hikvision NVR | PoE Switch | 10.10.40.x | 40 | CCTV recording |

---

## Cabinet & Power

### Rack

| Attribute | Specification |
|-----------|---------------|
| **Type** | 12U Vertical Cabinet |
| **Min Depth** | 600mm (DAS clearance + ventilation) |

### UPS

| Attribute | Specification |
|-----------|---------------|
| **Type** | Line-interactive or online UPS |
| **Capacity** | *(to be determined by load calculation)* |
| **Runtime Target** | ~15 min full load (graceful shutdown) |
| **Location** | Base of rack (2U) |

### PDU

| Attribute | Specification |
|-----------|---------------|
| **Type** | Rackmount PDU |
| **Outlets** | 8+ (to be confirmed) |
| **Location** | Top of rack (1U) |

---

## Cable Inventory (Key Runs)

| From | To | Cable | Purpose |
|------|----|-------|---------|
| ISP Modem | NanoPi R3S (WAN) | Cat6 | WAN uplink |
| NanoPi R3S (LAN) | Managed Switch | Cat6 | Trunk (all VLANs) |
| Managed Switch | AP1 | Cat6 | Trunk (all VLANs) |
| Managed Switch | AP2 | Cat6 | Trunk (all VLANs) |
| AP1 LAN | Sony TV | Cat6 | Entertainment |
| AP1 LAN | Marantz SR5015 | Cat6 | Audio |
| AP2 LAN | Node 1 (2.5G NIC) | Cat6 | Production LAN |
| AP2 LAN | PoE Switch | Cat6 | IoT/CCTV |
| Patch Panel | PoE Switch | Cat6 | CCTV camera drops |
