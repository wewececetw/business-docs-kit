# Tasks: business-docs-kit 核心工具包

**Feature**: 001-core-kit
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

`[P]` = 可平行；`[US1-5]` = 對應 user story

---

## Phase 1: 模板與規則（foundation）

- [ ] T001 [US2] 建立 `kit/docs/business/_template.md`：6 小節 + metadata + 範例提示
- [ ] T002 [US2] 建立 `kit/docs/business/README.md`：10 條寫作規則完整說明
- [ ] T003 驗證模板：用 KTV songbook 為例填寫一份，確認結構合理

---

## Phase 2: Slash Commands

- [ ] T004 [P] [US2] 建立 `kit/.claude/commands/new-doc.md`：收到 `/new-doc <name>` 時複製 _template 到 `docs/business/<name>.md`
- [ ] T005 [P] [US4] 建立 `kit/.claude/commands/push-docs.md`：收到 `/push-docs [name]` 時執行 sync_to_notion.py

---

## Phase 3: Python 腳本

- [ ] T006 [P] [US5] 建立 `kit/scripts/validate_doc.py`：檢查 metadata（一句話、最後更新、分類）+ 必填小節
- [ ] T007 [P] [US3] 建立 `kit/scripts/sync_to_notion.py`：讀 md → 解析 metadata → 建/更新 Notion Database row → 寫 .business-docs-sync.json
- [ ] T008 建立 `kit/.env.example`：NOTION_TOKEN、NOTION_DATABASE_ID 範本

---

## Phase 4: Hook

- [ ] T009 [US3] 建立 `kit/.claude/hooks/push-to-notion.sh`：PostToolUse:Bash 偵測 git commit 含 docs/business/ 變更 → 呼叫 sync_to_notion.py
- [ ] T010 建立 `kit/.claude/settings.kit.json`：hook 設定片段

---

## Phase 5: 安裝腳本

- [ ] T011 [US1] 建立 `install.sh`：從 GitHub raw 下載 kit/ 內容，複製到使用者專案，merge settings.json，不覆蓋既有檔案
- [ ] T012 建立 `README.md`（repo 根目錄）：安裝指令 + 功能說明 + 10 條規則摘要

---

## Phase 6: 測試驗證

- [ ] T013 在 KTV 專案執行 install.sh，確認檔案正確安裝
- [ ] T014 在 KTV 跑 `/new-doc test-feature`，確認產生模板
- [ ] T015 在 KTV 跑 `python3 scripts/validate_doc.py`，確認驗證正確
- [ ] T016 設定 Notion token，commit 一份 docs/business/*.md，確認自動推 Notion
- [ ] T017 在 KTV 跑 `/push-docs`，確認手動推送

---

## Dependencies

```text
T001-T003 (模板) ← 無依賴
    ↓
T004-T005 (commands) ║ T006-T008 (Python) ║ T009-T010 (hook) ← 可平行
    ↓
T011-T012 (安裝腳本) ← 依賴上面全部
    ↓
T013-T017 (驗證) ← 依賴安裝腳本
```
