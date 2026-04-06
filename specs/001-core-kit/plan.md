# Implementation Plan: business-docs-kit 核心工具包

**Branch**: `001-core-kit` | **Date**: 2026-04-06 | **Spec**: [spec.md](./spec.md)

## Summary

做一個 curl 一鍵安裝的 Claude Code 擴充包，提供「結構化商業文件模板 + 10 條寫作規則 + Notion 同步」三位一體。使用者在任何專案跑一行指令即可安裝，寫文件時 Claude Code 跟著模板走，git commit 後自動推 Notion Database。

## Technical Context

**Language/Version**: Bash 4+（install.sh、hooks）、Python 3.8+（Notion 同步）、Markdown（模板與文件）
**Primary Dependencies**: `notion-client`（官方 Python SDK）、`jq`（hook 解析 JSON input）
**Storage**: 使用者專案內 `.business-docs-sync.json`（記錄檔案 → Notion page id 對應）
**Testing**: 手動測試 + 在 KTV 專案作為實際使用案例驗證
**Target Platform**: macOS / Linux（bash + python）
**Project Type**: CLI 工具包（檔案散佈形式，無 runtime server）
**Performance Goals**: 安裝腳本 < 5s；單份文件推 Notion < 3s
**Constraints**: 不要求 Node.js；Python 依賴最小化（只用 notion-client）
**Scale/Scope**: 預估每個使用者專案 docs/business 5~20 份檔案

## Constitution Check

憲法模板，略。

## Project Structure

### Documentation (this feature)

```text
specs/001-core-kit/
├── plan.md
├── spec.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── file-layout.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
business-docs-kit/
├── install.sh                   # curl 一鍵安裝入口
├── README.md                    # 說明 + 10 條規則
├── kit/                         # 實際會被複製到使用者專案的檔案
│   ├── .claude/
│   │   ├── hooks/
│   │   │   └── push-to-notion.sh
│   │   ├── commands/
│   │   │   ├── new-doc.md
│   │   │   └── push-docs.md
│   │   └── settings.kit.json    # hook 設定片段，供 merge
│   ├── docs/
│   │   └── business/
│   │       ├── README.md        # 10 條規則說明
│   │       └── _template.md     # 文件模板
│   ├── scripts/
│   │   ├── sync_to_notion.py
│   │   └── validate_doc.py
│   └── .env.example             # NOTION_TOKEN、NOTION_DATABASE_ID 範本
├── specs/                       # speckit 文件
└── .specify/                    # speckit 結構
```

**Structure Decision**: 採用「kit/ 目錄存放所有會被複製的檔案」模式。install.sh 只做兩件事：(1) 下載本 repo kit/ 內容 (2) 複製到使用者專案對應位置。這讓「要安裝什麼」和「安裝邏輯」解耦，日後新增檔案不用改 install.sh。

## Complexity Tracking

無違規。
