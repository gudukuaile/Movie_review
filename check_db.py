import sqlite3

def check_database():
    # 连接到数据库
    conn = sqlite3.connect('data-dev.sqlite')
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("数据库中的表：")
    for table in tables:
        print(f"\n表名: {table[0]}")
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor.fetchall()
        print("列信息：")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 获取记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
        count = cursor.fetchone()[0]
        print(f"记录数: {count}")
        
        # 如果是movies表，显示一些示例数据
        if table[0] == 'movies':
            cursor.execute("SELECT id, title, rating FROM movies LIMIT 5;")
            movies = cursor.fetchall()
            print("\n示例电影数据：")
            for movie in movies:
                print(f"  ID: {movie[0]}, 标题: {movie[1]}, 评分: {movie[2]}")

    conn.close()

if __name__ == "__main__":
    check_database() 