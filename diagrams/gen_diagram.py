#!/usr/bin/env python3
"""Network diagram generator for house-infrastructure repo."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(22, 16))
ax.set_xlim(0, 22)
ax.set_ylim(0, 16)
ax.axis('off')
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')

# Color palette
C = {
    'bg':      '#0d1117',
    'edge':    '#21262d',
    'primary': '#58a6ff',   # blue
    'green':   '#3fb950',
    'orange':  '#d29922',
    'red':     '#f85149',
    'purple':  '#bc8cff',
    'cyan':    '#39d2c0',
    'yellow':  '#f0c74f',
    'white':   '#e6edf3',
    'dim':     '#8b949e',
    'vlan10':  '#58a6ff',   # Trusted
    'vlan20':  '#3fb950',   # Server
    'vlan30':  '#d29922',   # Streaming
    'vlan40':  '#bc8cff',   # IoT
}

def box(ax, x, y, w, h, label, sublabel=None, color='#21262d', border='#30363d',
        textcolor='#e6edf3', fontsize=9.5, fontweight='bold', alpha=0.95):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor=border,
                          linewidth=1.5, alpha=alpha)
    ax.add_patch(rect)
    ty = y + (0.15 if sublabel else 0)
    ax.text(x, ty, label, ha='center', va='center', fontsize=fontsize,
            fontweight=fontweight, color=textcolor, zorder=5,
            fontfamily='monospace')
    if sublabel:
        ax.text(x, y - 0.22, sublabel, ha='center', va='center',
                fontsize=7.5, color=C['dim'], zorder=5, fontfamily='monospace')

def arrow(ax, x1, y1, x2, y2, color='#30363d', lw=2, style='->', label=None, linestyle=None):
    ap = dict(arrowstyle=style, color=color, lw=lw,
              connectionstyle='arc3,rad=0.0')
    if linestyle:
        ap['linestyle'] = linestyle
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=ap)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.1, my, label, fontsize=7, color=C['dim'],
                fontfamily='monospace', zorder=6)

def zone_bg(ax, x, y, w, h, label, color, alpha=0.06):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.15",
                          facecolor=color, edgecolor=color,
                          linewidth=1, alpha=alpha, linestyle='dashed')
    ax.add_patch(rect)
    ax.text(x + w/2, y + h + 0.25, label, ha='center', va='center',
            fontsize=9, color=color, fontweight='bold', alpha=0.8)

# ── Title ──
ax.text(11, 15.5, 'THE SOVEREIGN FORTRESS', ha='center', va='center',
        fontsize=18, fontweight='bold', color=C['white'], fontfamily='monospace')
ax.text(11, 15.05, 'Home Infrastructure — Network Topology', ha='center', va='center',
        fontsize=10, color=C['dim'], fontfamily='monospace')

# ── Zone backgrounds ──
zone_bg(ax, 0.3, 11.5, 4.4, 3.9, 'EDGE / WAN', C['red'])
zone_bg(ax, 5.3, 11.5, 4.4, 3.9, 'CORE NETWORK', C['primary'])
zone_bg(ax, 10.3, 10.5, 5.4, 4.9, 'SERVER ZONE (VLAN 20)', C['green'])
zone_bg(ax, 16.2, 10.5, 5.4, 4.9, 'AP1 — TRUSTED / STREAMING', C['vlan30'])
zone_bg(ax, 16.2, 5.5, 5.4, 4.5, 'AP2 — SERVER / IoT', C['vlan40'])
zone_bg(ax, 0.3, 5.5, 5.4, 5.5, 'IoT / CCTV', C['purple'])

# ── ISP / WAN ──
box(ax, 2.5, 14.2, 3.2, 0.8, 'ISP WAN', 'Fiber / DSL',
    color='#161b22', border=C['red'], fontsize=9)
box(ax, 2.5, 12.7, 3.2, 1.0, 'NanoPi R3S', 'OpenWrt Router',
    color='#161b22', border=C['red'])
ax.text(2.5, 12.25, '10.10.10.1', ha='center', va='center',
        fontsize=7.5, color=C['red'], fontfamily='monospace')

# ── Core Switch ──
box(ax, 7.5, 13.8, 3.0, 1.2, 'L2 Managed Switch', 'VLAN Trunking',
    color='#161b22', border=C['primary'])
ax.text(7.5, 13.25, 'VLAN 10 | 20 | 30 | 40', ha='center', va='center',
        fontsize=7.5, color=C['primary'], fontfamily='monospace')

# ── Arrows: ISP → Router → Switch ──
arrow(ax, 2.5, 13.5, 2.5, 13.0, color=C['red'], lw=2.5)
arrow(ax, 4.1, 12.7, 6.0, 13.5, color=C['primary'], lw=2.5)

# ── AP1 (Trust + Stream VLANs) ──
box(ax, 18.9, 14.5, 3.8, 1.2, 'AP1 — Xiaomi AX3600', 'OpenWrt Dumb AP',
    color='#161b22', border=C['vlan30'])
# SSIDs
box(ax, 17.5, 13.2, 2.2, 0.65, 'nt-nw5', 'WPA3 — VLAN 10',
    color='#161b22', border=C['vlan10'], fontsize=8)
box(ax, 18.9, 13.2, 2.2, 0.65, 'nt-nw-stm', 'WPA2 — VLAN 30',
    color='#161b22', border=C['vlan30'], fontsize=8)
box(ax, 20.6, 13.2, 1.8, 0.65, 'nt-nw-iot', 'Open — VLAN 40',
    color='#161b22', border=C['vlan40'], fontsize=8)
arrow(ax, 9.0, 13.8, 17.0, 14.5, color=C['vlan30'], lw=2)

# AP1 LAN clients
box(ax, 17.5, 11.9, 2.4, 0.65, 'Sony Android TV', 'AP1 LAN',
    color='#161b22', border=C['orange'], fontsize=8)
box(ax, 20.3, 11.9, 2.4, 0.65, 'Marantz SR5015', 'AP1 LAN',
    color='#161b22', border=C['orange'], fontsize=8)
ax.annotate('', xy=(18.9, 13.9), xytext=(18.9, 13.55),
            arrowprops=dict(arrowstyle='->', color=C['orange'], lw=1.5))

# ── AP2 (Server + IoT VLANs) ──
box(ax, 18.9, 9.0, 3.8, 1.2, 'AP2 — Xiaomi AX3600', 'OpenWrt Dumb AP',
    color='#161b22', border=C['vlan40'])
arrow(ax, 9.0, 13.4, 17.0, 9.0, color=C['green'], lw=2)

# AP2 LAN: Node 1
box(ax, 17.5, 7.4, 2.6, 0.65, 'Node 1 — Proxmox', 'HP EliteDesk 800 G3',
    color='#161b22', border=C['green'], fontsize=8)

# AP2 LAN: PoE Switch → NVR
box(ax, 20.4, 7.4, 2.6, 0.55, 'Dumb PoE Switch', 'IoT VLAN',
    color='#161b22', border=C['purple'], fontsize=8)
box(ax, 20.4, 6.2, 2.6, 0.65, 'Hikvision NVR', 'CCTV Recording',
    color='#161b22', border=C['red'], fontsize=8)
arrow(ax, 18.9, 8.4, 18.9, 7.75, color=C['vlan40'], lw=1.5)
arrow(ax, 20.4, 7.1, 20.4, 6.55, color=C['purple'], lw=1.5)

# Node 1 → PoE (indirect via AP2 trunk, shown for clarity)
ax.annotate('', xy=(17.5, 7.05), xytext=(20.4, 7.1),
            arrowprops=dict(arrowstyle='->', color=C['dim'], lw=1, linestyle='dashed'))

# ── Server Zone: Proxmox LXCs ──
box(ax, 13.0, 14.8, 4.2, 0.85, 'LXC 301 — Hermes Agent', 'CT 301 (NVMe)',
    color='#161b22', border=C['cyan'], fontsize=8.5)
box(ax, 11.8, 13.8, 3.0, 0.65, 'LXC 101 — Cloudflared', 'Tunnel',
    color='#161b22', border=C['cyan'], fontsize=8)
box(ax, 14.2, 13.8, 3.0, 0.65, 'LXC 102 — Technitium DNS', '10.10.20.22',
    color='#161b22', border=C['cyan'], fontsize=8)
box(ax, 11.8, 12.9, 3.0, 0.65, 'LXC 103 — Caddy', 'Reverse Proxy',
    color='#161b22', border=C['cyan'], fontsize=8)
box(ax, 14.2, 12.9, 3.0, 0.65, 'LXC 105 — Jump Server', 'SSH Bastion',
    color='#161b22', border=C['cyan'], fontsize=8)
box(ax, 11.8, 12.0, 3.0, 0.65, 'LXC 401 — BentoPDF', 'PDF Editor',
    color='#161b22', border=C['cyan'], fontsize=8)
box(ax, 14.2, 12.0, 3.0, 0.65, 'LXC 402 — Paperless-NGX', 'Documents',
    color='#161b22', border=C['cyan'], fontsize=8)
arrow(ax, 17.0, 9.0, 13.0, 14.3, color=C['green'], lw=1.5, linestyle='dashed')

# ── DNS ──
box(ax, 13.0, 10.5, 4.0, 1.0, 'Technitium DNS', 'Ad-block + Split-horizon',
    color='#161b22', border=C['yellow'])
ax.text(13.0, 10.15, '10.10.20.22  |  271224.xyz.lan', ha='center', va='center',
        fontsize=7.5, color=C['yellow'], fontfamily='monospace')

# ── Domain ──
box(ax, 7.5, 9.0, 3.5, 0.85, 'Domain: 271224.xyz', 'Public + .lan split',
    color='#161b22', border=C['yellow'])

# ── Timezone / Location ──
ax.text(7.5, 7.5, 'Asia/Bangkok', ha='center', va='center',
        fontsize=9, color=C['dim'], fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#161b22', edgecolor='#21262d'))
ax.text(7.5, 7.0, 'Thailand  TH', ha='center', va='center',
        fontsize=8, color=C['dim'])

# ── Hermes Profiles ──
box(ax, 4.0, 8.5, 4.2, 2.4, '', color='#161b22', border=C['cyan'])
ax.text(4.0, 9.85, 'HERMES AGENTS', ha='center', va='center',
        fontsize=9, fontweight='bold', color=C['cyan'], fontfamily='monospace')
ax.text(4.0, 9.35, 'buddy  |  investor  |  trader', ha='center', va='center',
        fontsize=8, color=C['dim'], fontfamily='monospace')
ax.text(4.0, 8.9, 'monitor  |  financialanalyst (Tae + Nhoo)', ha='center', va='center',
        fontsize=8, color=C['dim'], fontfamily='monospace')
ax.text(4.0, 8.35, 'Hindsight API: 127.0.0.1:8888', ha='center', va='center',
        fontsize=7.5, color=C['green'], fontfamily='monospace')
ax.text(4.0, 7.95, 'PostgreSQL 16 + pgvector', ha='center', va='center',
        fontsize=7.5, color=C['dim'], fontfamily='monospace')

# ── Future: Node 2 + Frigate ──
box(ax, 4.0, 4.5, 4.2, 1.5, '⚡ FUTURE: Node 2 — Frigate NVR', 'HP EliteDesk 800 G3 Mini',
    color='#161b22', border=C['dim'], textcolor=C['dim'], fontsize=8.5)
ax.text(4.0, 4.0, 'AI Object Detection  +  DAS via USB-C', ha='center', va='center',
        fontsize=7, color=C['dim'], fontfamily='monospace')

# ── Legend ──
legend_items = [
    (C['vlan10'], 'VLAN 10 — Trusted (10.10.10.0/24)'),
    (C['vlan20'], 'VLAN 20 — Server  (10.10.20.0/24)'),
    (C['vlan30'], 'VLAN 30 — Streaming (10.10.30.0/24)'),
    (C['vlan40'], 'VLAN 40 — IoT (10.10.40.0/24)'),
    (C['cyan'],   'Hermes / LXC'),
    (C['yellow'], 'DNS / Domain'),
    (C['red'],    'WAN / CCTV'),
]
for i, (c, l) in enumerate(legend_items):
    ax.plot(0.6, 4.5 - i*0.35, 's', color=c, markersize=8, transform=ax.transData)
    ax.text(0.9, 4.5 - i*0.35, l, fontsize=7.5, color=C['dim'],
            va='center', fontfamily='monospace')

plt.tight_layout(pad=0.3)
plt.savefig('/root/house-infrastructure/diagrams/network-topology.svg',
            format='svg', bbox_inches='tight', facecolor='#0d1117',
            edgecolor='none', dpi=150)
plt.savefig('/root/house-infrastructure/diagrams/network-topology.png',
            format='png', bbox_inches='tight', facecolor='#0d1117',
            edgecolor='none', dpi=150)
print("Diagrams saved: network-topology.svg + network-topology.png")
