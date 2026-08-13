#!/bin/bash
# 诊断 + 重新触发 GitHub Pages
set -euo pipefail
TOKEN=$(grep GITHUB_TOKEN "$HOME/.github/.env" | cut -d= -f2 | tr -d '\n\r ')
OWNER="yczhang1028"; REPO="ti2026"

echo "=== 1. Pages 配置状态 ==="
curl -s -H "Authorization: Bearer $TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pages" | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('status'), '| html_url:', d.get('html_url'), '| source:', d.get('source'), '| msg:', d.get('message'))"

echo "=== 2. 默认分支 ==="
curl -s -H "Authorization: Bearer $TOKEN" "https://api.github.com/repos/$OWNER/$REPO" | python3 -c "import json,sys; d=json.load(sys.stdin); print('default_branch:', d.get('default_branch'), '| has_pages:', d.get('has_pages'))"

echo "=== 3. 重新配置 Pages (main 分支) ==="
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "https://api.github.com/repos/$OWNER/$REPO/pages" \
  -d '{"source":{"branch":"main","path":"/"}}' | python3 -c "import json,sys; d=json.load(sys.stdin); print('result:', d.get('status') or d.get('html_url') or d.get('message'))"

echo "=== 4. 请求重建 ==="
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$OWNER/$REPO/pages/builds" | python3 -c "import json,sys; d=json.load(sys.stdin); print('build status:', d.get('status'), '| msg:', d.get('message'))"
