from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction, QColor
from PyQt6.QtCore import Qt, QTimer
import sys
import os
import datetime
import requests
from bs4 import BeautifulSoup


curPath = os.path.dirname(os.path.realpath(__file__))


class PrayerTimeMain():

    def __init__(self):
        super().__init__()

    def filterNextPrayers(self, pi):
        tmpPrayerHour = int(pi.prayerTime.split(':')[0])
        tmpPrayerMinute = int(pi.prayerTime.split(':')[1])
        if datetime.datetime.now().hour < tmpPrayerHour or (datetime.datetime.now().hour == tmpPrayerHour and datetime.datetime.now().minute <= tmpPrayerMinute):
            return True
        return False

    def setCurTime(self):
        curTime = str.format(
            "{0}", datetime.datetime.now().strftime("%d-%h-%Y %I:%M:%S %p"))
        childLst = self.w.children()
        for x in childLst:
            if(type(x) == QLabel and x.objectName() == 'curTime'):
                x.setText(curTime)
        if(self.collectPrayerTime()):
            i = 0
            for prayerInfo in self.prayerList:
                prayerName = QTableWidgetItem(prayerInfo.prayerName)
                prayerName.setFont(QFont("verdana",11,900,False))
                prayerName.setForeground(QColor("#ffffff"))
                prayerName.setBackground(QColor("#575757"))
                prayerName.setFlags(Qt.ItemFlag.ItemIsEnabled)
                prayerName.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                prayerTime = QTableWidgetItem(prayerInfo.prayerTimeDisp)
                prayerTime.setFont(QFont("verdana",11,900,False))
                prayerTime.setFlags(Qt.ItemFlag.ItemIsEnabled)
                prayerTime.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.prayerTable.setItem(i, 0, prayerName)
                self.prayerTable.setItem(i, 1, prayerTime)
                i += 1
        filterList = list(filter(self.filterNextPrayers, self.prayerList))
        if(len(filterList) > 0):
            nextPrayer = min(filterList, key=lambda pi: int(
                pi.prayerTime.split(':')[0]))
            nextPrayerIdx = self.prayerList.index(nextPrayer)
            if nextPrayerIdx > 0:
                self.prayerTable.item(
                    nextPrayerIdx-1, 0).setForeground(QColor("#ffffff"))
                self.prayerTable.item(
                    nextPrayerIdx-1, 0).setBackground(QColor("#575757"))
                self.prayerTable.item(
                    nextPrayerIdx-1, 1).setBackground(QColor("#ffffff"))
            self.prayerTable.item(
                nextPrayerIdx, 0).setForeground(QColor("#000000"))
            self.prayerTable.item(
                nextPrayerIdx, 0).setBackground(QColor("#ffff33"))
            self.prayerTable.item(
                nextPrayerIdx, 1).setBackground(QColor("#ffff33"))

    def changeWindowTitle(self):  
        if(self.wcMovable.isChecked()):
            self.w.move()
        self.w.show()


    def startApp(self):
        app = QApplication(sys.argv)
        app.setApplicationDisplayName('UAE Prayer Time')
        app.setWindowIcon(QIcon(QPixmap(curPath+'\images\pt-icon.png')))

        self.w = QWidget()
        #self.w.setMouseTracking(True)
        #self.w.mouseMoveEvent()
        #self.w.removeAction(QAction('close'))
        self.w.resize(300, 210)
        self.w.move(300, 300)

        self.w.setWindowFlag(Qt.WindowType.CoverWindow)
        self.w.setWindowIcon(QIcon(QPixmap(curPath+'\images\pt-icon.png')))
        self.w.setStyleSheet("background-color:#ffffff")

        layout = QVBoxLayout()
        self.w.setLayout(layout)
        layout.setSpacing(15)
        hLayout = QHBoxLayout()
        layout.addLayout(hLayout)
        hLayout.setSpacing(15)

        wcLabel = QLabel("")
        wcLabel.setObjectName("curTime")
        wcLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        wcLabel.setFont(QFont('verdana', 12, 900, False))
        hLayout.addWidget(wcLabel)

        #self.wcMovable = QCheckBox("")
        #self.wcMovable.stateChanged.connect(self.changeWindowTitle)
        #hLayout.addWidget(self.wcMovable)

        self.prayerTable = QTableWidget()
        self.prayerTable.verticalHeader().setVisible(False)
        self.prayerTable.horizontalHeader().setVisible(False)
        self.prayerTable.setRowCount(5)
        self.prayerTable.setColumnCount(2)
        colWidth = self.w.size().width()
        colWidth = colWidth//2
        self.prayerTable.setColumnWidth(0, colWidth-13)
        self.prayerTable.setColumnWidth(1, colWidth-13)
        layout.addWidget(self.prayerTable)

        self.prayerTimeCollectedOn = datetime.datetime.min
        self.w.show()
        timer = QTimer()
        timer.timeout.connect(self.setCurTime)
        timer.start(1000)

        sys.exit(app.exec())

    class PrayerInfo():
        def __init__(self, prayerName, prayerTime):
            super().__init__()
            self.prayerName = prayerName
            self.prayerTime = prayerTime
            tmpPrayerHour = int(self.prayerTime.split(':')[0])
            tmpPrayerMinute = int(self.prayerTime.split(':')[1])
            tmpAmPm = "AM"
            if tmpPrayerHour >= 12:
                tmpAmPm = "PM"
                tmpPrayerHour = 12 if tmpPrayerHour == 12 else tmpPrayerHour-12
            hourZero = "0" if tmpPrayerHour<10 else ""
            MinuteZero = "0" if tmpPrayerMinute<10 else ""
            self.prayerTimeDisp = str.format("{3}{0}:{4}{1} {2}",tmpPrayerHour,tmpPrayerMinute,tmpAmPm,hourZero,MinuteZero)

    def collectPrayerTime(self):
        if (self.prayerTimeCollectedOn != None and self.prayerTimeCollectedOn.strftime("%d%h%Y") == datetime.datetime.now().strftime("%d%h%Y")):
            return False

        self.prayerTimeCollectedOn = datetime.datetime.now()
        soup = BeautifulSoup(requests.get(
            "https://www.khaleejtimes.com/prayer-time-uae").content, "html.parser")
        self.prayerList = []
        self.prayerList.append(self.PrayerInfo(
            "Fajr", soup.select_one("#nav_pt_calculate_fajr").string))
        self.prayerList.append(self.PrayerInfo(
            "Dhuhr", soup.select_one("#nav_pt_calculate_dhuhr").string))
        self.prayerList.append(self.PrayerInfo(
            "Asr", soup.select_one("#nav_pt_calculate_asr").string))
        self.prayerList.append(self.PrayerInfo(
            "Maghrib", soup.select_one("#nav_pt_calculate_magrib").string))
        self.prayerList.append(self.PrayerInfo(
            "Isha", soup.select_one("#nav_pt_calculate_isha").string))
        return True

    #def mouseMoveEvent(self, event):
    #   if(self.wcMovable.isChecked()):
    #       self.w.move(event.x(), event.y())

if __name__ =='__main__':
    # intializing the App Main window
    PrayerTimeMain().startApp()
