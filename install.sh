#!/bin/bash
# business-docs-kit 一鍵安裝腳本
# 用法: curl -sSL https://raw.githubusercontent.com/wewececetw/business-docs-kit/main/install.sh | bash
set -e

REPO="wewececetw/business-docs-kit"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/$REPO/$BRANCH/kit"

echo "📦 business-docs-kit 安裝中..."
echo ""

# 檢查是否在 git 專案內
if [ ! -d ".git" ]; then
  echo "❌ 請在 git 專案根目錄執行此腳本"
  exit 1
fi

# 檢查是否已安裝
if [ -f "docs/business/_template.md" ] && [ -f ".claude/hooks/push-to-notion.sh" ]; then
  echo "⚠️  已安裝過 business-docs-kit"
  read -p "要更新嗎？(y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消安裝"
    exit 0
  fi
fi

# 建立目錄
mkdir -p .claude/hooks .claude/commands docs/business scripts

# 下載檔案（不覆蓋既有）
download() {
  local src="$1"
  local dest="$2"
  local overwrite="${3:-false}"

  if [ -f "$dest" ] && [ "$overwrite" = "false" ]; then
    echo "  ⏭️  $dest 已存在，跳過"
    return
  fi

  curl -sSL "$RAW_BASE/$src" -o "$dest"
  echo "  ✅ $dest"
}

echo "📄 安裝文件模板..."
download "docs/business/_template.md" "docs/business/_template.md"
download "docs/business/README.md" "docs/business/README.md"

echo ""
echo "🤖 安裝 Claude Code 設定..."
download ".claude/hooks/push-to-notion.sh" ".claude/hooks/push-to-notion.sh" true
chmod +x .claude/hooks/push-to-notion.sh
download ".claude/commands/new-doc.md" ".claude/commands/new-doc.md" true
download ".claude/commands/push-docs.md" ".claude/commands/push-docs.md" true

echo ""
echo "🐍 安裝 Python 腳本..."
download "scripts/sync_to_notion.py" "scripts/sync_to_notion.py" true
download "scripts/validate_doc.py" "scripts/validate_doc.py" true
chmod +x scripts/sync_to_notion.py scripts/validate_doc.py

echo ""
echo "📝 安裝設定範本..."
download ".env.example" ".env.example.business-docs"

# Merge settings.json
HOOK_CMD="bash .claude/hooks/push-to-notion.sh"
if [ -f ".claude/settings.json" ]; then
  if ! grep -q "push-to-notion" .claude/settings.json 2>/dev/null; then
    # 自動 merge hook 到既有 settings.json
    python3 -c "
import json, sys
try:
    with open('.claude/settings.json') as f:
        s = json.load(f)
except:
    s = {}
hooks = s.setdefault('hooks', {})
post = hooks.setdefault('PostToolUse', [])
# 找是否有 Bash matcher
found = False
for entry in post:
    if entry.get('matcher') == 'Bash':
        hs = entry.setdefault('hooks', [])
        if not any('push-to-notion' in h.get('command','') for h in hs):
            hs.append({'type': 'command', 'command': '$HOOK_CMD'})
        found = True
        break
if not found:
    post.append({'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': '$HOOK_CMD'}]})
with open('.claude/settings.json', 'w') as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
    f.write('\n')
" 2>/dev/null && echo "  ✅ .claude/settings.json（已 merge hook 設定）" || echo "  ⚠️  無法自動 merge settings.json，請手動加入 push-to-notion hook"
  else
    echo "  ⏭️  .claude/settings.json 已有 push-to-notion hook"
  fi
else
  download ".claude/settings.kit.json" ".claude/settings.json"
fi

echo ""
echo "✅ 安裝完成！"
echo ""
echo "下一步："
echo "  1. 在 Claude Code 裡用 /new-doc <功能名> 建立第一份文件"
echo "  2. （選配）設定 Notion 同步："
echo "     - 到 https://www.notion.so/my-integrations 建 Integration"
echo "     - 在 Notion 建 Database（欄位：Title, 一句話, 分類, 最後更新, 檔案路徑）"
echo "     - 分享 Database 給 Integration"
echo "     - export NOTION_TOKEN=secret_xxx"
echo "     - export NOTION_DATABASE_ID=xxx"
echo "  3. pip3 install notion-client（若要用 Notion 同步）"
echo ""
echo "📖 規則說明：docs/business/README.md"
