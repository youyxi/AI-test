#!/usr/bin/env python3
"""
详细查看单个对话
"""
import sqlite3
import sys
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).parent / "data" / "ai_chat.db"

def view_conversation_detail(conversation_id):
    if not DB_PATH.exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 获取对话信息
        cursor.execute(
            "SELECT id, user_id, title, model, provider, created_at, updated_at FROM conversations WHERE id = ?;",
            (conversation_id,)
        )
        conv = cursor.fetchone()

        if not conv:
            print(f"❌ 没有找到ID为 {conversation_id} 的对话")
            return

        print("=" * 80)
        print(f"  对话详情 - ID: {conv[0]}")
        print("=" * 80)
        print(f"  标题: {conv[2]}")
        print(f"  模型: {conv[3]}")
        print(f"  提供商: {conv[4]}")
        print(f"  创建时间: {conv[5]}")
        print(f"  更新时间: {conv[6]}")
        print("=" * 80)
        print("\n  消息列表:")
        print("-" * 80)

        # 获取所有消息
        cursor.execute(
            "SELECT id, role, content, tokens, created_at FROM messages WHERE conversation_id = ? ORDER BY id;",
            (conversation_id,)
        )
        messages = cursor.fetchall()

        for i, msg in enumerate(messages, 1):
            print(f"\n  [{i}] {msg[1].upper()}")
            print("-" * 40)
            print(f"  {msg[2]}")
            if msg[3]:
                print(f"  (Tokens: {msg[3]})")
            print(f"  时间: {msg[4]}")
            print()

        print("=" * 80)

    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        conv_id = int(sys.argv[1])
        view_conversation_detail(conv_id)
    else:
        print("用法: python view_conversation.py <对话ID>")
        print("\n例如: python view_conversation.py 1")
        print("\n提示: 先运行 python view_db.py 查看可用的对话ID")
