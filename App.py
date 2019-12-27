from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys
import Main
import arrow
import pprint
from functools import partial
import threading
from configparser import ConfigParser

isLoading = True
task_box = []
input_box = []
output_box = []
finish_box = []
schedule_table = {}


class MessageWidget(QWebEngineView):
    '''消息框部件

    显示用户们的消息的地方 维护本地消息序列
    '''
    def __init__(self, father):
        super().__init__(father)

        with open('./Css/MsgWidget.html', 'r') as f:
            self.html_head = f.read()
        self.html_tail = '</body></html>'

        self.LBubble_head = ''' <div class="LBubble-container">
                                    <div class="LBubble">
                                        <p>
                                            <span class="msg">'''
        self.LBubble_tail = '''             </span>
                                            <span class="bottomLevel left"></span>
                                            <span class="topLevel"></span>
                                        </p>
                                        <br>
                                    </div>
                                </div>'''
        self.RBubble_head = ''' <div class="RBubble-container">
                                    <div class="RBubble">
                                        <p>
                                            <span class="msg">'''
        self.RBubble_tail = '''             </span>
                                            <span class="bottomLevel right"></span>
                                            <span class="topLevel"></span>
                                        </p>
                                        <br>
                                    </div>
                                </div>'''
        self.init_UI()
        
    def init_UI(self):
        self.__refresh()

    def addMine(self, msg):
        self.html_head += self.RBubble_head + msg + self.RBubble_tail
        self.__refresh()


    def addOthers(self, msg):
        name_html = '''<strong style="font-family:cursive">Server: </strong>'''
        self.html_head += self.LBubble_head + name_html + msg + self.LBubble_tail
        self.__refresh()


    def __refresh(self):
        self.setHtml(self.html_head + self.html_tail)




class InputWidget(QWidget):
    '''输入部件

    用户输入消息的地方
    '''
    def __init__(self, parent):
        super().__init__(parent)
        self.init_UI()
        
    def init_UI(self):
        self.submitButton = QPushButton()
        self.submitButton.setStyleSheet( "QPushButton{width:25px; height:25px; border-image: url(./Css/ok.ico)}"
                                    "QPushButton:hover{border-image: url(./Css/ok_h.ico)}"
                                    "QPushButton:pressed{border-image: url(./Css/ok_h.ico)}")
        self.inputLine = QLineEdit()

        self.submitButton.clicked.connect(self.submit)
        self.inputLine.returnPressed.connect(self.submit)

        hbox = QHBoxLayout()
        hbox.addWidget(self.inputLine)
        hbox.addSpacing(10)
        hbox.addWidget(self.submitButton)

        self.setLayout(hbox) 

    def submit(self):
        if self.inputLine.text() == '':
            return
        global task_box
        task_box.append(self.inputLine.text())
        self.inputLine.clear()


class TaskWidget(QWidget):
    '''任务列表
    '''
    def __init__(self, parent):
        super().__init__(parent)
        # 设置背景颜色
        self.setPalette(QPalette(QColor('#404040'))) # 着色，区分背景
        self.setAutoFillBackground(True) # 自动填充背景
        self.setMinimumSize(100,100) # 这一句是辅助
        self.init_UI()

    def init_UI(self):

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

    def refresh(self, _date):
        global schedule_table

        for i in range(self.vbox.count()):
            self.vbox.itemAt(i).widget().deleteLater()

        if _date not in schedule_table.keys():
            return

        check_box_list = list()
        for task in sorted(schedule_table[_date]):
            x = QCheckBox(task)
            x.setStyleSheet("QCheckBox {color:#f8fdfc;}")
            x.toggled.connect(partial(self.deleteTask, _date, task))
            check_box_list.append(x)


        for box in check_box_list:
            self.vbox.addWidget(box)


    def deleteTask(self, _date, task):
        global schedule_table, finish_box
        if _date in schedule_table.keys() and task in schedule_table[_date]:
            schedule_table[_date].remove(task)
        finish_box.append(task)
        self.refresh(_date)




