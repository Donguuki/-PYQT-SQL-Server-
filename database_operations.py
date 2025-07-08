import pymssql
import numpy
import pyodbc

def init_db():
    db = pymssql.connect(server='localhost',user='sa',password='20040323Ww',database='student_management',charset='cp936')
    cursor = db.cursor()
    cursor.execute("SELECT NAME FROM student_management.SYS.TABLES")
    tables = cursor.fetchall()
    return db, cursor, tables

def query(table, cursor, conn,condition,mode=0):
    """
    查询函数
    """
    i=0
    a={}
    b={}
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'" % table
    cursor.execute(sql)
    if mode==0:
        title = numpy.array(cursor.fetchall()).flatten()
    else:
        title = numpy.array(['成绩','学号'])
    print("表内有元素：", title, "请输入你要查询的条件？\n")
    #condition = input("请输入条件：")
    if mode==0:
        sql = "SELECT * FROM %s WHERE %s" % (table, condition)
    else:
        sql = "SELECT class_grade,student_id FROM %s WHERE %s" % (table, condition)
    try:
        cursor.execute(sql)
        conn.commit()  # 提交事务
   
        results = numpy.array(cursor.fetchall())
        
            
        for row in results:
            a[i]=dict(zip(title, row))
            i=i+1
        return a
    except Exception as e:
            conn.rollback()  # 发生错误时回滚
            print("查询失败：", e)

def insert(table, cursor, conn,values):
    """
    插入数据函数
    """
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'" % table
    cursor.execute(sql)
    title = numpy.array(cursor.fetchall()).flatten()
    print("表内的列名：", title)

    
    placeholders = ", ".join(["%s"] * len(title))  # 生成与列数匹配的占位符
    column_names = ", ".join(title)  # 生成列名字符串

    sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
    try:
        cursor.execute(sql, values)
        conn.commit()  # 提交事务
        print("数据插入成功！")
        return 1
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        print("插入失败：", e)
        return 0

def delete(table, cursor, conn,condition):
    """
    删除数据函数
    """
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'" % table
    cursor.execute(sql)
    title = numpy.array(cursor.fetchall()).flatten()
    print("表内的列名：", title)
    sql = "DELETE FROM %s WHERE %s" % (table, condition)
    try:
        cursor.execute(sql)
        conn.commit()  # 提交事务
        print("数据删除成功！")
        return 1
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        print("删除失败：", e)
        return 0

def update(table, cursor, conn,condition,set_clause):
    """
    更新数据函数
    """
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'" % table
    cursor.execute(sql)
    title = numpy.array(cursor.fetchall()).flatten()
    print("表内的列名：", title)
    
    sql = "UPDATE %s SET %s WHERE %s" % (table, set_clause, condition)
    try:
        cursor.execute(sql)
        conn.commit()  # 提交事务
        print("数据更新成功！")
        return 1
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        print("更新失败：", e)
        return 0

def get_title(table, cursor):
    """
    获得标题函数
    """
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'" % table
    cursor.execute(sql)
    title = numpy.array(cursor.fetchall()).flatten()
    return title