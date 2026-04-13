#!/usr/bin/env python3
"""
同步 docs/business/*.md 到 Notion Database
用法: python3 sync_to_notion.py <filepath> [<filepath> ...]
      python3 sync_to_notion.py --all   # 推送所有 docs/business/*.md

環境變數:
  NOTION_TOKEN       - Notion Integration token
  NOTION_DATABASE_ID - 目標 Database ID
"""
import sys
import os
import re
import json
import requests
from pathlib import Path
from datetime import datetime

SYNC_FILE = '.business-docs-sync.json'
NOTION_API = 'https://api.notion.com/v1'
NOTION_VERSION = '2022-06-28'


def check_env():
    token = os.environ.get('NOTION_TOKEN')
    db_id = os.environ.get('NOTION_DATABASE_ID')
    if not token:
        print('⏭️  NOTION_TOKEN 未設定，跳過 Notion 同步')
        sys.exit(0)
    if not db_id:
        print('❌ NOTION_DATABASE_ID 未設定')
        sys.exit(1)
    return token, db_id


def headers(token):
    return {
        'Authorization': f'Bearer {token}',
        'Notion-Version': NOTION_VERSION,
        'Content-Type': 'application/json',
    }


def load_sync_state():
    path = Path(SYNC_FILE)
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return {}


def save_sync_state(state):
    Path(SYNC_FILE).write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )


def parse_metadata(content):
    meta = {}
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    meta['title'] = title_match.group(1) if title_match else '未命名'

    oneliner_match = re.search(r'\*\*一句話\*\*：(.+)', content)
    meta['oneliner'] = oneliner_match.group(1).strip() if oneliner_match else ''

    category_match = re.search(r'\*\*分類\*\*：(.+)', content)
    meta['category'] = category_match.group(1).strip() if category_match else ''

    date_match = re.search(r'\*\*最後更新\*\*：(\d{4}-\d{2}-\d{2})', content)
    meta['last_updated'] = date_match.group(1) if date_match else None

    return meta


SECTION_ICONS = {
    '為什麼需要這個': '💡',
    '使用者怎麼用': '👤',
    '關鍵規則': '📏',
    '為什麼這樣設計': '🏗️',
    '會碰到的狀況': '⚠️',
    '不做什麼': '🚫',
}


def parse_rich_text(text):
    """把 markdown 粗體 **text** 轉成 Notion rich_text annotations"""
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    rich = []
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            rich.append({
                'type': 'text',
                'text': {'content': part[2:-2]},
                'annotations': {'bold': True}
            })
        elif part:
            rich.append({
                'type': 'text',
                'text': {'content': part}
            })
    return rich if rich else [{'type': 'text', 'text': {'content': text}}]


def md_to_notion_blocks(content, meta):
    blocks = []

    # Callout: metadata 摘要
    callout_text = f"📌 {meta['oneliner']}" if meta['oneliner'] else '📌 （缺一句話描述）'
    callout_parts = [callout_text]
    if meta['category']:
        callout_parts.append(f"分類：{meta['category']}")
    if meta['last_updated']:
        callout_parts.append(f"最後更新：{meta['last_updated']}")
    blocks.append({
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '📋'},
            'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(callout_parts)}}],
            'color': 'blue_background'
        }
    })
    blocks.append({'type': 'divider', 'divider': {}})

    lines = content.split('\n')

    # 找到第一個 ## 開始
    start = 0
    for idx, line in enumerate(lines):
        if line.startswith('## '):
            start = idx
            break

    # 先把內容按 ## 切成 sections
    sections = []
    current_title = None
    current_lines = []

    for idx in range(start, len(lines)):
        line = lines[idx]
        if line.startswith('## '):
            if current_title is not None:
                sections.append((current_title, current_lines))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_title is not None:
        sections.append((current_title, current_lines))

    # 每個 section 做成 toggle heading
    for title, section_lines in sections:
        icon = SECTION_ICONS.get(title, '📝')
        # 收集 children blocks
        children = []
        for line in section_lines:
            # 跳過 HTML 註解
            if line.strip().startswith('<!--'):
                while section_lines and '-->' not in line:
                    idx = section_lines.index(line) + 1 if line in section_lines else len(section_lines)
                    break
                continue
            if '-->' in line:
                continue

            if line.startswith('- '):
                children.append({
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'rich_text': parse_rich_text(line[2:].strip())
                    }
                })
            elif line.strip():
                children.append({
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': parse_rich_text(line.strip())
                    }
                })

        # Divider before each section (except first)
        if sections.index((title, section_lines)) > 0:
            blocks.append({'type': 'divider', 'divider': {}})

        # Toggle heading
        blocks.append({
            'type': 'heading_2',
            'heading_2': {
                'rich_text': [{'type': 'text', 'text': {'content': f'{icon} {title}'}}],
                'is_toggleable': True,
                'children': children if children else [
                    {'type': 'paragraph', 'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': '（待填寫）'}}]}}
                ]
            }
        })

    return blocks


