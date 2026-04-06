# File Layout Contract: 安裝後專案結構

install.sh 執行後，使用者專案會新增以下檔案：

```text
<user-project>/
├── .claude/
│   ├── hooks/
│   │   └── push-to-notion.sh          # PostToolUse:Bash hook
│   ├── commands/
│   │   ├── new-doc.md                  # /new-doc <name>
│   │   └── push-docs.md               # /push-docs [name]
│   └── settings.json                   # 新增 hook 設定（merge 不覆蓋）
├── docs/
│   └── business/
│       ├── README.md                   # 10 條規則
│       └── _template.md               # 文件模板
├── scripts/
│   ├── sync_to_notion.py              # Notion 同步腳本
│   └── validate_doc.py                # 文件格式驗證
├── .env.example                       # 新增 NOTION_TOKEN、NOTION_DATABASE_ID
└── .business-docs-sync.json           # 同步狀態（首次推送時自動產生）
```

## 安裝規則

- `.claude/settings.json`：若已存在，merge hook 設定進去（不覆蓋使用者既有設定）
- `.env.example`：若已存在，append 不重複
- 其他檔案：若已存在則跳過，印提示
