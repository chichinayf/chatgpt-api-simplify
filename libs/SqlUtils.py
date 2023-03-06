import sqlite3
import libs.MyMainWindow

# 数据库连接
from libs import MyMainWindow

conn = None


# 定义一个 DBConnectionError 异常，用于表示数据库连接失败
class DBConnectionError(Exception):
    pass


# 定义一个 数据库操作的utils

def create_data_base():
    # 创建数据库连接
    global conn
    conn = sqlite3.connect("database.db")
    # 创建表
    conn.cursor().execute(
        """CREATE TABLE IF NOT EXISTS chats (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           types TEXT,
           ask TEXT,
           answer TEXT,
           answers TEXT,
           conversation_id TEXT,
           is_del INTEGER default 0
           )"""
    )
    # 提交事务
    conn.commit()
    # 关闭连接
    conn.close()


# 保存数据到数据库
def execute_query_sql(sql, param):
    global conn
    try:
        # 创建数据库连接
        conn = sqlite3.connect("database.db")
        # 查询数据
        cursor = conn.cursor()
        cursor.execute(sql, param)
        if cursor:
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            # 关闭连接
            conn.close()
            return columns, rows
        else:
            return [], []
    except sqlite3.Error as err:
        # 如果连接失败，抛出 DBConnectionError 异常
        conn.close()
        raise DBConnectionError("数据库连接失败，保存到本地失败") from err


# 查询数据库数据
def execute_update_sql(sql, param):
    global conn
    try:
        # 创建数据库连接
        conn = sqlite3.connect("database.db")
        # 查询数据
        cursor = conn.cursor()
        cursor.execute(sql, param)
        if cursor:
            rows = cursor.fetchall()
            # 关闭连接
            conn.commit()
            conn.close()
            return rows
        else:
            return 0
    except sqlite3.Error as err:
        # 如果连接失败，抛出 DBConnectionError 异常
        conn.close()
        raise DBConnectionError("数据库连接失败，保存到本地失败") from err


# 更新数据库数据
def save_data_to_database(ask, answer, answers):
    global conn
    try:
        conn = sqlite3.connect("database.db")
        # 插入数据
        conn.cursor().execute(
            'INSERT INTO chats (types,conversation_id,ask,answer,answers,is_del) VALUES (?, ?, ?, ?, ?, ?)',
            (MyMainWindow.formatted_time, "", ask, answer, answers, 0))
        # 提交事务
        conn.commit()
        # 关闭连接
        conn.close()
    except sqlite3.Error as err:
        # 关闭连接
        conn.close()
        # 消息提示打印出来
        # 如果连接失败，抛出 DBConnectionError 异常
        raise DBConnectionError("数据库连接失败，保存到本地失败") from err
