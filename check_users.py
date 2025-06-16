import sqlite3

def check_users():
    # 连接到数据库
    conn = sqlite3.connect('data-dev.sqlite')
    cursor = conn.cursor()
    
    # 检查用户表
    print("\n=== 用户表数据 ===")
    cursor.execute("SELECT id, username, email, password_hash FROM users;")
    users = cursor.fetchall()
    print(f"用户总数: {len(users)}")
    for user in users:
        print(f"ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}")
        print(f"密码哈希: {user[3]}")
        print("-" * 50)

    conn.close()

if __name__ == "__main__":
    check_users() 