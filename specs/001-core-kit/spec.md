# Feature Specification: business-docs-kit 核心工具包

**Feature Branch**: `001-core-kit`
**Created**: 2026-04-06
**Status**: Draft
**Input**: 一鍵安裝的工具包，統一商業邏輯文件規範 + 推 Notion

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 一鍵安裝到既有專案 (Priority: P1)

開發者在自己的專案裡跑一行 curl 指令，自動把 business-docs-kit 的檔案（template、hooks、slash commands）安裝到 `.claude/` 和 `docs/business/`，無需手動搬檔案。

**Why this priority**: 安裝門檻高等於沒人用。一行指令才能讓這個工具真的被採用。

**Independent Test**: 在一個全新專案跑 `curl -sSL https://.../install.sh | bash`，確認 `.claude/hooks/`、`.claude/commands/`、`docs/business/README.md` 都被建立。

**Acceptance Scenarios**:
1. **Given** 專案沒有 `.claude/` 目錄, **When** 執行 install.sh, **Then** 自動建立 `.claude/hooks/` 和 `.claude/commands/`
2. **Given** 專案已有 `.claude/` 但無本 kit 檔案, **When** 執行 install.sh, **Then** 只新增本 kit 的檔案，不覆蓋既有設定
3. **Given** 專案已安裝過本 kit, **When** 再次執行 install.sh, **Then** 提示「已安裝」並詢問是否更新

---

### User Story 2 - 寫商業文件有固定格式可遵循 (Priority: P1)

開發者寫 `docs/business/*.md` 時有固定的 6 小節模板可套用，不用每次煩惱「要寫什麼、怎麼分段」。

**Why this priority**: 沒有模板等於每人寫一套，文件風格混亂就沒價值。

**Independent Test**: 跑 `/new-doc songbook`，確認產生符合 10 條規則的 markdown 檔骨架。

**Acceptance Scenarios**:
1. **Given** 使用者執行 `/new-doc <功能名>`, **When** Claude 收到指令, **Then** 在 `docs/business/<功能名>.md` 產生含 6 小節的模板檔
2. **Given** 模板檔案, **When** 開發者開啟查看, **Then** 每節有中文說明與 1 個範例提示
3. **Given** 模板檔最上方, **When** 查看, **Then** 有「一句話」、「最後更新」、「分類」三個必填 metadata

---

### User Story 3 - git commit 後自動推 Notion (Priority: P1)

開發者 commit 含 `docs/business/*.md` 變更時，hook 自動把更新的檔案推到 Notion Database，每份文件對應一筆 row。

**Why this priority**: 讓文件「活」在 Notion，非技術成員（PM、老闆）才看得到。

**Independent Test**: 改 `docs/business/songbook.md` 後 commit，確認 Notion Database 對應 row 內容已更新。

**Acceptance Scenarios**:
1. **Given** 已設定 `NOTION_TOKEN` 和 `NOTION_DATABASE_ID`, **When** commit 含 `docs/business/` 變更, **Then** hook 自動執行 Python 腳本推送
2. **Given** Notion Database 內該文件已有 row, **When** 推送時, **Then** 更新既有 row（by 標題比對）
3. **Given** 推送失敗（網路/token 錯）, **When** hook 執行, **Then** 印出錯誤但不阻擋 commit
4. **Given** 未設定 Notion 環境變數, **When** hook 執行, **Then** 安靜跳過（讓使用者自行決定是否啟用）

---

### User Story 4 - 手動觸發推送 (Priority: P2)

開發者有時想立即推送但不 commit（例如文件寫到一半想預覽 Notion 呈現效果）。

**Why this priority**: 降低心理負擔，不用為了推 Notion 勉強 commit。

**Independent Test**: 在 Claude Code 裡呼叫 `/push-docs`，確認所有 `docs/business/*.md` 被推到 Notion。

