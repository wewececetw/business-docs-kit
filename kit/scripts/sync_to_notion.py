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
from pathlib import Path
from datetime import datetime

SYNC_FILE = '.business-docs-sync.json'


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
    """從 markdown 提取 metadata"""
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


def md_to_notion_blocks(content):
    """簡化 markdown → Notion blocks 轉換（只支援 H2、段落、清單）"""
    blocks = []
    lines = content.split('\n')

    # 跳過 metadata 區（到第一個 ## 之前）
    start = 0
    for i, line in enumerate(lines):
        if line.startswith('## '):
            start = i
            break

    i = start
    while i < len(lines):
        line = lines[i]

        # 跳過 HTML 註解
        if line.strip().startswith('<!--'):
            while i < len(lines) and '-->' not in lines[i]:
                i += 1
            i += 1
            continue

        if line.startswith('## '):
            blocks.append({
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [{'type': 'text', 'text': {'content': line[3:].strip()}}]
                }
            })
        elif line.startswith('- '):
            blocks.append({
                'type': 'bulleted_list_item',
                'bulleted_list_item': {
                    'rich_text': [{'type': 'text', 'text': {'content': line[2:].strip()}}]
                }
            })
        elif line.strip():
            blocks.append({
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [{'type': 'text', 'text': {'content': line.strip()}}]
                }
            })

        i += 1

    return blocks


def find_existing_page(client, db_id, title):
    """在 Database 中找到同名 page"""
    results = client.databases.query(
        database_id=db_id,
        filter={'property': 'Title', 'title': {'equals': title}}
    )
    if results['results']:
        return results['results'][0]['id']
    return None


def sync_file(client, db_id, filepath, sync_state):
    path = Path(filepath)
    content = path.read_text(encoding='utf-8')
    meta = parse_metadata(content)
    blocks = md_to_notion_blocks(content)

    # 建立 properties
    properties = {
        'Title': {'title': [{'text': {'content': meta['title']}}]},
        '一句話': {'rich_text': [{'text': {'content': meta['oneliner']}}]},
        '分類': {'select': {'name': meta['category'] or '未分類'}},
        '檔案路徑': {'rich_text': [{'text': {'content': str(filepath)}}]},
    }
    if meta['last_updated']:
        properties['最後更新'] = {'date': {'start': meta['last_updated']}}

    # 檢查是否已有對應 page
    page_id = sync_state.get(str(filepath), {}).get('notion_page_id')

    if not page_id:
        page_id = find_existing_page(client, db_id, meta['title'])

    if page_id:
        # 更新既有 page
        try:
            client.pages.update(page_id=page_id, properties=properties)
            # 清除舊 blocks 再新增
            existing = client.blocks.children.list(block_id=page_id)
            for block in existing['results']:
                try:
                    client.blocks.delete(block_id=block['id'])
                except Exception:
                    pass
            if blocks:
                client.blocks.children.append(block_id=page_id, children=blocks)
            action = '更新'
        except Exception as e:
            print(f'  ❌ 更新失敗: {e}')
            return None
    else:
        # 新建 page
        try:
            page = client.pages.create(
                parent={'database_id': db_id},
                properties=properties,
                children=blocks
            )
            page_id = page['id']
            action = '新建'
        except Exception as e:
            print(f'  ❌ 新建失敗: {e}')
            return None

    # 更新 sync state
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

    try:
        from notion_client import Client
    except ImportError:
        print('❌ 請先安裝 notion-client: pip3 install notion-client')
        sys.exit(1)

    client = Client(auth=token)

    # 收集要推送的檔案
    if len(sys.argv) < 2 or sys.argv[1] == '--all':
        files = sorted(Path('docs/business').glob('*.md'))
        files = [f for f in files if f.name != 'README.md' and not f.name.startswith('_')]
    else:
        files = []
        for arg in sys.argv[1:]:
            p = Path(arg)
            if not p.exists():
                # 嘗試補全路徑
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
        result = sync_file(client, db_id, f, sync_state)
        if result:
            success += 1

    save_sync_state(sync_state)
    print(f'\n完成：{success}/{len(files)} 份推送成功')


if __name__ == '__main__':
    main()