class MainWidget(QWidget):
    '''主部件

    负责安排各部件的布局
    '''
    def __init__(self, father):
        super().__init__(father)
        self.cal_widget = QCalendarWidget(self)
        self.msg_widget = MessageWidget(self)
        self.input_widget = InputWidget(self)
        self.task_widget = TaskWidget(self)
        self.initUI()


    def initUI(self):
        self.cal_widget.setGridVisible(False)
        self.cal_widget.clicked[QDate].connect(self.flush)
        self.cal_widget.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        txFormat = QTextCharFormat()
        txFormat.setForeground(Qt.black)
        self.cal_widget.setWeekdayTextFormat(Qt.Saturday, txFormat)
        self.cal_widget.setWeekdayTextFormat(Qt.Sunday, txFormat)
        # 布局
        vbox1 = QVBoxLayout()
        vbox1.setSpacing(10)
        vbox1.addWidget(self.cal_widget, stretch=5)
        vbox1.setSpacing(10)
        vbox1.addWidget(self.task_widget, stretch=3)

        vbox2 = QVBoxLayout()
        vbox1.setSpacing(10)
        vbox2.addWidget(self.msg_widget, stretch=9)
        vbox2.addWidget(self.input_widget, stretch=1)

        hbox = QHBoxLayout()
        vbox1.setSpacing(10)
        hbox.addLayout(vbox1, stretch=3)
        vbox1.setSpacing(20)
        hbox.addLayout(vbox2, stretch=3)
        vbox1.setSpacing(10)

        self.setLayout(hbox)
        self.explaining = False
        self.introducing = False

        # 起refresher线程
        self.timer = QTimer()
        self.timer.timeout.connect(self.__refresh)
        self.timer.start(40)



    def flush(self, _date):
        tmp = _date.toString().split(" ", 3)
        M = int(tmp[1][:-1])
        D = int(tmp[2])
        Y = int(tmp[3])
        self.task_widget.refresh("%d/%02d/%02d" % (Y, M, D))
        self.set_color()



    def __refresh(self):
        global task_box, input_box, output_box, isLoading, finish_box
        if isLoading and not self.explaining:
            self.msg_widget.addOthers('模型加载中...请稍后')
            self.explaining = True
        
        if not isLoading and not self.introducing:
            self.msg_widget.addOthers("加载完毕！")
            self.msg_widget.addOthers("你最近要做哪些事呢，用一段话说明，我会为你安排妥当的～")
            self.introducing = True

        if len(task_box) != 0:
            text = task_box[0]
            task_box.pop(0)
            self.msg_widget.addMine(text)
            self.msg_widget.addOthers('正在解析中...')
            input_box.append(text)

        if len(output_box) != 0:
            text = output_box[0]
            output_box.pop(0)
            self.msg_widget.addOthers(text)
            self.set_color()
            self.flush(self.cal_widget.selectedDate())
            self.msg_widget.addOthers('安排上了！')

        if len(finish_box) != 0:
            text = finish_box[0]
            finish_box.pop(0)
            self.msg_widget.addOthers(f'任务 [{text}] 已完成!')


    def set_color(self):
        global schedule_table
        for date in schedule_table.keys():
            tmp = date.split('/', 2)
            Format = QTextCharFormat()
            Date = QDate(int(tmp[0]), int(tmp[1]), int(tmp[2]))
            if len(schedule_table[date]) == 0:
                Format.setForeground(Qt.black)
                Format.setFontUnderline(False)
            else:
                Format.setForeground(Qt.darkCyan)
                Format.setFontUnderline(True)
            self.cal_widget.setDateTextFormat(Date, Format)



class MainWin(QMainWindow):
    '''主界面
    '''
    def __init__(self):
        super().__init__()
        # 初始化主窗口
        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)

        self.initUI()

    def initUI(self):
        # 基本信息
        self.setGeometry(360, 150, 800, 500)
        self.setWindowTitle('TODO Helper')    
        self.setStyleSheet("QMainWindow {background: #4a4a4a;}")
        self.show()



def addToSchedule(date, task):
    if '~' in date:
        tmp = date.split(' ~ ', 1)
        startTime, endTime = tmp[0], tmp[1]
        tmp_start = startTime.split(' ', 1)
        tmp_end = endTime.split(' ', 1)
        date_start, date_end = tmp_start[0], tmp_end[0] # 对于时间段，忽略时间，只考虑日期
        addSegment(date_start, date_end, task)
    else:
        global schedule_table
        tmp = date.split(' ', 1)
        _date= tmp[0]
        _time = tmp[1] if len(tmp) > 1 else None
        if _date not in schedule_table.keys():
            schedule_table[_date] = list()
        if _time is None:
            schedule_table[_date].append(task)
        else:
            schedule_table[_date].append(_time + ' ' + task)



def addSegment(date1, date2, task):
    global schedule_table
    arrow1 = arrow.get(date1, 'YYYY/MM/DD')
    arrow2 = arrow.get(date2, 'YYYY/MM/DD')
    Y, M, D = arrow1.year, arrow1.month, arrow1.day
    while (Y, M, D) <= (arrow2.year, arrow2.month, arrow2.day):
        _date = "%d/%02d/%02d" % (Y, M, D)
        if _date not in schedule_table.keys():
            schedule_table[_date] = list()
        schedule_table[_date].append('[Long]' + ' ' + task)
        arrow1 = arrow1.shift(days=1)
        Y, M, D = arrow1.year, arrow1.month, arrow1.day



def proc(model_path):
    global input_box, output_box, isLoading
    time_ner = Main.TimeNer(model_path)
    isLoading = False
    while True:
        if len(input_box) != 0:
            text = input_box[0]
            input_box.pop(0)
            schedule, doubt = time_ner.get_schedule(text)

            # [for debug]
            print("无法解析的时间:")
            pprint.pprint(doubt)

            output = list()
            for date, task in schedule.items():
                task = '、'.join(task)
                addToSchedule(date, task)
                output.append(f'<span style="color:red;">{date}</span>  <span style="color:blue;">{task}</span>')
            output_box.append('<br>' + '<br>'.join(output))




if __name__ == '__main__':
    cf = ConfigParser()
    cf.read('./config.ini')
    model_path = cf.get('global', 'model_dir')

    app = QApplication(sys.argv)
    TODO_Helper = MainWin()
    calculator = threading.Thread(target=proc, args=(model_path,), daemon=True)
    calculator.start()
    app.exec_()
