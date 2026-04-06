---
description: "推送商業文件到 Notion"
---

# /push-docs

手動推送 `docs/business/*.md` 到 Notion Database。

## 用法

- `/push-docs` — 推送所有 `docs/business/*.md`（不含 README.md、_template.md）
- `/push-docs songbook` — 只推送 `docs/business/songbook.md`

## 執行步驟

1. 檢查環境變數 `NOTION_TOKEN` 和 `NOTION_DATABASE_ID` 是否已設定
   - 若未設定，提示使用者參考 `.env.example` 設定
2. 對每份要推送的檔案，先執行驗證：
   ```bash
   python3 scripts/validate_doc.py docs/business/<name>.md
   ```
   - 驗證失敗 → 列出問題，詢問是否仍要推送
3. 執行推送：
   ```bash
   python3 scripts/sync_to_notion.py docs/business/<name>.md
   ```
4. 回報結果：列出推送成功的檔案 + Notion URL
