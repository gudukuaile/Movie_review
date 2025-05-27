from app import create_app, db
from app.models import Movie, Genre, MovieGenre

def migrate_genres():
    app = create_app('development')
    with app.app_context():
        # 获取所有电影
        movies = Movie.query.all()
        
        for movie in movies:
            if movie.genre:  # 如果电影有类型信息
                # 分割类型字符串
                genres = [g.strip() for g in movie.genre.split('/')]
                
                # 为每个类型创建记录
                for genre_name in genres:
                    # 查找或创建类型
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        db.session.add(genre)
                    
                    # 创建电影-类型关联
                    movie_genre = MovieGenre(movie=movie, genre=genre)
                    db.session.add(movie_genre)
        
        # 提交更改
        try:
            db.session.commit()
            print("类型迁移完成！")
        except Exception as e:
            db.session.rollback()
            print(f"迁移失败：{str(e)}")

if __name__ == '__main__':
    migrate_genres() 