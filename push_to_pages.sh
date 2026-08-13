#!/bin/bash
# 创建 ti2026 GitHub Pages 仓库 + 推送战报 HTML
set -euo pipefail
TOKEN=$(grep GITHUB_TOKEN "$HOME/.github/.env" | cut -d= -f2 | tr -d '\n\r ')
OWNER="yczhang1028"
REPO="ti2026"

# 1. 建仓库 (若不存在)
if ! curl -s -H "Authorization: Bearer $TOKEN" "https://api.github.com/repos/$OWNER/$REPO" | grep -q '"full_name"'; then
  curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    "https://api.github.com/user/repos" \
    -d "{\"name\":\"$REPO\",\"private\":false,\"auto_init\":false}" > /dev/null
  echo "✓ repo 已创建"
else
  echo "✓ repo 已存在"
fi

# 2. 启用 GitHub Pages (main 分支根目录)
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "https://api.github.com/repos/$OWNER/$REPO/pages" \
  -d '{"source":{"branch":"main","path":"/"}}' > /dev/null 2>&1 || true
echo "✓ pages 已配置"

# 3. 推送
cd "$HOME/hermes_share/ti2026"
if [ ! -d .git ]; then
  git init -q -b main
  git remote add origin "https://x-access-token:${TOKEN}@github.com/$OWNER/$REPO.git"
else
  git remote set-url origin "https://x-access-token:${TOKEN}@github.com/$OWNER/$REPO.git"
  # 若当前分支不是 main, 改名
  CUR=$(git branch --show-current)
  if [ "$CUR" != "main" ] && [ -n "$CUR" ]; then
    git branch -m main 2>/dev/null || true
  fi
fi
git add -A
git -c user.name="yczhang1028" -c user.email="yczhang1028@users.noreply.github.com" commit -m "update $(date +%Y-%m-%d)" -q || true
git push -u origin main 2>&1 | tail -5
echo "✓ 已推送: https://$OWNER.github.io/$REPO/"
