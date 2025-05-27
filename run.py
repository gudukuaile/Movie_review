import os
from app import create_app, db
from app.models import User, Movie, Review

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Movie=Movie, Review=Review)

if __name__ == '__main__':
    app.run(debug=True) 