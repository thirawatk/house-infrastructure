# Kavita eBook Server — Ops Reference

**CT 404 (autocaliweb, 10.10.20.44)** — Docker container running Kavita + rclone for OneDrive sync.

## Access Pattern

```bash
# From CT 301 → pve1 → CT 404:
ssh root@10.10.20.11 "pct exec 404 -- bash -c '<command>'"
# From CT 301 → pve1 → CT 404 (docker):
ssh root@10.10.20.11 "pct exec 404 -- docker exec kavita <command>"
```

SSH key: `id_ed25519` on CT 301 (used to reach pve1 at 10.10.20.11).

## Docker Container Spec

```
Name: kavita
Image: jvmilazz0/kavita:0.9.0.2
Restart: unless-stopped
Port: 0.0.0.0:5000 -> 5000/tcp
Env: TZ=Asia/Bangkok
Mounts:
  /opt/kavita/data:/kavita/config       (Kavita DB, settings, backups)
  /mnt/calibre/library:/books            (book files, 7.7GB, 580 files)
```

## Upgrade Process

```bash
ssh root@10.10.20.11 "pct exec 404 -- bash -c 'docker pull jvmilazz0/kavita:latest'"
ssh root@10.10.20.11 "pct exec 404 -- bash -c 'docker stop kavita && docker rm kavita'"
ssh root@10.10.20.11 "pct exec 404 -- docker run -d --name kavita --restart unless-stopped -e TZ=Asia/Bangkok -p 5000:5000 -v /opt/kavita/data:/kavita/config -v /mnt/calibre/library:/books jvmilazz0/kavita:latest'"
```

Data persists across upgrades because `/opt/kavita/data` is a bind mount to the host.

## OPDS Configuration

**OPDS URL:** `https://kavita.271224.xyz/api/opds/72900210-ab5d-4d67-95ed-df695109e070`

| Version | Route Format |
|---------|-------------|
| 0.8.x | `/api/opds?apiKey=<key>` (query param) |
| 0.9.x | `/api/opds/<key>` (path param) |

**API Key:** `72900210-ab5d-4d67-95ed-df695109e070` (stored in `AspNetUsers.ApiKey` in SQLite DB)

**OPDS root links:** on-deck, recently-updated, recently-added, reading-list, want-to-read, libraries, collections, search

**OPDS-PS (Progress Sync):** NOT SUPPORTED. Kavita's OPDS feed is read-only.

## Kavita API Auth

```bash
# Login to get JWT token
curl -s -X POST http://localhost:5000/api/Account/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"lottez","password":"Th!2awatKVT"}'
# Returns: {"token": "eyJ...", ...}
```

## Library Scan

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/Account/login -H 'Content-Type: application/json' -d '{"username":"lottez","password":"Th!2awatKVT"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
curl -s -X POST "http://localhost:5000/api/Library/scan?libraryId=1" -H "Authorization: Bearer $TOKEN"
```

## rclone OneDrive Sync

| Item | Value |
|------|-------|
| Remote | `onedrive:Personal_stuff/e-book/` |
| Local | `/mnt/calibre/library/` |
| drive_id | `847FBA794A95EBF0` |
| drive_type | personal |
| Cron | Every 6 hours: `0 */6 * * *` |
| Log | `/var/log/rclone-sync.log` |
| Config | `/root/.config/rclone/rclone.conf` on CT 404 |

## Reading Progress Sync

| Method | Works? | Notes |
|--------|--------|-------|
| Moon Reader → Kavita via OPDS-PS | ❌ | Kavita doesn't support OPDS-PS |
| Moon Reader Google Drive sync | Moon-to-Moon only | User's choice for progress sync |
| Kavita web reader | ✅ | Progress saved to Kavita natively |
| Panels/Kybook apps | ✅ | Native Kavita API with progress sync |

## Caddy Route (CT 103)

```
kavita.271224.xyz {
    import cloudflare_tls
    reverse_proxy http://10.10.20.44:5000 {
        header_up Host {upstream_hostport}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

## Shell Quoting Pitfall

Running complex Python/JSON via `pct exec 404 -- bash -c '...'` fails due to nested quote escaping. The reliable workaround is **base64 encoding**:

```python
import subprocess, base64
script = open("/tmp/myscript.py").read()
encoded = base64.b64encode(script.encode()).decode()
cmd = f"pct exec 404 -- bash -c \"echo {encoded} | base64 -d | python3\""
result = subprocess.run(["ssh", "root@10.10.20.11", cmd], capture_output=True, text=True, timeout=30)
```
