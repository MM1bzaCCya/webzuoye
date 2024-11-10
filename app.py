import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话管理的密钥

# 配置文件上传
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# MySQL数据库配置
db_config = {
    'host': 'localhost',  # 数据库主机地址
    'user': 'root',  # 数据库用户名
    'password': 'MM1bzaCC',  # 数据库密码
    'database': 'flask_app_db'  # 数据库名称
}


# 连接到数据库
def get_db_connection():
    try:
        connection = pymysql.connect(**db_config)
        return connection
    except pymysql.MySQLError as err:
        print("Error connecting to database:", err)
        flash('无法连接到数据库，请检查数据库配置', 'error')
        return None


# 哈希密码
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# 检查文件类型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 登录页面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 验证输入不为空
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return redirect(url_for('login'))

        # 数据库验证
        connection = get_db_connection()
        if connection is None:
            return redirect(url_for('login'))

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        except pymysql.MySQLError as err:
            print("Database error:", err)
            flash('数据库查询出错，请稍后再试', 'error')
            return redirect(url_for('login'))
        finally:
            connection.close()

        if user:
            # 如果用户存在，检查密码
            if user['password'] == hash_password(password):
                session['username'] = username  # 保存用户名到会话中
                session['image_url'] = user['image_url']  # 保存图片URL到会话中
                return redirect(url_for('profile'))
            else:
                flash('密码错误', 'error')
                return redirect(url_for('login'))
        else:
            # 如果用户不存在，跳转到注册页面
            flash('用户不存在，请注册', 'info')
            return redirect(url_for('register'))

    return render_template('a.html')


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        file = request.files['image_file']

        # 验证输入不为空
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return redirect(url_for('register'))

        # 检查文件是否符合允许的类型
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # 保存图片到 images 文件夹

            # 生成图片相对路径以存储到数据库
            image_url = f"{app.config['UPLOAD_FOLDER']}/{filename}"

            # 检查用户名是否已存在
            connection = get_db_connection()
            if connection is None:
                return redirect(url_for('register'))

            cursor = connection.cursor(pymysql.cursors.DictCursor)
            try:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user:
                    flash('用户名已存在，请直接登录', 'error')
                    return redirect(url_for('login'))
                else:
                    # 插入新用户
                    hashed_password = hash_password(password)
                    cursor.execute("INSERT INTO users (username, password, image_url) VALUES (%s, %s, %s)",
                                   (username, hashed_password, image_url))
                    connection.commit()
            except pymysql.MySQLError as err:
                print("Database error during registration:", err)
                flash('注册过程中出错，请稍后再试', 'error')
                return redirect(url_for('register'))
            finally:
                connection.close()

            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        else:
            flash('请上传有效的图片文件', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


# 登录成功后的页面
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        image_url = session.get('image_url')  # 获取存储在会话中的图片URL
        return render_template('b.html', username=username, image_url=image_url)
    else:
        return redirect(url_for('login'))


# 注销会话
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('image_url', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
