import random
import sys
import os

from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QImage,
    QPainter,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QRadioButton,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


NUM_COLORS = {
    1: QColor("#f44336"),
    2: QColor("#9C27B0"),
    3: QColor("#3F51B5"),
    4: QColor("#03A9F4"),
    5: QColor("#00BCD4"),
    6: QColor("#4CAF50"),
    7: QColor("#E91E63"),
    8: QColor("#FF9800"),
}








class Pos(QWidget):

    clicked_left = pyqtSignal(int, int)
    clicked_right = pyqtSignal(object)

    def __init__(self, x, y):
        super().__init__()

        self.setMinimumSize(QSize(30, 30))
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_discovered = False
        self.surrounding_mines = 0
        self.to_expand = True
        self.set_flag = False
        self.field_color = QColor("lightgray")
        self.pen_color = QColor("gray")
        self.img = QPixmap("")
        self.text_color = QColor("gray")
        self.text = " "

    def paintEvent(self, event):
        p = QPainter(self)
        r = event.rect()

        brush = QBrush()
        brush.setColor(self.field_color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        p.fillRect(r, brush)

        p.drawPixmap(r, self.img)

        pen = QPen()
        pen.setColor(self.pen_color)
        p.setPen(pen)
        pen.setWidth(8)
        p.drawRect(r)

        text = QPen()
        text.setColor(self.text_color)
        p.setPen(text)

        f = p.font()
        f.setPointSize(16)
        f.setBold(True)
        p.setFont(f)
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, self.text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.clicked_right.emit(self)

        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_left.emit(self.x, self.y)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bug-Search")
        self.to_discover = []
        self.flag_list = []
        self.level_text = "small"
        self.clicked_count = 0
        self.b_size = 8
        self.n_mines = 10

        self.wg = QWidget()

        button1 = QPushButton("reset")
        button1.clicked.connect(self.game_reset)
        grid_radio = QGridLayout()
        self.IMG_BOMB = QImage(self.resource_path("bug.png"))
        self.IMG_FLAG = QImage(self.resource_path("flag.png"))
        self.IMG_TROPHY = QImage(self.resource_path("trophy.png"))
        self.ICON_BUG = self.resource_path("bug.png")


        self.setWindowIcon(QIcon(self.ICON_BUG))

        radiobutton = QRadioButton("S")
        radiobutton.setChecked(True)
        radiobutton.item = ("small", 8, 10)
        radiobutton.toggled.connect(self.rb_changed)
        grid_radio.addWidget(radiobutton, 0, 0)

        radiobutton = QRadioButton("M")
        radiobutton.item = ("medium", 14, 24)
        radiobutton.toggled.connect(self.rb_changed)
        grid_radio.addWidget(radiobutton, 0, 1)

        radiobutton = QRadioButton("L")
        radiobutton.item = ("large", 20, 44)
        radiobutton.toggled.connect(self.rb_changed)
        grid_radio.addWidget(radiobutton, 0, 2)

        radiobutton = QRadioButton("XL")
        radiobutton.item = ("X-large", 28, 99)
        radiobutton.toggled.connect(self.rb_changed)
        grid_radio.addWidget(radiobutton, 0, 3)

        self.label_level_name = QLabel()
        self.label_level_name.setStyleSheet("color:black; font-size:12pt")
        self.label_level_name.setText(self.level_text)
        self.label_level_name.setFixedHeight(20)
        self.label_level_name.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        label_bug = QLabel()
        label_bug.setStyleSheet("color:red")
        label_bug.setPixmap(QPixmap(self.IMG_BOMB))
        label_bug.setFixedHeight(20)

        self.label_bug_count = QLabel()
        self.label_bug_count.setStyleSheet("color:black; font-size:12pt")
        self.label_bug_count.setText(str(self.n_mines))
        self.label_bug_count.setFixedHeight(20)

        self.label_status = QLabel()
        self.label_status.setStyleSheet("color:red; font-size:12pt; font-weight: bold")
        self.label_status.setText("")
        self.label_status.setFixedHeight(20)

        label_counter = QLabel()
        label_counter.setStyleSheet("color:black; font-size:12pt")
        label_counter.setText("counter")
        label_counter.setFixedHeight(20)
        label_counter.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.label_counter_text = QLabel()
        self.label_counter_text.setStyleSheet("color:black; font-size:12pt")
        self.label_counter_text.setText(str(self.clicked_count))
        self.label_counter_text.setFixedHeight(20)

        hbox = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox = QVBoxLayout()

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        hbox.addWidget(button1)
        hbox.addLayout(grid_radio)

        hbox2.addWidget(self.label_level_name)
        hbox2.addStretch(1)
        hbox2.addWidget(label_bug)
        hbox2.addWidget(self.label_bug_count)
        hbox2.addStretch(1)
        hbox2.addWidget(self.label_status)
        hbox2.addStretch(1)
        hbox2.addWidget(label_counter)
        hbox2.addWidget(self.label_counter_text)
        hbox2.addStretch(1)

        vbox.addLayout(hbox)
        vbox.addLayout(self.grid)
        vbox.addLayout(hbox2)

        self.wg.setLayout(vbox)
        self.setCentralWidget(self.wg)

        self.create_playfield()

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    

    def rb_changed(self):

        radioButton = self.sender()

        if radioButton.isChecked():
            self.reset_playfield()
            self.level_name, self.b_size, self.n_mines = radioButton.item
            self.clicked_count = 0
            self.label_counter_text.setText(str(self.clicked_count))
            self.label_bug_count.setText(str(self.n_mines))
            self.label_level_name.setText(self.level_name)
            self.label_status.setText("")
            self.create_playfield()

    def create_playfield(self):
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                self.w = Pos(x, y)
                self.w.clicked_left.connect(self.left_clicked)
                self.w.clicked_right.connect(self.right_clicked)
                self.grid.addWidget(self.w, y, x)

        QTimer.singleShot(0, lambda: self.resize(1, 1))
        self.create_mine_positions()

    def game_reset(self):
        self.clicked_count = 0
        self.flag_list = []
        self.label_counter_text.setText(str(self.clicked_count))
        self.label_status.setText("")
        self.reset_playfield()
        self.create_playfield()
        self.label_status.setText("")

    def reset_playfield(self):

        for xi in range(self.b_size):
            for yi in range(self.b_size):
                r = self.grid.itemAtPosition(yi, xi).widget()
                r.close()
                self.grid.removeWidget(r)

    def create_mine_positions(self):

        self.m_pos_list = []

        while len(self.m_pos_list) < self.n_mines:

            pos_x = random.randint(0, self.b_size - 1)
            pos_y = random.randint(0, self.b_size - 1)
       

            pos_mine = (pos_x, pos_y)

            if pos_mine not in self.m_pos_list:
                self.m_pos_list.append((pos_x, pos_y))

                w = self.grid.itemAtPosition(pos_y, pos_x).widget()
                w.is_mine = True
  
     

    def left_clicked(self, x, y):
    
        self.clicked_count += 1
        self.label_counter_text.setText(str(self.clicked_count))
        f = self.grid.itemAtPosition(y, x).widget()
        if f.set_flag == False:
            self.discover_pos(x, y)

    def discover_pos(self, x, y):

        f = self.grid.itemAtPosition(y, x).widget()
        f.field_color = QColor("transparent")
        f.pen_color = QColor("transparent")
        f.update()

        if f.is_mine == True:
            self.label_status.setText("NO LUCK")
            self.flag_list = []
            undisc_lst = self.create_undiscovered_list()

            for w in undisc_lst:
                if w.set_flag == True:

                    w.set_flag = False
                for m in self.m_pos_list:
                    self.discover_positions(w)
                    x, y = m[0], m[1]
                    w = self.grid.itemAtPosition(y, x).widget()
                    w.img = QPixmap(self.IMG_BOMB)
                w.update()

        else:
            self.discover_surrounding(x, y)

    def create_undiscovered_list(self):
        undiscovered_list = []
        for xi in range(self.b_size):
            for yi in range(self.b_size):
                w = self.grid.itemAtPosition(yi, xi).widget()
                if w.is_discovered == False:
                    undiscovered_list.append(w)
        return undiscovered_list

    def discover_surrounding(self, x, y):
        to_expand = True

        w = self.grid.itemAtPosition(y, x).widget()
        w.is_discovered = False
        position_list = [w]

        n = 0
        list_to_expand = []

        while to_expand:
        
            
            l = position_list
            position_list = []
            

            for w in l:

                n += 1
                x, y = w.x, w.y
                positions = self.get_surrounding_positions(x, y)
                n_mines = self.count_surrounding_mines(positions)
                w.surrounding_mines = n_mines
      

                if n_mines == 0 and w.is_discovered == False:
                    surrounding_positions = self.get_surrounding_positions(x, y)
                    n_mines = self.count_surrounding_mines(surrounding_positions)
                    w.surrounding_mines = n_mines
                    position_list.append(w)
                  
                    list_to_expand.append(w)
                    w.is_discovered = True

                    position_list.extend(surrounding_positions)
               
                    to_expand = True

                elif n_mines != 0 and w.is_discovered == False:
                    position_list.append(w)
                    list_to_expand.append(w)
                    w.is_discovered = True
                    to_expand = False
                
                else:
                
                    to_expand = False
              
                    w.is_discovered = True
                
        for w in list_to_expand:
            self.discover_positions(w)

    def discover_positions(self, w):
        if w.set_flag == False:
            w.field_color = QColor("transparent")
            w.pen_color = QColor("transparent")
            if w.surrounding_mines > 0:
                w.text_color = QColor(NUM_COLORS[w.surrounding_mines])
                w.text = str(w.surrounding_mines)

            w.update()

    def count_surrounding_mines(self, positions):
        mines_count = 0
        for w in positions:
            if w.is_mine == True:
                mines_count += 1
        return mines_count

    def right_clicked(self, w):
        self.clicked_count += 1
        self.label_counter_text.setText(str(self.clicked_count))
        if w.is_discovered == False:
            w.set_flag = not w.set_flag
            pos = w.x, w.y
            if w.set_flag:
                w.img = QPixmap(self.IMG_FLAG)

                self.flag_list.append(pos)
            else:
                w.img = QPixmap(" ")
                self.flag_list.remove(pos)
            w.update()


            if sorted(self.flag_list) == sorted(self.m_pos_list):
                self.label_status.setText("YOU WON !")

                for pos in self.flag_list:
                    x, y = pos[0], pos[1]
                    w = self.grid.itemAtPosition(y, x).widget()
                    w.img = QPixmap(self.IMG_TROPHY)
                    w.update()

    def get_surrounding_positions(self, x, y):
        positions = []

        for xi in range(max(0, x - 1), min(x + 2, self.b_size)):
            for yi in range(max(0, y - 1), min(y + 2, self.b_size)):
                if not (xi == x and yi == y):
                    positions.append(self.grid.itemAtPosition(yi, xi).widget())

        return positions


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
