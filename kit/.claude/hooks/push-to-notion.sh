#!/bin/bash
# Hook: git commit 後自動推送 docs/business/ 變更到 Notion
# 觸發條件: PostToolUse on Bash (偵測 git commit)

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""')

# 只處理 Bash 工具
[ "$TOOL" = "Bash" ] || exit 0

CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# 只處理 git commit
echo "$CMD" | grep -qE 'git commit' || exit 0

# 找到 docs/business/ 中有變更的檔案
CHANGED=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | grep '^docs/business/.*\.md$' | grep -v 'README.md' | grep -v '_template.md')

[ -z "$CHANGED" ] && exit 0

# 檢查 Notion 環境變數
if [ -z "$NOTION_TOKEN" ] || [ -z "$NOTION_DATABASE_ID" ]; then
  # 未設定 Notion → 安靜跳過
  exit 0
fi

# 推送每個變更的檔案
for f in $CHANGED; do
  python3 scripts/sync_to_notion.py "$f" 2>&1 || true
done

exit 0
