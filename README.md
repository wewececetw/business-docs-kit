# business-docs-kit

一鍵安裝的商業邏輯文件工具包，整合 Claude Code + Notion + Slack。

## 安裝

```bash
curl -sSL https://raw.githubusercontent.com/wewececetw/business-docs-kit/main/install.sh | bash
```

## 功能

| 功能 | 說明 |
|------|------|
| `/new-doc <name>` | 從模板建立新的商業文件 |
| `/push-docs [name]` | 手動推送文件到 Notion |
| Git commit hook | commit 含 `docs/business/` 變更時自動推 Notion |
| Business-docs hook | 程式碼修改時自動提醒更新對應的商業文件 |
| Slack 通知 | Issue/PR 開啟、PR merge 時推送 Slack |
| 格式驗證 | 推送前檢查 10 條規則是否合規 |

## 10 條規則（摘要）

1. **一句話開頭** — 一句話講完功能
2. **Why > What** — 文件講 why，code 講 what
3. **人話不用術語** — 例子取代抽象
4. **固定六節** — 為什麼 / 怎麼用 / 規則 / 設計 / 狀況 / 不做什麼
5. **規則配例子** — 沒例子就刪
6. **不重複 code** — 禁止貼 API schema
7. **決策留 why** — 記錄為什麼選這個
8. **日期同步** — 改文件就改日期
9. **一檔一功能** — 不混寫
10. **不做什麼也要寫** — 避免反覆討論

完整規則見安裝後的 `docs/business/README.md`。

## Slack 通知（選配）

安裝後會在 `.github/workflows/notify-slack.yml` 放一個模板，觸發條件：

- Issue 新建 → 推 Slack
- PR 開啟 → 推 Slack
- PR Merged → 推 Slack

設定方式：到 GitHub repo Settings → Secrets and variables → Actions → 新增 `SLACK_WEBHOOK_URL`。

未設定 secret 時，workflow 會執行但推送失敗（不影響其他功能）。

## Business-docs hook

程式碼修改時，Claude 會自動收到提醒：

- **Edit/Write 觸發**：修改任何程式碼檔案時，提醒檢查是否需要更新 `docs/business/` 對應文件
- **Git commit 觸發**：commit 完成後，提醒檢查本次變更是否涉及商業邏輯

此 hook 只做提醒，不自動修改文件，最終由 Claude 判斷是否需要更新。

## Notion 同步（選配）

1. 到 [Notion Integrations](https://www.notion.so/my-integrations) 建立 Integration
2. 在 Notion 建一個 Database，欄位：
   - `Title`（標題）
   - `一句話`（Rich text）
   - `分類`（Select）
   - `最後更新`（Date）
   - `檔案路徑`（Rich text）
3. 分享 Database 給 Integration
4. 設定環境變數：
   ```bash
   export NOTION_TOKEN=secret_xxx
   export NOTION_DATABASE_ID=xxx
   ```
5. 安裝 Python SDK：
   ```bash
   pip3 install notion-client
   ```

未設定 Notion 環境變數時，所有 Notion 相關功能會安靜跳過。

## 檔案結構

安裝後你的專案會新增：

```text
.claude/
├── hooks/
│   ├── push-to-notion.sh       # commit 後自動推 Notion
│   └── business-docs-hook.sh   # 程式碼修改時提醒更新文件
├── commands/
│   ├── new-doc.md
│   └── push-docs.md
└── settings.json               # Hook 設定（首次安裝）或 settings.kit.json（已有設定時）
.github/workflows/
└── notify-slack.yml            # Slack 通知模板
docs/business/
├── README.md                   # 10 條規則
└── _template.md                # 文件模板
scripts/
├── sync_to_notion.py
└── validate_doc.py
```
