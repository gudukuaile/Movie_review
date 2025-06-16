import sqlite3

def check_database():
    # 连接到数据库
    conn = sqlite3.connect('data-dev.sqlite')
    cursor = conn.cursor()
    
    # 检查电影表
    print("\n=== 电影表数据 ===")
    cursor.execute("SELECT COUNT(*) FROM movies;")
    movie_count = cursor.fetchone()[0]
    print(f"电影总数: {movie_count}")
    
    # 检查分类表
    print("\n=== 分类表数据 ===")
    cursor.execute("SELECT * FROM genres;")
    genres = cursor.fetchall()
    print(f"分类总数: {len(genres)}")
    for genre in genres:
        print(f"分类ID: {genre[0]}, 名称: {genre[1]}")
    
    # 检查电影-分类关联表
    print("\n=== 电影-分类关联数据 ===")
    cursor.execute("SELECT COUNT(*) FROM movie_genres;")
    relation_count = cursor.fetchone()[0]
    print(f"关联关系总数: {relation_count}")
    
    # 检查每个分类下的电影数量
    print("\n=== 每个分类下的电影数量 ===")
    cursor.execute("""
        SELECT g.name, COUNT(mg.movie_id) 
        FROM genres g 
        LEFT JOIN movie_genres mg ON g.id = mg.genre_id 
        GROUP BY g.id, g.name;
    """)
    genre_counts = cursor.fetchall()
    for genre_name, count in genre_counts:
        print(f"分类 '{genre_name}' 下的电影数量: {count}")
    
    # 检查一些具体的关联数据
    print("\n=== 示例关联数据 ===")
    cursor.execute("""
        SELECT m.title, g.name 
        FROM movies m 
        JOIN movie_genres mg ON m.id = mg.movie_id 
        JOIN genres g ON g.id = mg.genre_id 
        LIMIT 5;
    """)
    examples = cursor.fetchall()
    for movie_title, genre_name in examples:
        print(f"电影 '{movie_title}' 属于分类 '{genre_name}'")

    conn.close()

if __name__ == "__main__":
    check_database() 