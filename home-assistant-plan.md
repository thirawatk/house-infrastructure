# Home Assistant Deployment Plan (AC Control Focus)

> Created: 2026-08-13 · Status: PLANNED · Owner: buddy
> Goal: Rich, reliable smart-AC control + automation, independent of Tuya cloud.

## 1. Deployment — HA in LXC on Proxmox (pve1, 10.10.20.11)

| Item | Value |
|---|---|
| LXC ID | 601 (next free) |
| Template | Ubuntu 24.04 (or Debian 13) — use existing template cache |
| vCPU / RAM / Disk | 2 vCPU / 4 GB RAM / 32 GB on ssd-vault |
| Network | VLAN 20 (Server), static 10.10.20.61/24, GW 10.10.20.1, DNS 10.10.20.22 |
| Nesting | enabled (Docker-in-LXC if HA via docker; else HAOS VM not needed — containerized HA Core + supervisor alternatives) |
| Install | HA Container (Docker): `ghcr.io/home-assistant/home-assistant:stable` |
| Ports | 8123 (HA web), firewall: allow from Trust (10.10.10/24) + Server only |

Alternative: HAOS VM (full supervisor + add-ons) — heavier, more robust. Decision point.

## 2. Integrations (HACS + built-in)

1. **Local Tuya** (HACS) — control the 3 Gubei/Tuya ACs directly, two-way state, no cloud
   - Need: Tuya IoT project (developer.tuya.com), device local keys (via tuya-local key extraction — python script on LAN or cloud API)
   - Entities: climate per AC (mode/temp/fan/swing) — replaces ACFreedom app as primary UI
2. **Broadlink** (built-in) — RM4 Mini IR blasters as fallback/insurance
   - One RM4 Mini per room (Family/Bedroom/Office), on nt-nw-iot VLAN 40
   - Pair: Broadlink app → AC mode → brand database → test beep
   - HA climate entity via integration (auto-discovered)
3. **Node-RED** (HACS/add-on) — automation flows (presence, schedules)
4. Voice pipeline: Whisper + Piper + OpenWakeWord (local, no cloud)

## 3. Smart-AC entity map

| AC | Room | Tuya climate | RM4 Mini fallback | WiFi status |
|---|---|---|---|---|
| AC1 (...53:24) | Family | Local Tuya | RM4-Family | AP1 |
| AC2 (...9b:ce) | Bedroom | Local Tuya | RM4-Bedroom | AP2 (pinned) |
| AC3 (...89:72) | Office | Local Tuya | RM4-Office | OFFLINE — power cycle pending |

Automation: if Tuya climate unavailable > 10 min → switch control to Broadlink IR entity (fallback), alert via Telegram.

## 4. Acquisition list (buy when ready)

| Item | Qty | Est. THB | Notes |
|---|---|---|---|
| Broadlink RM4 Mini | 3 | ~500 ea | IR fallback per room; needs line-of-sight to AC indoor unit |
| (Optional) Tuya-compatible smart relay/contactor | 3 | ~300–800 ea | Auto power-cycle if drops recur post-fix — electrician for 220V |
| Nothing else | — | — | HA itself is free/self-hosted |

## 5. Rollout order

1. Recover AC3 (power cycle) — verify joins AP1 (pinned)
2. Deploy HA LXC (601) + Docker + port/firewall
3. Local Tuya: create Tuya IoT project → extract local keys → configure 3 climates
4. Buy + pair 3× RM4 Mini (Broadlink app → AC mode → brand codes)
5. Node-RED automations: presence-based AC control, fallback switchover, Telegram alerts
6. Verify: HA climate cards + fallback drill (kill Tuya entity → IR takes over)

## 6. Open questions

- HAOS VM vs HA Container LXC? (VM = add-ons like Node-RED easier; LXC = lighter, our style)
- Tuya local key extraction: cloud API route (needs Tuya dev account) vs LAN script (tuya-local `tuya_localkey` tool) — LAN preferred, no cloud
- AC brand for RM4 code database — check nameplate when at the units
