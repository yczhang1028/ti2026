#!/usr/bin/env python3
"""查询 TI2026 tunnel 现有 ingress 配置 + 现有 hostname"""
import base64, json, os, urllib.request

tok = open(os.path.expanduser("~/.cloudflare/tunnel_token.txt")).read().strip()
dec = json.loads(base64.b64decode(tok + "=" * (-len(tok) % 4)))
acct = dec["a"]
tun = dec["t"]

# API token 从 .env 读
env = {}
for line in open(os.path.expanduser("~/.cloudflare/.env")):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
api_token = env.get("CLOUDFLARE_API_TOKEN") or env.get("CLOUDFLARE_TOKEN") or env.get("CLOUDFLARE_API_KEY")

def cf(path):
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        headers={"Authorization": "Bearer " + api_token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())

# 1. tunnel 配置
try:
    cfg = cf(f"/accounts/{acct}/cfd_tunnel/{tun}/configurations")
    ing = (cfg.get("result") or {}).get("config", {}).get("ingress", [])
    print("=== tunnel ingress ===")
    for e in ing:
        print(f"  {e.get('hostname','(default)')!r:40s} -> {e.get('service')}")
except Exception as ex:
    print("tunnel 配置查询失败:", ex)

# 2. 该 zone 下所有 DNS 记录
print("\n=== DNS 记录 (knownothing.dpdns.org) ===")
try:
    zones = cf("/zones")
    for z in zones.get("result", []):
        zn = z.get("name", "")
        if "dpdns.org" in zn or "knownothing" in zn:
            zid = z["id"]
            recs = cf(f"/zones/{zid}/dns_records?per_page=100")
            for r in recs.get("result", []):
                print(f"  {z['name']:30s} {r['type']:6s} {r['name']:40s} -> {r['content']} (proxied={r.get('proxied')})")
except Exception as ex:
    print("DNS 查询失败:", ex)
