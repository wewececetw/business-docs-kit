#!/bin/bash
# Hook: 程式碼修改後提醒 Claude 更新 docs/business/ 對應文件
# 觸發條件: PostToolUse on Edit/Write (檔案修改) 和 Bash (git commit)

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""')

# ── Edit / Write 觸發：檢查修改的檔案是否涉及商業邏輯 ──
if [ "$TOOL" = "Edit" ] || [ "$TOOL" = "Write" ]; then
  FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
  [ -z "$FILE" ] && exit 0

  # 跳過 docs/business/ 本身的修改（避免無限迴圈）
  echo "$FILE" | grep -q 'docs/business/' && exit 0

  # 跳過非程式碼檔案
  echo "$FILE" | grep -qE '\.(md|txt|log|json|yml|yaml|lock|gitignore)$' && exit 0

  # 輸出提醒（Claude 會看到這個 additionalContext）
  BASENAME=$(basename "$FILE")
  echo "{\"additionalContext\": \"[business-docs-hook] 檔案 $FILE 已被修改。若此變更影響了任何商業邏輯，請更新 docs/business/ 底下對應的文件。\"}"
  exit 1  # exit 1 = blocking，Claude 必須回應
fi

# ── Bash 觸發：git commit 後檢查 ──
if [ "$TOOL" = "Bash" ]; then
  CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')
  echo "$CMD" | grep -qE 'git commit' || exit 0

  echo "{\"additionalContext\": \"[business-docs-hook] git commit 執行完成。請檢查本次 commit 涉及的檔案，若有商業邏輯變更，請同步更新 docs/business/ 底下對應的文件，並更新各文件的「最後更新」日期。\"}"
  exit 1
fi

exit 0
