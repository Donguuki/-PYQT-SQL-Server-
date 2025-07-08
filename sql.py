import pymssql
import numpy
import pyodbc

 
 # 定义查询函数
def query(table,cursor,conn):
    """
    查询函数
    """
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'"%table
    cursor.execute(sql)
    title = numpy.array(cursor.fetchall()).flatten()
    print("表内有元素：",title,"请输入你要查询的条件？\n")
    condition = input("请输入条件：")
    sql = "SELECT * FROM %s WHERE %s"%(table,condition)
    try:
        cursor.execute(sql)
        conn.commit()  # 提交事务
        results = numpy.array(cursor.fetchall())
        for row in results:
            print(dict(zip(title,row)))
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        print("查询失败：", e)

    
    


def getvalues(table, cursor, conn):
    """
    插入数据函数
    """
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'"%table
    cursor.execute(sql)
    title = numpy.array(cursor.fetchall()).flatten()
    values = []
    i = 0
    for col in title:
        val = input(f"请输入字段 {col} 的值：")
        values.append(val)
        i=i+1
    return values
    


def delete(table, cursor, conn):
    """
    删除数据函数
    """
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'"%table
    cursor.execute(sql)
    title = numpy.array(cursor.fetchall()).flatten()
    print("表内的列名：", title)
    condition = input("请输入删除的条件（例如 id=1）：")
    sql = "DELETE FROM %s WHERE %s"%(table, condition)
    try:
        cursor.execute(sql)
        conn.commit()  # 提交事务
        print("数据删除成功！")
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        print("删除失败：", e)

def update(table, cursor, conn):
    """
    更新数据函数
    """
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'"%table
    cursor.execute(sql)
    title = numpy.array(cursor.fetchall()).flatten()
    print("表内的列名：", title)
    set_clause = input("请输入更新内容（例如 name='新名字'）：")
    condition = input("请输入更新的条件（例如 id=1）：")
    sql = "UPDATE %s SET %s WHERE %s"%(table, set_clause, condition)
    try:
        cursor.execute(sql)
        conn.commit()  # 提交事务
        print("数据更新成功！")
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        print("更新失败：", e)



  
 
    







def init_sql(username,password_in):
    """
    初始化数据库连接
    """
# 打开数据库连接
    db1 = pymssql.connect(server='localhost',
                     user=username,
                     password=password_in,
                     database='student_management'
                    )
    db2 = pymssql.connect(server='localhost',
                     user=username,
                     password=password_in,
                     database='student_management'
                    )
 
# 创建一个游标对象
    cursor1 = db1.cursor()
    db1.autocommit(True)
    cursor2 = db2.cursor()
    db2.autocommit(True)
# 查看现有表
    sql = "SELECT NAME FROM student_management.SYS.TABLES"
    msg = cursor1.execute(sql)
    now_table=cursor1.fetchall()

    return db1,cursor1,db2,cursor2,now_table



