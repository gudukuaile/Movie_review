import sqlite3
from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def fix_password_hashes():
    # 连接到数据库
    conn = sqlite3.connect('data-dev.sqlite')
    cursor = conn.cursor()
    
    # 获取所有用户
    cursor.execute("SELECT id, username, email FROM users;")
    users = cursor.fetchall()
    
    # 为每个用户重置密码
    for user in users:
        user_id, username, email = user
        # 设置默认密码为 "123123"
        new_hash = pwd_context.hash("123123")
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_hash, user_id)
        )
        print(f"已重置用户 {username} ({email}) 的密码为: 123123")
    
    # 提交更改
    conn.commit()
    conn.close()
    print("\n所有用户的密码已重置为: 123123")

if __name__ == "__main__":
    fix_password_hashes() 