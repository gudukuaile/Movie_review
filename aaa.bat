@echo off

:: 创建主目录结构
mkdir apps\common\__pycache__ apps\user\__pycache__ apps\movie\__pycache__ apps\review\__pycache__ extend\__pycache__ models\__pycache__ static\css static\js static\images templates\user templates\movie templates\review tests\__pycache__ uploads utils\__pycache__

:: 创建必要的初始化文件
type nul > README.md
type nul > main.py
type nul > requirements.txt
type nul > app.db

:: 创建apps目录下的文件
type nul > apps\__init__.py
type nul > apps\common\__init__.py
type nul > apps\common\dependencies.py
type nul > apps\user\__init__.py
type nul > apps\user\auth.py
type nul > apps\user\crud.py
type nul > apps\user\routes.py
type nul > apps\user\schemas.py
type nul > apps\movie\__init__.py
type nul > apps\movie\crud.py
type nul > apps\movie\routes.py
type nul > apps\movie\schemas.py
type nul > apps\review\__init__.py
type nul > apps\review\crud.py
type nul > apps\review\routes.py
type nul > apps\review\schemas.py

:: 创建extend目录下的文件
type nul > extend\__init__.py
type nul > extend\database.py

:: 创建models目录下的文件
type nul > models\__init__.py
type nul > models\user_models.py
type nul > models\movie_models.py
type nul > models\review_models.py
type nul > models\role_models.py
type nul > models\audit_log_models.py

:: 创建static目录下的文件
type nul > static\__init__.py
type nul > static\css\style.css
type nul > static\js\main.js

:: 创建templates目录下的文件
type nul > templates\__init__.py
type nul > templates\base.html
type nul > templates\admin_base.html
type nul > templates\index.html
type nul > templates\login.html
type nul > templates\register.html
type nul > templates\dashboard.html
type nul > templates\user\__init__.py
type nul > templates\user\profile_view.html
type nul > templates\user\profile_edit.html
type nul > templates\user\list_users.html
type nul > templates\user\edit_user.html
type nul > templates\user\delete_account_confirm.html
type nul > templates\user\password_change.html
type nul > templates\movie\__init__.py
type nul > templates\movie\add_movie.html
type nul > templates\movie\edit_movie.html
type nul > templates\movie\list_movies.html
type nul > templates\review\__init__.py
type nul > templates\review\add_review.html
type nul > templates\review\edit_review.html
type nul > templates\review\list_reviews.html

:: 创建tests目录下的文件
type nul > tests\__init__.py
type nul > tests\conftest.py
type nul > tests\test_main.py
type nul > tests\test_user_auth.py
type nul > tests\test_movie_management.py
type nul > tests\test_review_management.py

:: 创建uploads和utils目录下的文件
type nul > uploads\__init__.py
type nul > utils\__init__.py
type nul > utils\security.py

echo 目录结构创建完成！