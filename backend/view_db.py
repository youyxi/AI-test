#!/usr/bin/env python3
"""
查看数据库中的对话信息
"""
import sqlite3
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).parent / "data" / "ai_chat.db"

def print_separator(title=""):
    print("=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)

def view_database():
    if not DB_PATH.exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 查看所有表
        print_separator("1. 数据库表结构")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"表数量: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")

        # 查看用户表
        print_separator("2. 用户表 (users)")
        try:
            cursor.execute("SELECT id, username, email, nickname, created_at FROM users;")
            users = cursor.fetchall()
            print(f"用户数量: {len(users)}")
            for user in users:
                print(f"\n  ID: {user[0]}")
                print(f"  用户名: {user[1]}")
                print(f"  邮箱: {user[2]}")
                print(f"  昵称: {user[3]}")
                print(f"  创建时间: {user[4]}")
        except Exception as e:
            print(f"  (表不存在或为空: {e})")

        # 查看对话表
        print_separator("3. 对话表 (conversations)")
        try:
            cursor.execute("SELECT id, user_id, title, model, provider, created_at, updated_at FROM conversations ORDER BY updated_at DESC;")
            conversations = cursor.fetchall()
            print(f"对话数量: {len(conversations)}")
            for conv in conversations:
                print(f"\n  [对话 {conv[0]}]")
                print(f"  用户ID: {conv[1]}")
                print(f"  标题: {conv[2]}")
                print(f"  模型: {conv[3]}")
                print(f"  提供商: {conv[4]}")
                print(f"  创建时间: {conv[5]}")
                print(f"  更新时间: {conv[6]}")

                # 查看该对话的消息
                cursor.execute("SELECT id, role, content, tokens, created_at FROM messages WHERE conversation_id = ? ORDER BY id;", (conv[0],))
                messages = cursor.fetchall()
                print(f"  消息数量: {len(messages)}")
                for i, msg in enumerate(messages, 1):
                    role = "👤" if msg[1] == "user" else "🤖"
                    content_preview = msg[2][:50] + "..." if len(msg[2]) > 50 else msg[2]
                    print(f"    {i}. {role} [{msg[1]}] - {content_preview}")
                    if msg[3]:
                        print(f"       Token: {msg[3]}")

        except Exception as e:
            print(f"  (表不存在或为空: {e})")

        # 查看消息表
        print_separator("4. 消息表 (messages) - 统计")
        try:
            cursor.execute("SELECT COUNT(*) FROM messages;")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT role, COUNT(*) FROM messages GROUP BY role;")
            by_role = cursor.fetchall()
            print(f"总消息数: {total}")
            for role, count in by_role:
                role_label = "用户" if role == "user" else "AI助手" if role == "assistant" else role
                print(f"  {role_label}: {count} 条")
        except Exception as e:
            print(f"  (表不存在或为空: {e})")

    finally:
        conn.close()
        print_separator()
        print("✅ 查询完成")

if __name__ == "__main__":
    view_database()
