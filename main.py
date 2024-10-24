from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout ,QWidget, QGridLayout, QLineEdit,\
     QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox , QToolBar , QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sqlite3 as sql
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        self.setMinimumSize(600, 400)

        file_menu_item = self.menuBar().addMenu('&File')
        help_menu_item = self.menuBar().addMenu('&Help')
        edit_menu_item = self.menuBar().addMenu('&Edit')

        # File --> Add Student Action 
        add_student_action = QAction(QIcon("icons/add.png"),"Add Student",self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Help --> About Action 
        about_action = QAction('About',self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # Edit --> Search Action 
        search_action = QAction(QIcon("icons/search.png"),'Search',self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(('ID','Name','Course','Mobile'))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = sql.connect('database.db')
        result = connection.execute("Select * from students")
        self.table.setRowCount(0)
        for row_num , row_data in enumerate(result):
            self.table.insertRow(row_num)
            for column_num , data in enumerate(row_data):
                self.table.setItem(row_num, column_num, QTableWidgetItem(str(data)))
        connection.close
        
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()    
    
    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self): 
        dialog = EditDialog()
        dialog.exec()

    def delete(self): 
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
This App is created for my Learning. For changes please clone the git repo"""
        self.setText(content)

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get Student Name from Selected Row
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        # Get ID from selected row
        self.student_id = main_window.table.item(index,0).text()

        # Add Student Name
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        course_name = main_window.table.item(index,2).text()
        self.student_course = QComboBox()
        courses = ['Biology','Math','Astronomy','Physics']
        self.student_course.addItems(courses)
        self.student_course.setCurrentText(course_name)
        layout.addWidget(self.student_course)

        # Add mobile
        mobile = main_window.table.item(index,3).text()
        self.student_mobile = QLineEdit(mobile)
        self.student_mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.student_mobile)

        # Add Submit
        submit_button = QPushButton("Update")
        submit_button.clicked.connect(self.update_student)
        layout.addWidget(submit_button)
        
        self.setLayout(layout)

    def update_student(self):
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("update students set name = ?, course = ?, mobile = ? where id = ?",
                      (self.student_name.text(), 
                       self.student_course.itemText(self.student_course.currentIndex()),
                       self.student_mobile.text(),
                       self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        main_window.load_data()

        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

    
        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")
        layout.addWidget(confirmation, 0,0,1,2)
        layout.addWidget(yes, 1,0)
        layout.addWidget(no, 1,1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
    
    def delete_student(self):
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index,0).text()

        connection = sql.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("delete from students where id = ?",(student_id, ))
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_data()

        self.close()

        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Success")
        confirmation_message.setText("Deleted Record Sucessfully!!!!!!!")
        confirmation_message.exec()

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add Name Field
        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")
        layout.addWidget(self.name)

        # Add Search Button
        button = QPushButton("Search")
        button.clicked.connect(self.search_student)
        layout.addWidget(button)

        self.setLayout(layout)
    
    def search_student(self):
        name = self.name.text()
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        result = cursor.execute("select * from students where name = ?",
                       (name,))
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(name,Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(),1).setSelected(True)

        cursor.close()
        connection.close()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add Student Name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.student_course = QComboBox()
        courses = ['Biology','Math','Astronomy','Physics']
        self.student_course.addItems(courses)
        layout.addWidget(self.student_course)

        # Add mobile
        self.student_mobile = QLineEdit()
        self.student_mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.student_mobile)

        # Add Submit
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.add_student)
        layout.addWidget(submit_button)
        
        self.setLayout(layout)
    
    def add_student(self):
        name   = self.student_name.text()
        course = self.student_course.itemText(self.student_course.currentIndex())
        mobile = self.student_mobile.text()
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("insert into students (name, course, mobile) values (?,?,?)",
                       (name,course,mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())