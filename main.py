#!/usr/bin/python3
import sys, os, json

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLineEdit, QTabBar, QFrame, QStackedLayout,QShortcut)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *


class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()

class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Browser")
        self.setBaseSize(2400, 1200)
        self.setMinimumSize(1366,768)
        self.setWindowIcon(QIcon("logo.png"))
        self.create_app()


    def create_app(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        """create tabs"""
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.tabCloseRequested.connect(self.close_tab)
        self.tabbar.tabBarClicked.connect(self.switch_tab)
        self.tabbar.setCurrentIndex(0)
        self.tabbar.setDrawBase(False)
        self.tabbar.setLayoutDirection(Qt.LeftToRight)
        self.tabbar.setElideMode(Qt.ElideLeft)

        self.shortcut_new_tab = QShortcut(QKeySequence("Ctrl+t"),self)
        self.shortcut_new_tab.activated.connect(self.add_tab)
        self.shortcut_reload = QShortcut(QKeySequence("Ctrl+r"), self)
        self.shortcut_reload.activated.connect(self.reload)
        """keep track of tabs"""
        self.tabcount = 0
        self.tabs = []

        """create addressbar"""
        self.addressbar = AddressBar()
        self.toolbar = QWidget()
        self.toolbar.setObjectName("tool_bar")
        self.toolbarlayout = QHBoxLayout()
        self.addressbar.returnPressed.connect(self.browse_to)
        self.toolbar.setLayout(self.toolbarlayout)
        self.toolbarlayout.addWidget(self.addressbar)
        """new tab button"""
        self.addtabbutton = QPushButton("+")
        self.addtabbutton.clicked.connect(self.add_tab)

        """set tool bar buttons"""
        self.back_button = QPushButton("<")
        self.back_button.clicked.connect(self.go_back)
        self.forward_button = QPushButton(">")
        self.forward_button.clicked.connect(self.go_forward)
        self.reload_button = QPushButton("R")
        self.reload_button.clicked.connect(self.reload)


        """build tool bar"""
        self.toolbarlayout.addWidget(self.addtabbutton)
        self.toolbarlayout.addWidget(self.reload_button)
        self.toolbarlayout.addWidget(self.back_button)
        self.toolbarlayout.addWidget(self.forward_button)
        """set main view"""
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        """handling layout"""
        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.toolbar)

        self.layout.addWidget(self.container)
        self.setLayout(self.layout)
        self.add_tab()
        self.show()

    def browse_to(self):
        text = self.addressbar.text()
        index = self.tabbar.currentIndex()
        tab = self.tabbar.tabData(index)["object"]
        web_view = self.findChild(QWidget, tab).content

        if "http" not in text:
            if "." not in text:
                url = "http://www.google.co.il/search?q="+text
            else:
                url = "http://" + text
        else:
            url = text

        web_view.load(QUrl.fromUserInput(url))

    def switch_tab(self, i):
         if self.tabbar.tabData(i):
            tab_data = self.tabbar.tabData(i)["object"]
            tab_content = self.findChild(QWidget, tab_data)
            self.container.layout.setCurrentWidget(tab_content)
            new_url = tab_content.content.url().toString()
            self.addressbar.setText(new_url)

    def close_tab(self,i):
        self.tabbar.removeTab(i)

    def add_tab(self):
        i = self.tabcount

        """set tabs<#> =QWidget"""
        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)


        """for tab switching"""
        self.tabs[i].setObjectName("tab"+str(i))

        """create webview within the tabs top level widget"""
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("http://google.com/"))

        self.tabs[i].content.titleChanged.connect(lambda: self.set_tab_content(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.set_tab_content(i, "icon"))
        self.tabs[i].content.urlChanged.connect(lambda: self.set_tab_content(i, "url"))
        """add webview to tabs layout"""
        self.tabs[i].layout.addWidget(self.tabs[i].content)

        """set top level tab from list to layout"""
        self.tabs[i].setLayout(self.tabs[i].layout)

        """add tab to top level stackedwidget"""
        self.container.layout.addWidget(self.tabs[i])
        self.container.layout.setCurrentWidget(self.tabs[i])

        """create tab on tabbar representing this tab """
        """set tabData to <#> so it knows what self.tabs[#] it needs to control"""
        self.tabbar.addTab("New Tab")
        self.tabbar.setTabData(i,{"object": "tab"+str(i),"initial": i})
        self.tabbar.setCurrentIndex(i)

        self.tabcount += 1

    def set_tab_content(self, i, types):
        # self.tabs[i].objectName = tab1
        tab_name = self.tabs[i].objectName()
        count = 0
        running = True
        current_tab = self.tabbar.tabData(self.tabbar.currentIndex())["object"]

        if current_tab == tab_name and types == "url":
            new_url = self.findChild(QWidget, tab_name).content.url().toString()
            self.addressbar.setText(new_url)
            return False

        while running:
            tab_data_name = self.tabbar.tabData(count)

            if count >= 99:
                running = False
            if tab_name == tab_data_name["object"]:
                if types == "title":
                    new_title = self.findChild(QWidget, tab_name).content.title()
                    self.tabbar.setTabText(count, new_title)
                elif types == "icon":
                    new_icon = self.findChild(QWidget, tab_name).content.icon()
                    self.tabbar.setTabIcon(count, new_icon)
                running = False
            else:
                count += 1

    def go_back(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content
        tab_content.back()

    def go_forward(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content
        tab_content.forward()

    def reload(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content
        tab_content.reload()

if __name__ == '__main__':
    app=QApplication(sys.argv)
    window = App()

    with open("main.css","r") as style:
        app.setStyleSheet(style.read())
    sys.exit(app.exec_())