#!/bin/bash
# TI2026 发布: 把 analysis.md 合并进 data.json, 推送 GitHub Pages
set -uo pipefail
BASE="$HOME/hermes_share/ti2026"

# 1. 合并 analysis.md 到 data.json (若 agent 已写 analysis.md)
python3 - "$BASE" <<'EOF'
import json, sys, os
base = sys.argv[1]
data_path = os.path.join(base, "data.json")
ap = os.path.join(base, "analysis.md")
d = json.load(open(data_path))
if os.path.exists(ap) and os.path.getsize(ap) > 0:
    d["analysis"] = open(ap).read().strip()
else:
    d["analysis"] = ""
json.dump(d, open(data_path, "w"), ensure_ascii=False, indent=2)
print(f"✓ analysis 已合并 (长度 {len(d['analysis'])})")
EOF

# 2. 推送
bash "$BASE/push_to_pages.sh"
