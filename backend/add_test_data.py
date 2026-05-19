#!/usr/bin/env python3
"""
添加测试数据到数据库
"""
import sqlite3
from pathlib import Path
from datetime import datetime

# 数据库文件路径
DB_PATH = Path(__file__).parent / "data" / "ai_chat.db"

def add_test_data():
    if not DB_PATH.exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("📝 开始添加测试数据...")

        # 获取当前用户ID
        cursor.execute("SELECT id FROM users LIMIT 1;")
        user = cursor.fetchone()
        if not user:
            print("❌ 没有找到用户，请先注册")
            return
        user_id = user[0]

        # 测试对话1
        print("\n添加对话 1: Python入门教程")
        cursor.execute(
            """
            INSERT INTO conversations (user_id, title, model, provider, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, "Python入门教程", "gpt-3.5-turbo", "openai",
             datetime.now().isoformat(), datetime.now().isoformat())
        )
        conv1_id = cursor.lastrowid

        # 添加消息
        messages1 = [
            ("user", "你好，我想学习Python"),
            ("assistant", "你好！欢迎学习Python。Python是一门简洁优雅的编程语言。"),
            ("user", "如何打印Hello World？"),
            ("assistant", "很简单！在Python中，只需：\n\n```python\nprint('Hello World')\n```\n\n这样就可以了！"),
        ]

        for role, content in messages1:
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (conv1_id, role, content, datetime.now().isoformat())
            )

        # 测试对话2
        print("添加对话 2: AI聊天测试")
        cursor.execute(
            """
            INSERT INTO conversations (user_id, title, model, provider, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, "AI聊天测试", "gpt-4", "openai",
             datetime.now().isoformat(), datetime.now().isoformat())
        )
        conv2_id = cursor.lastrowid

        messages2 = [
            ("user", "你能帮我写个故事吗？"),
            ("assistant", "当然！请告诉我你想要什么类型的故事？"),
            ("user", "科幻类型的，关于太空探险的"),
            ("assistant", "好的！这是一个关于太空探险的故事...\n\n在遥远的2157年，人类已经开始探索银河系边缘的新星系..."),
        ]

        for role, content in messages2:
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (conv2_id, role, content, datetime.now().isoformat())
            )

        # 测试对话3
        print("添加对话 3: DeepSeek 模型测试")
        cursor.execute(
            """
            INSERT INTO conversations (user_id, title, model, provider, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, "DeepSeek 模型测试", "deepseek-chat", "deepseek",
             datetime.now().isoformat(), datetime.now().isoformat())
        )
        conv3_id = cursor.lastrowid

        messages3 = [
            ("user", "你好，请介绍一下你自己"),
            ("assistant", "你好！我是DeepSeek AI助手。很高兴为您服务！"),
        ]

        for role, content in messages3:
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (conv3_id, role, content, datetime.now().isoformat())
            )

        conn.commit()
        print("\n✅ 测试数据添加成功！")
        print(f"  - 添加了 {3} 个对话")
        print(f"  - 添加了 {len(messages1) + len(messages2) + len(messages3)} 条消息")

    finally:
        conn.close()

if __name__ == "__main__":
    add_test_data()
