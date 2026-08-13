#!/bin/bash
# TI2026 每日战报更新: 抓数据 -> 下载队标 -> 渲染 HTML -> push GitHub Pages
set -uo pipefail
BASE="$HOME/hermes_share/ti2026"
cd "$HOME/.hermes/scripts"

# 1. 抓数据 (JSON) + 下载队标
python3 ti2026.py --json --logo-dir "$BASE/logos" > "$BASE/data/data.json" 2>/tmp/ti2026_err.log || {
  echo "抓取失败:"; cat /tmp/ti2026_err.log; exit 1
}

# 2. 渲染 HTML
python3 render_ti2026.py "$BASE/data/data.json" "$BASE/logos" "$BASE/index.html" || {
  echo "渲染失败"; exit 1
}

# 3. push
bash "$BASE/push_to_pages.sh"

echo "DONE"
