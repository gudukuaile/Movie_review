import pandas as pd
from app import create_app, db
from app.models import Movie, Genre, MovieGenre

def process_genres():
    app = create_app('development')
    with app.app_context():
        # 读取Excel文件
        df = pd.read_excel('movie_info_整理版.xlsx')
        
        # 获取所有电影
        movies = Movie.query.all()
        movie_map = {movie.title: movie for movie in movies}
        
        # 用于存储所有唯一的类型
        all_genres = set()
        
        # 遍历Excel数据
        for _, row in df.iterrows():
            if pd.notna(row['类型']):
                # 分割类型字符串（使用空格分割）
                genres = [g.strip() for g in str(row['类型']).split(' ')]
                all_genres.update(genres)
                
                # 获取对应的电影对象
                movie = movie_map.get(row['影片中文名'])
                if movie:
                    # 清除现有的类型关联
                    MovieGenre.query.filter_by(movie_id=movie.id).delete()
                    
                    # 为每个类型创建记录
                    for genre_name in genres:
                        # 查找或创建类型
                        genre = Genre.query.filter_by(name=genre_name).first()
                        if not genre:
                            genre = Genre(name=genre_name)
                            db.session.add(genre)
                            db.session.flush()  # 获取新创建的genre的ID
                        
                        # 创建电影-类型关联
                        movie_genre = MovieGenre(movie=movie, genre=genre)
                        db.session.add(movie_genre)
        
        try:
            db.session.commit()
            print(f"成功处理了 {len(all_genres)} 个不同的类型")
            print("所有类型：", sorted(list(all_genres)))
        except Exception as e:
            db.session.rollback()
            print(f"处理失败：{str(e)}")

if __name__ == '__main__':
    process_genres()

