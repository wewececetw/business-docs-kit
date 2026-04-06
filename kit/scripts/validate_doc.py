#!/usr/bin/env python3
"""
商業文件格式驗證
用法: python3 validate_doc.py <filepath> [<filepath> ...]
Exit code: 0 = 全部通過, 1 = 有錯誤, 2 = 有警告但無錯誤
"""
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

REQUIRED_METADATA = ['一句話', '最後更新', '分類']
REQUIRED_SECTIONS = ['為什麼需要這個', '使用者怎麼用', '關鍵規則', '為什麼這樣設計', '會碰到的狀況']
ALLOWED_SECTIONS = REQUIRED_SECTIONS + ['不做什麼']
STALE_DAYS = 90


def validate(filepath):
    path = Path(filepath)
    if not path.exists():
        return [f'ERROR: 檔案不存在: {filepath}'], []

    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')
    errors = []
    warnings = []

    # R1: 一句話 metadata
    if '**一句話**' not in content:
        errors.append('R1: 缺少「一句話」metadata')
    elif re.search(r'\*\*一句話\*\*：\s*\[', content):
        errors.append('R1:「一句話」還是模板佔位符，請填寫實際內容')

    # R8: 最後更新
    date_match = re.search(r'\*\*最後更新\*\*：(\d{4}-\d{2}-\d{2})', content)
    if not date_match:
        errors.append('R8: 缺少「最後更新」日期（格式 YYYY-MM-DD）')
    else:
        try:
            update_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
            if datetime.now() - update_date > timedelta(days=STALE_DAYS):
                warnings.append(f'R8:「最後更新」超過 {STALE_DAYS} 天，文件可能過期')
        except ValueError:
            errors.append('R8:「最後更新」日期格式不正確')

    # 分類
    if '**分類**' not in content:
        errors.append('R9: 缺少「分類」metadata')

    # R4: 固定小節
    headings = re.findall(r'^## (.+)$', content, re.MULTILINE)
    for section in REQUIRED_SECTIONS:
        if section not in headings:
            errors.append(f'R4: 缺少必填小節「{section}」')

    for heading in headings:
        if heading not in ALLOWED_SECTIONS:
            warnings.append(f'R4: 非標準小節「{heading}」（允許但建議移除）')

    # R6: 不應有 code block（簡易檢查）
    code_blocks = re.findall(r'```\w+', content)
    if code_blocks:
        warnings.append('R6: 文件中有程式碼區塊，商業文件不應包含程式碼')

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print('用法: python3 validate_doc.py <filepath> [<filepath> ...]')
        sys.exit(1)

    has_errors = False
    has_warnings = False

    for filepath in sys.argv[1:]:
        # 跳過模板和 README
        name = Path(filepath).name
        if name.startswith('_') or name == 'README.md':
            continue

        errors, warnings = validate(filepath)

        if errors or warnings:
            print(f'\n📄 {filepath}')
            for e in errors:
                print(f'  ❌ {e}')
                has_errors = True
            for w in warnings:
                print(f'  ⚠️  {w}')
                has_warnings = True
        else:
            print(f'  ✅ {filepath} 通過')

    if has_errors:
        print('\n驗證失敗：請修正上述錯誤')
        sys.exit(1)
    elif has_warnings:
        print('\n驗證通過（有警告）')
        sys.exit(2)
    else:
        print('\n✅ 全部通過')
        sys.exit(0)


if __name__ == '__main__':
    main()
