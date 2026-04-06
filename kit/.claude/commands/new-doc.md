---
description: "建立新的商業邏輯文件"
---

# /new-doc

使用者提供功能名稱（例如 `/new-doc songbook`），你要：

1. 複製 `docs/business/_template.md` 到 `docs/business/$ARGUMENTS.md`
2. 把 `[功能名稱]` 替換成使用者提供的名稱
3. 把 `YYYY-MM-DD` 替換成今天日期
4. 告知使用者檔案已建立，並提醒填寫內容

注意：
- 若檔案已存在，詢問是否覆蓋
- 檔名用小寫英文或中文，不含空白（用 `-` 連接）
- 遵守 `docs/business/README.md` 的 10 條規則
