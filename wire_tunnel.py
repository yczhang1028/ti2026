#!/usr/bin/env python3
"""为 TI2026 加 Cloudflare tunnel hostname: ti2026.knownothing.dpdns.org -> 127.0.0.1:18766"""
import base64, json, os, urllib.request

tok = open(os.path.expanduser("~/.cloudflare/tunnel_token.txt")).read().strip()
dec = json.loads(base64.b64decode(tok + "=" * (-len(tok) % 4)))
acct = dec["a"]
tun = dec["t"]

env = {}
for line in open(os.path.expanduser("~/.cloudflare/.env")):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
api_token = env.get("CLOUDFLARE_API_TOKEN") or env.get("CLOUDFLARE_TOKEN") or env.get("CLOUDFLARE_API_KEY")

def cf(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=data, method=method,
        headers={"Authorization": "Bearer " + api_token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())

HOST = "ti2026.knownothing.dpdns.org"
PORT = "18766"

# 1. 找 zone
zones = cf("/zones")
zone_id = None
for z in zones.get("result", []):
    if z.get("name") == "knownothing.dpdns.org":
        zone_id = z["id"]
        break
if not zone_id:
    print("ERROR: 找不到 zone knownothing.dpdns.org"); raise SystemExit(1)
print(f"zone_id: {zone_id}")

# 2. 加 DNS CNAME
dns = cf(f"/zones/{zone_id}/dns_records", "POST",
         {"type": "CNAME", "name": HOST, "content": f"{tun}.cfargotunnel.com", "proxied": True})
if dns.get("success"):
    print(f"DNS 记录已创建: {HOST} -> {tun}.cfargotunnel.com")
else:
    print("DNS 记录:", json.dumps(dns.get("errors"), ensure_ascii=False))

# 3. 更新 tunnel ingress (在 default 前插入新 hostname)
cfg = cf(f"/accounts/{acct}/cfd_tunnel/{tun}/configurations")
ing = (cfg.get("result") or {}).get("config", {}).get("ingress", [])
new_ing = [e for e in ing if e.get("hostname") != HOST]
insert = {"hostname": HOST, "service": f"http://127.0.0.1:{PORT}"}
# 插到 default (http_status:404) 之前
if new_ing and new_ing[-1].get("service") == "http_status:404":
    new_ing.insert(-1, insert)
else:
    new_ing.append(insert)
    new_ing.append({"service": "http_status:404"})

upd = cf(f"/accounts/{acct}/cfd_tunnel/{tun}/configurations", "PUT",
         {"config": {"ingress": new_ing}})
if upd.get("success"):
    print(f"ingress 已更新, 新增 {HOST} -> 127.0.0.1:{PORT}")
else:
    print("ingress 更新失败:", json.dumps(upd.get("errors"), ensure_ascii=False))

print("\n=== 当前 ingress ===")
for e in new_ing:
    print(f"  {e.get('hostname','(default)')!r:40s} -> {e.get('service')}")
