# coding:utf-8
import sys

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices,QStandardItemModel,QStandardItem,QPalette,QBrush,QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout,QVBoxLayout,QCompleter,QWidget,QGridLayout,QMainWindow,QLabel,QLineEdit
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, MSFluentWindow,ImageLabel,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont,setFont, ComboBox,LineEdit,PushButton,TextEdit,TeachingTip,TeachingTipTailPosition,BodyLabel)
from qfluentwidgets import FluentIcon as FIF
from database_operations import *
from sql import init_sql
from database_operations import init_db, query, insert, delete, update,get_title






class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)

   
        self.setObjectName(text.replace(' ', '-'))



class Window(MSFluentWindow):

    def __init__(self,username, password,):
        super().__init__()
        self.password=password
        self.username=username

        # create sub interface
        self.homeInterface = QueryPage(self)
        self.appInterface = InsertPage(self)
        self.videoInterface = UpdataPage(self)
        self.libraryInterface = DeletePage(self)
        # add sub interface
        self.otherface=OthertherPage(self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.SEARCH, '查询', FIF.HOME_FILL)
        self.addSubInterface(self.appInterface, FIF.ADD, '插入')
        self.addSubInterface(self.videoInterface, FIF.UPDATE, '更改')
        self.addSubInterface(self.libraryInterface, FIF.DELETE, '删除')
        self.addSubInterface(self.otherface, FIF.GAME, '特殊功能')

        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.setGeometry(100, 100, 1200, 900)
        self.setWindowIcon(QIcon('image.png'))
        self.setWindowTitle('学生管理系统')

        

class QueryPage(Widget):
    def __init__(self, parent=None):
        super().__init__('查询', parent)
        self.db1, self.cursor1,self.db2,self.cursor2, self.tables = init_sql("sa","20040323Ww") # 使用已有的数据库初始化函数
        self.initUI()

    def initUI(self):
        """初始化UI组件"""
        # 设置 ComboBox 用于选择表名
        self.tableInput = ComboBox(self)
        self.tableInput.setPlaceholderText("选择一个表")
        self.tableInput.addItems([table[0] for table in self.tables])  # 添加表名
        self.tableInput.setFixedSize(300, 40)
        self.tableInput.setCurrentIndex(-1)

        # 查询条件输入框
        self.conditionInput = LineEdit(self)
        self.conditionInput.setPlaceholderText("请输入查询条件")
        self.stands = [
    "class_id",
    "class_name",
    "department",
    "student_id",
    "student_name",
    "grade",
    "student_relation_id",
    "student_relation_name",
    "1=1"
]
        completer = QCompleter(self.stands, self.conditionInput)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setMaxVisibleItems(10)
        self.conditionInput.setCompleter(completer)
        self.conditionInput.setFixedSize(300, 40)

        # 查询按钮
        self.queryButton = PushButton('查询', self)
        self.queryButton.setFixedSize(200, 40)
        self.queryButton.clicked.connect(self.perform_query)

        # 设置 textEdit 用于展示查询结果
        self.textEdit= TextEdit(self)

        # 布局设置
        layout = QVBoxLayout(self)
        layout.addWidget(self.tableInput)
        layout.addWidget(self.conditionInput)
        layout.addWidget(self.queryButton)
        layout.addWidget(self.textEdit)

    def perform_query(self):
        """执行查询操作"""
        table = self.tableInput.currentText()  # 获取用户选择的表名
        condition = self.conditionInput.text()  # 获取查询条件
        if table and condition:
            result=query(table,self.cursor2,self.db2,condition)
            if table=="t_grade":
                self.display_result(result,15,20)
            else:
                self.display_result(result,25,25)
    def display_result(self, result, column_width=15, font_size=12):
        """
        显示表格数据，支持中英文混排对齐。

        Args:
            result (dict): 输入数据，格式为字典，键为行号，值为字典，每行的数据。
            column_width (int): 每列的宽度（单位：字符数，中文占 2，英文占 1）。
            font_size (int): 设置字体大小，用于 QTextEdit。
        """
        try:
            # 设置字体大小
            font = self.textEdit.font()
            font.setPointSize(font_size)
            self.textEdit.setFont(font)

            # 获取列标题
            first_row = next(iter(result.values()))
            if not isinstance(first_row, dict):
                raise ValueError("result 的值必须是字典类型。")
            
            headers = list(first_row.keys())  # 提取列标题
            headers = [str(header) for header in headers]  # 确保标题是字符串

            # 对每个字段进行格式化并填充到固定宽度
            table_output = []  # 存储表格内容
            formatted_headers = []
            for header in headers:
                header_str = str(header)  # 确保转换为字符串
                char_count = sum(2 if ord(c) > 127 else 1 for c in header_str)  # 计算当前宽度，判断是否为中文
                padding = column_width - char_count
                if padding > 0:
                    header_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                else:
                    header_str = header_str[:column_width]  # 截断超出的部分
                formatted_headers.append(header_str)

            table_output.append("".join(formatted_headers))  # 添加标题行
            table_output.append("-" * (column_width * len(headers)))  # 分隔线

            # 遍历每一行并格式化
            for row in result.values():
                formatted_row = []
                for header in headers:
                    value_str = str(str(row.get(header, "")).encode('latin').decode('GBK'))  # 确保转换为字符串,12/13增加编解码，解决中文乱码，连接字符集统一为为utf8
                    char_count = sum(2 if ord(c) > 127 else 1 for c in value_str)  # 计算当前宽度
                    padding = column_width - char_count
                    if padding > 0:
                        value_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                    else:
                        value_str = value_str[:column_width]  # 截断超出的部分
                    formatted_row.append(value_str)
                table_output.append("".join(formatted_row))

            # 显示格式化的表格内容
            self.textEdit.clear()
            self.textEdit.append("\n".join(table_output))

        except Exception as e:
            self.textEdit.append(f"错误: {str(e)}")