def find_existing_page(token, db_id, title):
    resp = requests.post(
        f'{NOTION_API}/databases/{db_id}/query',
        headers=headers(token),
        json={'filter': {'property': 'Title', 'title': {'equals': title}}}
    )
    data = resp.json()
    if data.get('results'):
        return data['results'][0]['id']
    return None


def sync_file(token, db_id, filepath, sync_state):
    path = Path(filepath)
    content = path.read_text(encoding='utf-8')
    meta = parse_metadata(content)
    blocks = md_to_notion_blocks(content, meta)

    properties = {
        'Title': {'title': [{'text': {'content': meta['title']}}]},
        '一句話': {'rich_text': [{'text': {'content': meta['oneliner']}}]},
        '分類': {'select': {'name': meta['category'] or '未分類'}},
        '檔案路徑': {'rich_text': [{'text': {'content': str(filepath)}}]},
    }
    if meta['last_updated']:
        properties['最後更新'] = {'date': {'start': meta['last_updated']}}

    page_id = sync_state.get(str(filepath), {}).get('notion_page_id')

    if not page_id:
        page_id = find_existing_page(token, db_id, meta['title'])

    if page_id:
        # 更新既有 page
        try:
            requests.patch(
                f'{NOTION_API}/pages/{page_id}',
                headers=headers(token),
                json={'properties': properties}
            ).raise_for_status()

            # 清除舊 blocks
            existing = requests.get(
                f'{NOTION_API}/blocks/{page_id}/children',
                headers=headers(token)
            ).json()
            for block in existing.get('results', []):
                try:
                    requests.delete(
                        f'{NOTION_API}/blocks/{block["id"]}',
                        headers=headers(token)
                    )
                except Exception:
                    pass

            # 新增 blocks（每次最多 100）
            for chunk_start in range(0, len(blocks), 100):
                chunk = blocks[chunk_start:chunk_start + 100]
                requests.patch(
                    f'{NOTION_API}/blocks/{page_id}/children',
                    headers=headers(token),
                    json={'children': chunk}
                ).raise_for_status()

            action = '更新'
        except Exception as e:
            print(f'  ❌ 更新失敗: {e}')
            return None
    else:
        # 新建 page
        try:
            resp = requests.post(
                f'{NOTION_API}/pages',
                headers=headers(token),
                json={
                    'parent': {'database_id': db_id},
                    'properties': properties,
                    'children': blocks[:100],  # 建立時最多 100 blocks
                }
            )
            resp.raise_for_status()
            page = resp.json()
            page_id = page['id']

            # 若超過 100 blocks，補上剩餘
            for chunk_start in range(100, len(blocks), 100):
                chunk = blocks[chunk_start:chunk_start + 100]
                requests.patch(
                    f'{NOTION_API}/blocks/{page_id}/children',
                    headers=headers(token),
                    json={'children': chunk}
                ).raise_for_status()

            action = '新建'
        except Exception as e:
            print(f'  ❌ 新建失敗: {e}')
            return None

    notion_url = f'https://notion.so/{page_id.replace("-", "")}'
    sync_state[str(filepath)] = {
        'notion_page_id': page_id,
        'last_pushed': datetime.now().isoformat(),
        'title': meta['title']
    }

    print(f'  ✅ {action}: {meta["title"]} → {notion_url}')
    return page_id


def main():
    token, db_id = check_env()

    if len(sys.argv) < 2 or sys.argv[1] == '--all':
        files = sorted(Path('docs/business').glob('*.md'))
        files = [f for f in files if f.name != 'README.md' and not f.name.startswith('_')]
    else:
        files = []
        for arg in sys.argv[1:]:
            p = Path(arg)
            if not p.exists():
                p = Path(f'docs/business/{arg}.md')
            if p.exists():
                files.append(p)
            else:
                print(f'⚠️  找不到: {arg}')

    if not files:
        print('沒有檔案需要推送')
        sys.exit(0)

    print(f'📤 推送 {len(files)} 份文件到 Notion...\n')

    sync_state = load_sync_state()
    success = 0

    for f in files:
        result = sync_file(token, db_id, f, sync_state)
        if result:
            success += 1

    save_sync_state(sync_state)
    print(f'\n完成：{success}/{len(files)} 份推送成功')


if __name__ == '__main__':
    main()
