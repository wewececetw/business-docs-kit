# Research: business-docs-kit 核心決策

## 安裝方式

**Decision**: curl 下載 install.sh 後執行，從 GitHub raw 拉 kit/ 內容

**Rationale**:
- 跟 spec-kit、oh-my-zsh 一致，使用者熟悉
- 不需 npm/pip 套件生態，零額外依賴
- `curl -sSL https://raw.githubusercontent.com/<user>/business-docs-kit/main/install.sh | bash`

**Alternatives**:
- npm package：要求 Node.js 環境
- git clone：多一步驟
- homebrew formula：發佈流程複雜

## Notion 目標結構

**Decision**: Database，每份 md 對應一筆 row

**Rationale**:
- 可排序、過濾、分類（by「分類」欄位）
- Notion 搜尋找得到
- 新增文件不需手動建 page
- 欄位對應：Title / 分類 / 最後更新 / 檔案路徑 / Git SHA

**Alternatives**:
- Page + Sub-pages：結構固定但失去過濾能力
- Single Page：所有文件串一起，太長

## Notion API SDK

**Decision**: `notion-client` (Python 官方 SDK)

**Rationale**:
- 官方維護、API 變動同步
- 支援 markdown → Notion block 轉換（透過 blocks.children.append）
- Python 是使用者系統預裝機率最高

**Alternatives**:
- md2notion：3 年沒更新
- notion-markdown-cli (Node)：需 Node 環境
- 裸 curl：手刻 blocks 太麻煩

## Hook 觸發方式

**Decision**: PostToolUse on Bash，檢查 git commit 是否含 `docs/business/` 變更

**Rationale**:
- 與 Claude Code hook 機制一致
- commit 才推，避免雜訊（Edit 時不推）
- 失敗不阻擋（exit 0）

## Markdown → Notion Block 策略

**Decision**: 用 notion-client 的 blocks API，自己寫簡化 markdown parser（只支援 H1-H3、段落、清單、粗體）

**Rationale**:
- 商業文件格式固定（6 小節），不需完整 markdown 支援
- 減少依賴
- 好 debug

## 同步狀態紀錄

**Decision**: `.business-docs-sync.json` 存在使用者專案根目錄，記錄 `{ filepath: notion_page_id }`

**Rationale**:
- 第二次推送時用 page id 更新既有 row，不新建
- gitignore 不加（讓 team 共用 page id）
- 若檔案被刪除，手動清 json entry

## 模板 6 小節結構

**Decision**: 為什麼需要 / 使用者怎麼用 / 關鍵規則 / 為什麼這樣設計 / 會碰到的狀況 / （選填）不做什麼

**Rationale**: 基於 KTV 實際文件經驗歸納，涵蓋動機、流程、規則、決策、邊界、取捨
