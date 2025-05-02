import os
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于session和flash消息

# 确保数据目录存在
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 文章和用户数据文件路径
POSTS_FILE = os.path.join(DATA_DIR, 'posts.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# 初始化数据文件
def init_data_files():
    # 初始化文章数据文件
    if not os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    # 初始化用户数据文件
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

# 获取所有文章
def get_posts():
    try:
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# 保存文章
def save_posts(posts):
    with open(POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

# 获取所有用户
def get_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# 保存用户
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# 首页 - 显示所有文章
@app.route('/')
def index():
    posts = get_posts()
    posts.sort(key=lambda x: x['date'], reverse=True)  # 按日期降序排序
    return render_template('index.html', posts=posts)

# 查看单篇文章
@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = get_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    if post:
        return render_template('post.html', post=post)
    flash('文章不存在', 'error')
    return redirect(url_for('index'))

# 创建新文章页面
@app.route('/new', methods=['GET', 'POST'])
def new_post():
    # 检查用户是否登录
    if 'username' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('标题和内容不能为空', 'error')
            return render_template('new_post.html')
        
        posts = get_posts()
        # 生成新文章ID
        post_id = 1 if not posts else max(post['id'] for post in posts) + 1
        
        # 创建新文章
        new_post = {
            'id': post_id,
            'title': title,
            'content': content,
            'author': session['username'],
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        posts.append(new_post)
        save_posts(posts)
        
        flash('文章发布成功', 'success')
        return redirect(url_for('view_post', post_id=post_id))
    
    return render_template('new_post.html')

# 编辑文章
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    # 检查用户是否登录
    if 'username' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    
    posts = get_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    
    if not post:
        flash('文章不存在', 'error')
        return redirect(url_for('index'))
    
    # 检查是否是文章作者
    if post['author'] != session['username']:
        flash('您没有权限编辑此文章', 'error')
        return redirect(url_for('view_post', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('标题和内容不能为空', 'error')
            return render_template('edit_post.html', post=post)
        
        # 更新文章
        post['title'] = title
        post['content'] = content
        post['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 更新日期
        
        save_posts(posts)
        
        flash('文章更新成功', 'success')
        return redirect(url_for('view_post', post_id=post_id))
    
    return render_template('edit_post.html', post=post)

# 删除文章
@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    # 检查用户是否登录
    if 'username' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    
    posts = get_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    
    if not post:
        flash('文章不存在', 'error')
        return redirect(url_for('index'))
    
    # 检查是否是文章作者
    if post['author'] != session['username']:
        flash('您没有权限删除此文章', 'error')
        return redirect(url_for('view_post', post_id=post_id))
    
    # 删除文章
    posts.remove(post)
    save_posts(posts)
    
    flash('文章已删除', 'success')
    return redirect(url_for('index'))

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('register.html')
        
        users = get_users()
        
        # 检查用户名是否已存在
        if any(user['username'] == username for user in users):
            flash('用户名已存在', 'error')
            return render_template('register.html')
        
        # 创建新用户
        new_user = {
            'username': username,
            'password': password  # 注意：实际应用中应该对密码进行哈希处理
        }
        
        users.append(new_user)
        save_users(users)
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('login.html')
        
        users = get_users()
        user = next((u for u in users if u['username'] == username), None)
        
        if not user or user['password'] != password:  # 注意：实际应用中应该对密码进行哈希比较
            flash('用户名或密码错误', 'error')
            return render_template('login.html')
        
        # 登录成功，设置session
        session['username'] = username
        flash('登录成功', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

# 登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('已登出', 'success')
    return redirect(url_for('index'))

# 初始化数据文件
init_data_files()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)