class InsertPage(Widget):
    def __init__(self, parent=None):
        super().__init__('插入', parent)
        self.db1, self.cursor1,self.db2,self.cursor2, self.tables = init_sql("sa","20040323Ww") # 使用已有的数据库初始化函数
        self.initUI()

    def initUI(self):
        """初始化UI组件"""
        # 设置 ComboBox 用于选择表名
        self.tableInput = ComboBox(self)
        self.tableInput.setPlaceholderText("选择一个表")
        self.tableInput.addItems([table[0] for table in self.tables])  # 添加表名
        self.tableInput.setFixedSize(300, 40)
        self.tableInput.setCurrentIndex(-1)
        self.tableInput.currentIndexChanged.connect(self.changehoderText)

        # 查询条件输入框
        self.valueInput = LineEdit(self)
        self.valueInput.setPlaceholderText("请输入元素：")
        self.valueInput.setFixedSize(320, 40)

        # 查询按钮
        self.InsertButton = PushButton('插入', self)
        self.InsertButton.setFixedSize(200, 40)
        self.InsertButton.clicked.connect(self.perform_insert)

        # 设置 textEdit 用于展示查询结果
        self.textEdit= TextEdit(self)

        # 布局设置
        layout = QVBoxLayout(self)
        layout.addWidget(self.tableInput)
        layout.addWidget(self.valueInput)
        layout.addWidget(self.InsertButton)
        layout.addWidget(self.textEdit)

    def perform_insert(self):
        """执行查询操作"""
        value_tuple=[]
        table = self.tableInput.currentText()  
        value = self.valueInput.text()
        value=value.split(",") 
        value_tuple = list(value)
        if insert(table,self.cursor2,self.db2,value_tuple)==1:
            self.show_success()
            self.perform_query()
        
    def changehoderText(self):
        table = self.tableInput.currentText()  # 获取用户选择的表名
        if table=="t_department":
            self.valueInput.setPlaceholderText("请输入院系编号，院系名称")
        if table=="t_classinfo":
            self.valueInput.setPlaceholderText("请输入课程名称，课程编号")
        if table=="t_grade":
            self.valueInput.setPlaceholderText("请输入成绩，课程名称，课程编号，学生学号")
        if table=="t_student_info":
            self.valueInput.setPlaceholderText("请输入学生学号，学生姓名")
        if table=="t_studentrelation":
            self.valueInput.setPlaceholderText("请输入院系编号，学生学号")
    def show_success(self):
        TeachingTip.create(
            target=self.InsertButton,
            icon="Success",
            title='插入提示',
            content="插入成功！",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    def perform_query(self):
        """执行查询操作"""
        table = self.tableInput.currentText()  # 获取用户选择的表名
        condition = '1=1'  # 获取查询条件
        if table and condition:
            result=query(table,self.cursor2,self.db2,condition)
            if table=="t_grade":
                self.display_result(result,15,20)
            else:
                self.display_result(result,25,25)
    def display_result(self, result, column_width=15, font_size=12):
        """
        显示表格数据，支持中英文混排对齐。

        Args:
            result (dict): 输入数据，格式为字典，键为行号，值为字典，每行的数据。
            column_width (int): 每列的宽度（单位：字符数，中文占 2，英文占 1）。
            font_size (int): 设置字体大小，用于 QTextEdit。
        """
        try:
            # 设置字体大小
            font = self.textEdit.font()
            font.setPointSize(font_size)
            self.textEdit.setFont(font)

            # 获取列标题
            first_row = next(iter(result.values()))
            if not isinstance(first_row, dict):
                raise ValueError("result 的值必须是字典类型。")
            
            headers = list(first_row.keys())  # 提取列标题
            headers = [str(header) for header in headers]  # 确保标题是字符串

            # 对每个字段进行格式化并填充到固定宽度
            table_output = []  # 存储表格内容
            formatted_headers = []
            for header in headers:
                header_str = str(header)  # 确保转换为字符串
                char_count = sum(2 if ord(c) > 127 else 1 for c in header_str)  # 计算当前宽度，判断是否为中文
                padding = column_width - char_count
                if padding > 0:
                    header_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                else:
                    header_str = header_str[:column_width]  # 截断超出的部分
                formatted_headers.append(header_str)

            table_output.append("".join(formatted_headers))  # 添加标题行
            table_output.append("-" * (column_width * len(headers)))  # 分隔线

            # 遍历每一行并格式化
            for row in result.values():
                formatted_row = []
                for header in headers:
                    value_str = str(str(row.get(header, "")).encode('latin').decode('GBK'))  # 确保转换为字符串,12/13增加编解码，解决中文乱码，连接字符集统一为为utf8
                    char_count = sum(2 if ord(c) > 127 else 1 for c in value_str)  # 计算当前宽度
                    padding = column_width - char_count
                    if padding > 0:
                        value_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                    else:
                        value_str = value_str[:column_width]  # 截断超出的部分
                    formatted_row.append(value_str)
                table_output.append("".join(formatted_row))

            # 显示格式化的表格内容
            self.textEdit.clear()
            self.textEdit.append("\n".join(table_output))

        except Exception as e:
            self.textEdit.append(f"错误: {str(e)}")


        
class UpdataPage(Widget):
    def __init__(self, parent=None):
        super().__init__('更改', parent)
        self.db1, self.cursor1,self.db2,self.cursor2, self.tables = init_sql("sa","20040323Ww") # 使用已有的数据库初始化函数
        self.initUI()

    def initUI(self):
        """初始化UI组件"""
        # 设置 ComboBox 用于选择表名
        self.tableInput = ComboBox(self)
        self.tableInput.setPlaceholderText("选择一个表")
        self.tableInput.addItems([table[0] for table in self.tables])  # 添加表名
        self.tableInput.setFixedSize(300, 40)
        self.tableInput.setCurrentIndex(-1)
        self.tableInput.currentIndexChanged.connect(self.changehoderText)

        # 改变条件输入框
        self.conditionInput = LineEdit(self)
        self.conditionInput.setPlaceholderText("请更改条件：")
        self.conditionInput.setFixedSize(320, 40)
        self.stands = [
    "class_id",
    "class_name",
    "department",
    "student_id",
    "student_name",
    "grade",
    "student_relation_id",
    "student_relation_name",
    "1=1"
]
        completer = QCompleter(self.stands, self.conditionInput)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setMaxVisibleItems(10)
        self.conditionInput.setCompleter(completer)
        # 改变元素输入框
        self.valueInput = LineEdit(self)
        self.valueInput.setPlaceholderText("请输入更改结果：")
        self.valueInput.setFixedSize(320, 40)
        self.stands2 = [
    "class_id",
    "class_name",
    "department",
    "student_id",
    "student_name",
    "grade",
    "student_relation_id",
    "student_relation_name",
    "1=1"
]
        completer2 = QCompleter(self.stands2, self.valueInput)
        completer2.setCaseSensitivity(Qt.CaseInsensitive)
        completer2.setMaxVisibleItems(10)
        self.valueInput.setCompleter(completer2)

        # 查询按钮
        self.InsertButton = PushButton('更改', self)
        self.InsertButton.setFixedSize(200, 40)
        self.InsertButton.clicked.connect(self.perform_updata)

        # 设置 textEdit 用于展示查询结果
        self.textEdit= TextEdit(self)

        # 布局设置
        layout = QVBoxLayout(self)
        layout.addWidget(self.tableInput)
        layout.addWidget(self.conditionInput)
        layout.addWidget(self.valueInput)
        layout.addWidget(self.InsertButton)
        layout.addWidget(self.textEdit)

    def perform_updata(self):
        """执行查询操作"""
        value_tuple=[]
        table = self.tableInput.currentText() 
        condition = self.conditionInput.text() 
        value = self.valueInput.text()
        if update(table,self.cursor2,self.db2,condition,value)==1:
            self.show_success()
            self.perform_query()
        
    def changehoderText(self):
        table = self.tableInput.currentText()  # 获取用户选择的表名
        if table=="t_department":
            self.valueInput.setPlaceholderText("请输入院系编号，院系名称")
        if table=="t_classinfo":
            self.valueInput.setPlaceholderText("请输入课程名称，课程编号")
        if table=="t_grade":
            self.valueInput.setPlaceholderText("请输入成绩，课程名称，课程编号，学生学号")
        if table=="t_student_info":
            self.valueInput.setPlaceholderText("请输入学生学号，学生姓名")
        if table=="t_student_relation":
            self.valueInput.setPlaceholderText("请输入院系编号，学生学号")
    def show_success(self):
        TeachingTip.create(
            target=self.InsertButton,
            icon="Success",
            title='更改提示',
            content="更改成功！",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    def perform_query(self):
        """执行查询操作"""
        table = self.tableInput.currentText()  # 获取用户选择的表名
        condition = '1=1'  # 获取查询条件
        if table and condition:
            result=query(table,self.cursor2,self.db2,condition)
            if table=="t_grade":
                self.display_result(result,15,20)
            else:
                self.display_result(result,25,25)
    def display_result(self, result, column_width=15, font_size=12):
        """
        显示表格数据，支持中英文混排对齐。

        Args:
            result (dict): 输入数据，格式为字典，键为行号，值为字典，每行的数据。
            column_width (int): 每列的宽度（单位：字符数，中文占 2，英文占 1）。
            font_size (int): 设置字体大小，用于 QTextEdit。
        """
        try:
            # 设置字体大小
            font = self.textEdit.font()
            font.setPointSize(font_size)
            self.textEdit.setFont(font)

            # 获取列标题
            first_row = next(iter(result.values()))
            if not isinstance(first_row, dict):
                raise ValueError("result 的值必须是字典类型。")
            
            headers = list(first_row.keys())  # 提取列标题
            headers = [str(header) for header in headers]  # 确保标题是字符串

            # 对每个字段进行格式化并填充到固定宽度
            table_output = []  # 存储表格内容
            formatted_headers = []
            for header in headers:
                header_str = str(header)  # 确保转换为字符串
                char_count = sum(2 if ord(c) > 127 else 1 for c in header_str)  # 计算当前宽度，判断是否为中文
                padding = column_width - char_count
                if padding > 0:
                    header_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                else:
                    header_str = header_str[:column_width]  # 截断超出的部分
                formatted_headers.append(header_str)

            table_output.append("".join(formatted_headers))  # 添加标题行
            table_output.append("-" * (column_width * len(headers)))  # 分隔线

            # 遍历每一行并格式化
            for row in result.values():
                formatted_row = []
                for header in headers:
                    value_str = str(str(row.get(header, "")).encode('latin').decode('GBK'))  # 确保转换为字符串,12/13增加编解码，解决中文乱码，连接字符集统一为为utf8
                    char_count = sum(2 if ord(c) > 127 else 1 for c in value_str)  # 计算当前宽度
                    padding = column_width - char_count
                    if padding > 0:
                        value_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                    else:
                        value_str = value_str[:column_width]  # 截断超出的部分
                    formatted_row.append(value_str)
                table_output.append("".join(formatted_row))

            # 显示格式化的表格内容
            self.textEdit.clear()
            self.textEdit.append("\n".join(table_output))

        except Exception as e:
            self.textEdit.append(f"错误: {str(e)}")

    
class DeletePage(Widget):
    def __init__(self, parent=None):
        super().__init__('删除', parent)
        self.db1, self.cursor1,self.db2,self.cursor2, self.tables = init_sql("sa","20040323Ww") # 使用已有的数据库初始化函数
        self.initUI()

    def initUI(self):
        """初始化UI组件"""
        # 设置 ComboBox 用于选择表名
        self.tableInput = ComboBox(self)
        self.tableInput.setPlaceholderText("选择一个表")
        self.tableInput.addItems([table[0] for table in self.tables])  # 添加表名
        self.tableInput.setFixedSize(300, 40)
        self.tableInput.setCurrentIndex(-1)
        self.tableInput.currentIndexChanged.connect(self.changehoderText)
        # 删除条件输入框
        self.conditionInput = LineEdit(self)
        self.conditionInput.setPlaceholderText("请输入查询条件")
        self.stands = [
    "class_id",
    "class_name",
    "department",
    "student_id",
    "student_name",
    "grade",
    "student_relation_id",
    "student_relation_name",
    "1=1"
]
        completer = QCompleter(self.stands, self.conditionInput)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setMaxVisibleItems(10)
        self.conditionInput.setCompleter(completer)
        self.conditionInput.setFixedSize(300, 40)


        # 查询按钮
        self.DeleteButton = PushButton('删除', self)
        self.DeleteButton.setFixedSize(200, 40)
        self.DeleteButton.clicked.connect(self.perform_delete)

        # 设置 textEdit 用于展示查询结果
        self.textEdit= TextEdit(self)

        # 布局设置
        layout = QVBoxLayout(self)
        layout.addWidget(self.tableInput)
        layout.addWidget(self.conditionInput)
        layout.addWidget(self.DeleteButton)
        layout.addWidget(self.textEdit)

    def perform_delete(self):
        """执行查询操作"""
        table = self.tableInput.currentText()  
        condition = self.conditionInput.text()  # 获取查询条件
        if delete(table,self.cursor2,self.db2,condition)==1:
            self.show_success()
            self.perform_query()
        
    def changehoderText(self):
        table = self.tableInput.currentText()  # 获取用户选择的表名
        if table=="t_department":
            self.conditionInput.setPlaceholderText("请输入院系编号，院系名称")
        if table=="t_classinfo":
            self.conditionInput.setPlaceholderText("请输入课程名称，课程编号")
        if table=="t_grade":
            self.conditionInput.setPlaceholderText("请输入成绩，课程名称，课程编号，学生学号")
        if table=="t_student_info":
            self.conditionInput.setPlaceholderText("请输入学生学号，学生姓名")
        if table=="t_studentrelation":
            self.conditionInput.setPlaceholderText("请输入院系编号，学生学号")
    def show_success(self):
        TeachingTip.create(
            target=self.DeleteButton,
            icon="Success",
            title='删除提示',
            content="删除成功！",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    def perform_query(self):
        """执行查询操作"""
        table = self.tableInput.currentText()  # 获取用户选择的表名
        condition = '1=1'  # 获取查询条件
        if table and condition:
            result=query(table,self.cursor2,self.db2,condition)
            if table=="t_grade":
                self.display_result(result,15,20)
            else:
                self.display_result(result,25,25)
    def display_result(self, result, column_width=15, font_size=12):
        """
        显示表格数据，支持中英文混排对齐。

        Args:
            result (dict): 输入数据，格式为字典，键为行号，值为字典，每行的数据。
            column_width (int): 每列的宽度（单位：字符数，中文占 2，英文占 1）。
            font_size (int): 设置字体大小，用于 QTextEdit。
        """
        try:
            # 设置字体大小
            font = self.textEdit.font()
            font.setPointSize(font_size)
            self.textEdit.setFont(font)

            # 获取列标题
            first_row = next(iter(result.values()))
            if not isinstance(first_row, dict):
                raise ValueError("result 的值必须是字典类型。")
            
            headers = list(first_row.keys())  # 提取列标题
            headers = [str(header) for header in headers]  # 确保标题是字符串

            # 对每个字段进行格式化并填充到固定宽度
            table_output = []  # 存储表格内容
            formatted_headers = []
            for header in headers:
                header_str = str(header)  # 确保转换为字符串
                char_count = sum(2 if ord(c) > 127 else 1 for c in header_str)  # 计算当前宽度，判断是否为中文
                padding = column_width - char_count
                if padding > 0:
                    header_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                else:
                    header_str = header_str[:column_width]  # 截断超出的部分
                formatted_headers.append(header_str)

            table_output.append("".join(formatted_headers))  # 添加标题行
            table_output.append("-" * (column_width * len(headers)))  # 分隔线

            # 遍历每一行并格式化
            for row in result.values():
                formatted_row = []
                for header in headers:
                    value_str = str(str(row.get(header, "")).encode('latin').decode('GBK'))  # 确保转换为字符串,12/13增加编解码，解决中文乱码，连接字符集统一为为utf8
                    char_count = sum(2 if ord(c) > 127 else 1 for c in value_str)  # 计算当前宽度
                    padding = column_width - char_count
                    if padding > 0:
                        value_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                    else:
                        value_str = value_str[:column_width]  # 截断超出的部分
                    formatted_row.append(value_str)
                table_output.append("".join(formatted_row))

            # 显示格式化的表格内容
            self.textEdit.clear()
            self.textEdit.append("\n".join(table_output))

        except Exception as e:
            self.textEdit.append(f"错误: {str(e)}")
    
class OthertherPage(Widget):
    def __init__(self, parent=None):
        super().__init__('特殊功能', parent)
        self.db1, self.cursor1,self.db2,self.cursor2, self.tables = init_sql("sa","20040323Ww") # 使用已有的数据库初始化函数
        self.initUI()

    def initUI(self):
        """初始化UI组件"""
        # 设置 ComboBox 用于选择表名
        self.tableInput = ComboBox(self)
        self.tableInput.setPlaceholderText("选择一个功能")
        self.tableInput.addItems(['统计人数','统计成绩','平均成绩'])  # 添加表名
        self.tableInput.setFixedSize(300, 40)
        self.tableInput.setCurrentIndex(-1)
        self.tableInput.currentIndexChanged.connect(self.changehoderText)
        # 条件输入框
        self.conditionInput = LineEdit(self)
        self.conditionInput.setPlaceholderText("请输入课程名")
        self.conditionInput.setFixedSize(300, 40)


        # 执行按钮
        self.goButton = PushButton('执行', self)
        self.goButton.setFixedSize(200, 40)
        self.goButton.clicked.connect(self.go)
    

        # 设置 textEdit 用于展示查询结果
        self.textEdit= TextEdit(self)

        # 布局设置
        layout = QVBoxLayout(self)
        layout.addWidget(self.tableInput)
        layout.addWidget(self.conditionInput)
        layout.addWidget(self.goButton)
        layout.addWidget(self.textEdit)

    def perform_go(self):
        """执行查询操作"""
        table = self.tableInput.currentText()  
        

        
    def changehoderText(self):
        table = self.tableInput.currentText()  # 获取用户选择的表名
        if table=="统计人数":
            self.conditionInput.setPlaceholderText("请输入院系名称")
        if table=="统计成绩":
            self.conditionInput.setPlaceholderText("请输入课程名称")
        if table=="平均成绩":
            self.conditionInput.setPlaceholderText("不用输入，请直接执行")
    def show_success(self):
        TeachingTip.create(
            target=self.goButton,
            icon="Success",
            title='操作提示',
            content="操作成功！",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    def show_success_countstudent(self,count,condition):
            TeachingTip.create(
                target=self.goButton,
                icon="Success",
                title='操作提示',
                content="院系%s人数为%s！"%(condition,count),
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=20000,
                parent=self
            )
    def go(self):
        table = self.tableInput.currentText()  # 获取用户选择的表名
        self.condition=self.conditionInput.text()
        if table=="统计人数":
            self.count=self.count_student(self.condition)
            if self.count!=-1:
                self.show_success_countstudent(self.count,self.condition)
        if table=="统计成绩":
            self.grade_query()
        if table=="平均成绩":
            self.avg_query()
    def count_student(self,condition):
        department = self.condition
        if department:
            try:
                department_id = self.get_department_id(department)
                sql='SELECT COUNT(DISTINCT student_id)  FROM t_studentrelation WHERE department_id = %s'%department_id
                self.cursor2.execute(sql)
                result = self.cursor2.fetchone()
                if result:
                    count = result[0]
                    return count
            except Exception as e:
                self.textEdit.append(f"查询失败：{e}")
                return -1
    def avg_query(self):
        sql = """
CREATE VIEW View_DepartmentCourseAverage AS
SELECT 
    d.department_name as'院系', 
    ci.class_name as'课程', 
    AVG(g.class_grade) AS '平均成绩'
FROM 
    t_department d
JOIN 
    t_studentrelation sr ON d.department_id = sr.department_id
JOIN 
    t_student_info si ON sr.student_id = si.student_id
JOIN 
    t_grade g ON si.student_id = g.student_id
JOIN 
    t_classinfo ci ON g.class_id = ci.class_id
GROUP BY 
    d.department_name, 
    ci.class_name;
"""
        try:
            self.cursor2.execute(sql)
            self.db2.commit()
            result = query("View_DepartmentCourseAverage", self.cursor2, self.db2,"1=1")
            #print(result[0])
            self.display_result(result,15,25)
            drop_view_sql = "DROP VIEW IF EXISTS View_DepartmentCourseAverage;"
            self.cursor2.execute(drop_view_sql)
            self.db2.commit()

        except Exception as e:
            self.textEdit.append(f"查询失败：{e}")
    
            
    def get_department_id(self, department):
        try:
            sql = "SELECT department_id FROM t_department WHERE department_name = '%s'"%department
            self.cursor2.execute(sql)
            result = self.cursor2.fetchone()
            return result[0] if result else None
        except Exception as e:
            self.textEdit.append(f"查询失败：{e}")
    def grade_query(self):
        class_name = self.condition
        if class_name:
            try:
                result = query("t_grade", self.cursor2, self.db2,"class_id='%s'"%self.get_class_id(class_name),mode=1)
                #print(result[0])
                result[0]["学号"]=int(result[0]["学号"])
                result[1]["学号"]=int(result[1]["学号"])
                self.display_result(result,25,25)
      
                
            except Exception as e:
                self.textEdit.append(f"查询失败：{e}")
    def get_class_id(self, class_name):
        try:
            sql = "SELECT class_id FROM t_classinfo WHERE class_name = '%s'"%class_name
            self.cursor2.execute(sql)
            result = self.cursor2.fetchone()
            return result[0] if result else None
        except Exception as e:
            self.textEdit.append(f"查询失败：{e}")

    def display_result(self, result, column_width=15, font_size=12):
        """
        显示表格数据，支持中英文混排对齐。

        Args:
            result (dict): 输入数据，格式为字典，键为行号，值为字典，每行的数据。
            column_width (int): 每列的宽度（单位：字符数，中文占 2，英文占 1）。
            font_size (int): 设置字体大小，用于 QTextEdit。
        """
        try:
            # 设置字体大小
            font = self.textEdit.font()
            font.setPointSize(font_size)
            self.textEdit.setFont(font)

            # 获取列标题
            first_row = next(iter(result.values()))
            if not isinstance(first_row, dict):
                raise ValueError("result 的值必须是字典类型。")
            
            headers = list(first_row.keys())  # 提取列标题
            headers = [str(header) for header in headers]  # 确保标题是字符串

            # 对每个字段进行格式化并填充到固定宽度
            table_output = []  # 存储表格内容
            formatted_headers = []
            for header in headers:
                header_str = str(header)  # 确保转换为字符串
                char_count = sum(2 if ord(c) > 127 else 1 for c in header_str)  # 计算当前宽度
                padding = column_width - char_count
                if padding > 0:
                    header_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                else:
                    header_str = header_str[:column_width]  # 截断超出的部分
                formatted_headers.append(header_str)

            table_output.append("".join(formatted_headers))  # 添加标题行
            table_output.append("-" * (column_width * len(headers)))  # 分隔线

            # 遍历每一行并格式化
            for row in result.values():
                formatted_row = []
                for header in headers:
                    value_str = str(str(row.get(header, "")).encode('latin').decode('GBK'))  # 确保转换为字符串,12/13增加编解码，解决中文乱码，连接字符集统一为为utf8
                    char_count = sum(2 if ord(c) > 127 else 1 for c in value_str)  # 计算当前宽度
                    padding = column_width - char_count
                    if padding > 0:
                        value_str += chr(12288) * (padding // 2) + " " * (padding % 2)
                    else:
                        value_str = value_str[:column_width]  # 截断超出的部分
                    formatted_row.append(value_str)
                table_output.append("".join(formatted_row))

            # 显示格式化的表格内容
            self.textEdit.clear()
            self.textEdit.append("\n".join(table_output))

        except Exception as e:
            self.textEdit.append(f"错误: {str(e)}")

#登录界面********************************
class login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        

    def initUI(self):
        self.setWindowTitle('登录')
        self.setWindowIcon(QIcon("image.png"))
        self.setGeometry(100, 100, 900, 558)
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QGridLayout()
        palette = QPalette()

        palette.setBrush(QPalette.Background, QBrush(QPixmap("image copy.png")))  

        self.setPalette(palette)
        self.label = QLabel('学生管理系统:', self)
     
        self.username = LineEdit()
        self.username.setFixedSize(400, 60)
        self.username.setPlaceholderText('请输入用户名')
        self.password = LineEdit()
        self.password.setFixedSize(400, 60)
        self.password.setPlaceholderText('请输入密码')
        self.password.setEchoMode(QLineEdit.Password)
        self.button = PushButton('登录', self)
        self.button.setFixedSize(400, 60)
        self.button.clicked.connect(self.log_input)
        layout.addWidget(self.label, 0, 1, 1, 2, Qt.AlignCenter)
        layout.addWidget(self.username, 1, 1, 1, 2, Qt.AlignCenter)
        layout.addWidget(self.password, 2, 1, 1, 2, Qt.AlignCenter)
        layout.addWidget(self.button, 3, 1, 1, 2, Qt.AlignCenter)
        
        centralWidget.setLayout(layout)
    def log_input(self):
        username = self.username.text()
        password = self.password.text()
        if username == 'sa' and password == '20040323Ww' or username == 'donguki' and password == '20040323'or username == 'reader' and password == '20040323':
            self.close()
            self.ex2=Window(username,password)
            self.ex2.show()
        else:
            TeachingTip.create(
            target=self.button,
            icon="Success",
            title='登录失败',
            content="密码错误！",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
if __name__ == '__main__':
    

    app = QApplication(sys.argv)
    w = login()
    w.show()
    app.exec_()