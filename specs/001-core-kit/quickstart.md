# Quickstart: 手動驗證

## 前置

- 有一個 git 專案（可用 KTV 或新建空專案）
- Python 3.8+ 已安裝
- Notion 帳號 + Integration token（可選）

## 驗證步驟

### 1. 安裝

```bash
cd <your-project>
curl -sSL https://raw.githubusercontent.com/wewececetw/business-docs-kit/main/install.sh | bash
```

確認：
- [ ] `.claude/hooks/push-to-notion.sh` 存在
- [ ] `.claude/commands/new-doc.md` 存在
- [ ] `docs/business/README.md` 存在
- [ ] `docs/business/_template.md` 存在

### 2. 產生文件

在 Claude Code 裡：
```
/new-doc songbook
```

確認：
- [ ] `docs/business/songbook.md` 產生
- [ ] 有 6 小節骨架
- [ ] 最上面有 metadata（一句話、最後更新、分類）

### 3. 格式驗證

```bash
python3 scripts/validate_doc.py docs/business/songbook.md
```

確認：
- [ ] 缺 metadata 會報錯
- [ ] 所有必填小節缺少會報錯
- [ ] 完整文件通過不報錯

### 4. 推 Notion（需設定 token）

```bash
export NOTION_TOKEN=secret_xxx
export NOTION_DATABASE_ID=xxx
python3 scripts/sync_to_notion.py docs/business/songbook.md
```

確認：
- [ ] Notion Database 出現新 row
- [ ] Title、分類、內容正確
- [ ] `.business-docs-sync.json` 有記錄
- [ ] 再跑一次 → 更新同一 row 不新建

### 5. Hook 驗證

```bash
git add docs/business/songbook.md
git commit -m "docs: 新增歌本商業文件"
```

確認：
- [ ] 有 NOTION_TOKEN → 自動推送成功
- [ ] 無 NOTION_TOKEN → 安靜跳過不報錯
