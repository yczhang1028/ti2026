#!/bin/bash
# 渲染 HTML(含 analysis.md) 并 push GitHub Pages
# 用法: render_and_push.sh [analysis.md路径]
set -uo pipefail
BASE="$HOME/hermes_share/ti2026"
ANALYSIS="${1:-$BASE/analysis.md}"
cd "$HOME/.hermes/scripts"

python3 render_ti2026.py "$BASE/data/data.json" "$BASE/logos" "$BASE/index.html" "$ANALYSIS" || { echo "渲染失败"; exit 1; }
bash "$BASE/push_to_pages.sh"
echo "✓ 已发布 https://yczhang1028.github.io/ti2026/"