**Acceptance Scenarios**:
1. **Given** 使用者呼叫 `/push-docs`, **When** Claude 執行, **Then** 推送所有 `docs/business/*.md` 到 Notion
2. **Given** 指定單一檔案 `/push-docs songbook`, **When** Claude 執行, **Then** 只推送 `docs/business/songbook.md`
3. **Given** 推送完成, **When** Claude 回報, **Then** 列出成功推送的檔案 + 對應 Notion URL

---

### User Story 5 - 文件格式驗證 (Priority: P2)

推送前自動檢查文件是否符合 10 條規則（缺小節、缺一句話、缺最後更新日期等），不合格時提示修正。

**Why this priority**: 沒有驗證，規範就只是建議，長期會鬆掉。

**Independent Test**: 故意寫一份缺「最後更新」的 md，跑 `/push-docs` 應被擋下並提示。

**Acceptance Scenarios**:
1. **Given** 文件缺「一句話」metadata, **When** 推送時, **Then** 拒絕推送，提示「缺少一句話開頭」
2. **Given** 文件多了規範外的節次, **When** 驗證時, **Then** 警告但允許推送（不強制）
3. **Given** 「最後更新」日期超過 90 天, **When** 驗證時, **Then** 警告「文件可能過期」

---

### Edge Cases

- **無 Notion token**：hook 安靜跳過，不噴錯
- **Notion API rate limit**：retry 3 次，失敗印錯但不阻擋
- **檔案被刪除**：對應 Notion row 不自動刪（人工處理更安全）
- **衝突編輯**：Notion 上有人改、repo 也改 → repo 為主，直接覆蓋（markdown is source of truth）
- **檔名含空白 / 中文**：支援，用檔名（不含 .md）當作標題 fallback
- **首次使用**：install.sh 後提示使用者到 Notion 建 integration、拿 token、設環境變數

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統 MUST 提供 curl 一鍵安裝腳本，複製所有 kit 檔案到使用者專案
- **FR-002**: 系統 MUST 提供商業文件模板，包含固定 6 小節結構
- **FR-003**: 系統 MUST 記錄並執行 10 條商業文件寫作規則
- **FR-004**: 系統 MUST 提供 `/new-doc <name>` slash command 產生新文件
- **FR-005**: 系統 MUST 提供 `/push-docs [name]` slash command 手動推送
- **FR-006**: 系統 MUST 在 git commit 後自動偵測 `docs/business/` 變更並推 Notion
- **FR-007**: 系統 MUST 支援 Notion Database 作為目標（每份文件對應一筆 row）
- **FR-008**: 系統 MUST 在推送前驗證文件格式（metadata 完整性、日期有效性）
- **FR-009**: 系統 MUST 透過環境變數 `NOTION_TOKEN`、`NOTION_DATABASE_ID` 設定 Notion 連線
- **FR-010**: 系統 MUST 在未設定 Notion 環境變數時優雅跳過（不報錯、不阻擋 commit）
- **FR-011**: 使用者 MUST 能在安裝後無需其他步驟即可使用基本功能（寫文件、產模板）；Notion 同步為選配

### Key Entities *(include if feature involves data)*

- **商業文件（Business Doc）**：一份 markdown 檔，代表一個功能的商業邏輯說明
- **Notion Row**：Notion Database 內一筆資料，對應一份商業文件
- **同步狀態**：記錄每份文件最後推送時間 / Notion page id（可存 `.business-docs-sync.json`）

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 使用者從 curl 安裝到寫完第一份文件，耗時 < 5 分鐘
- **SC-002**: 95% 的 commit 中 `docs/business/*.md` 變更會成功推到 Notion（排除 token 未設定情境）
- **SC-003**: 採用本 kit 的專案，非技術成員能在 Notion 讀懂 80% 以上的文件（不需問工程師）
- **SC-004**: 文件格式合規率（通過 10 條規則檢查）> 90%

## Assumptions

- 使用者有 Notion 帳號且能建立 Integration 拿到 API token
- 使用者 Notion workspace 有可寫入的 Database（或能自行建立）
- 使用者專案使用 git 做版本控制
- 使用者專案使用 Claude Code 作為主要開發工具（需要 `.claude/` 目錄）
- Python 3.8+ 已安裝（同步腳本需要）
