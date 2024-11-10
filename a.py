import pymysql

# 数据库配置
db_config = {
    'host': 'localhost',           # 数据库主机地址
    'user': 'root',                # 数据库用户名
    'password': 'MM1bzaCC',        # 数据库密码
    'database': 'flask_app_db'     # 数据库名称
}

def test_db_connection():
    try:
        # 尝试连接到数据库
        connection = pymysql.connect(**db_config)
        print("数据库连接成功！")

        # 创建游标并执行查询
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users")

            # 获取查询结果并打印
            users = cursor.fetchall()
            if users:
                print("查询到的用户记录：")
                for user in users:
                    print(user)
            else:
                print("未查询到任何用户记录。")

    except pymysql.MySQLError as err:
        print("数据库连接或查询失败:", err)

    finally:
        # 确保在最后关闭数据库连接
        if 'connection' in locals() and connection.open:
            connection.close()
            print("数据库连接已关闭。")

if __name__ == "__main__":
    test_db_connection()
