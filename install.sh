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
mkdir -p .claude/hooks .claude/commands docs/business scripts .github/workflows

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
echo "🤖 安裝 Claude Code Hooks..."
download ".claude/hooks/push-to-notion.sh" ".claude/hooks/push-to-notion.sh" true
download ".claude/hooks/business-docs-hook.sh" ".claude/hooks/business-docs-hook.sh" true
chmod +x .claude/hooks/push-to-notion.sh .claude/hooks/business-docs-hook.sh
download ".claude/commands/new-doc.md" ".claude/commands/new-doc.md" true
download ".claude/commands/push-docs.md" ".claude/commands/push-docs.md" true

echo ""
echo "🐍 安裝 Python 腳本..."
download "scripts/sync_to_notion.py" "scripts/sync_to_notion.py" true
download "scripts/validate_doc.py" "scripts/validate_doc.py" true
chmod +x scripts/sync_to_notion.py scripts/validate_doc.py

echo ""
echo "📢 安裝 GitHub Actions 模板..."
download ".github/workflows/notify-slack.yml" ".github/workflows/notify-slack.yml"

echo ""
echo "📝 安裝設定範本..."
download ".env.example" ".env.example.business-docs"

# Merge settings.json
HOOK_CMD="bash .claude/hooks/push-to-notion.sh"
if [ -f ".claude/settings.json" ]; then
  if ! grep -q "push-to-notion" .claude/settings.json 2>/dev/null || ! grep -q "business-docs-hook" .claude/settings.json 2>/dev/null; then
    # 自動 merge 所有 hook 到既有 settings.json
    python3 -c "
import json
try:
    with open('.claude/settings.json') as f:
        s = json.load(f)
except:
    s = {}
hooks = s.setdefault('hooks', {})
post = hooks.setdefault('PostToolUse', [])

# 要確保的 hook 列表
required_hooks = {
    'Bash': [
        'bash .claude/hooks/push-to-notion.sh',
        'bash .claude/hooks/business-docs-hook.sh',
    ],
    'Edit': ['bash .claude/hooks/business-docs-hook.sh'],
    'Write': ['bash .claude/hooks/business-docs-hook.sh'],
}

for matcher, cmds in required_hooks.items():
    entry = next((e for e in post if e.get('matcher') == matcher), None)
    if not entry:
        entry = {'matcher': matcher, 'hooks': []}
        post.append(entry)
    hs = entry.setdefault('hooks', [])
    for cmd in cmds:
        if not any(cmd in h.get('command', '') for h in hs):
            hs.append({'type': 'command', 'command': cmd})

with open('.claude/settings.json', 'w') as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
    f.write('\n')
" 2>/dev/null && echo "  ✅ .claude/settings.json（已 merge hook 設定）" || {
      echo "  ⚠️  無法自動 merge，請手動合併 .claude/settings.kit.json"
      download ".claude/settings.kit.json" ".claude/settings.kit.json"
    }
  else
    echo "  ⏭️  .claude/settings.json 已有所有 hook"
  fi
else
  download ".claude/settings.kit.json" ".claude/settings.json"
fi

echo ""
echo "✅ 安裝完成！"
echo ""
echo "已安裝的功能："
echo "  📄 /new-doc — 建立新商業文件"
echo "  📤 /push-docs — 推送文件到 Notion"
echo "  🔔 business-docs-hook — 程式碼修改時自動提醒更新文件"
echo "  📢 notify-slack.yml — PR/Issue 推送 Slack 通知"
echo ""
echo "下一步："
echo "  1. 在 Claude Code 裡用 /new-doc <功能名> 建立第一份文件"
echo "  2. （選配）Slack 通知："
echo "     - 到 GitHub repo Settings → Secrets 加入 SLACK_WEBHOOK_URL"
echo "  3. （選配）Notion 同步："
echo "     - export NOTION_TOKEN=secret_xxx"
echo "     - export NOTION_DATABASE_ID=xxx"
echo "     - pip3 install notion-client"
echo ""
echo "📖 規則說明：docs/business/README.md"
