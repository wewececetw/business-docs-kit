# Data Model: business-docs-kit

## 商業文件 (Business Doc)

一份 `docs/business/*.md` 檔案，格式固定。

### Metadata（檔案最上方）

| 欄位 | 必填 | 說明 |
|------|------|------|
| 功能名稱 | ✅ | H1 標題 |
| 一句話 | ✅ | 一句話講完功能 |
| 最後更新 | ✅ | YYYY-MM-DD |
| 分類 | ✅ | 例：歌本、候播、播放 |

### 固定小節

| 節次 | 必填 | 說明 |
|------|------|------|
| 為什麼需要這個 | ✅ | 動機 |
| 使用者怎麼用 | ✅ | 故事或步驟 |
| 關鍵規則 | ✅ | 每條規則配例子 |
| 為什麼這樣設計 | ✅ | 決策理由 |
| 會碰到的狀況 | ✅ | edge cases |
| 不做什麼 | ❌ | 選填 |

---

## 同步狀態 (.business-docs-sync.json)

記錄每份文件對應的 Notion page id。

```json
{
  "docs/business/songbook.md": {
    "notion_page_id": "abc123...",
    "last_pushed": "2026-04-06T12:00:00Z",
    "title": "歌本系統"
  }
}
```

---

## Notion Database Schema

安裝後需要在 Notion 建一個 Database，欄位：

| 欄位 | 型別 | 說明 |
|------|------|------|
| Title | Title | 功能名稱 |
| 一句話 | Rich text | 一句話描述 |
| 分類 | Select | 功能分類 |
| 最後更新 | Date | 文件更新日期 |
| 檔案路徑 | Rich text | repo 內相對路徑 |
| 內容 | Page content (blocks) | markdown 轉 Notion blocks |
