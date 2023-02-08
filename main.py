import sys

import requests
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from scale import scale

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
map_api_server = "http://static-maps.yandex.ru/1.x/"
map_type = 'map'


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def getMap(top, sc='50'):
    d = True
    if not sc:
        sc = '50'
    sc = int(sc)
    if sc > 900000:
        sc = 900000
    if sc < 1:
        sc = 1
    sc /= 10000
    sc = str(sc)
    try:
        n1 = top.split()[0]
        n2 = top.split()[1]
    except IndexError:
        d = False

    try:
        if check_int(n1) and check_int(n2) and d:
            pass
        else:
            d = False
    except UnboundLocalError:
        d = False

    if not d:
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": top,
            "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)
        json_response = response.json()
        try:
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
        except IndexError:
            return 0
        toponym_longitude, toponym_lattitude = scale(toponym)
    else:
        toponym_longitude, toponym_lattitude = str(n1), str(n2)
    delta = [str(sc), str(sc)]

    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join(delta),
        "l": map_type,
        "pt": ",".join([toponym_longitude, toponym_lattitude, 'round']),  # параметр, отвечающий за точку на карте
    }

    response = requests.get(map_api_server, params=map_params)
    Im_bytes = response.content

    return Im_bytes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.button.clicked.connect(self.click)
        self.comboBox.currentTextChanged.connect(self.combo)

    def combo(self, val):
        global map_type
        if val == 'Схема':
            map_type = 'map'
        elif val == 'Спутник':
            map_type = 'sat'
        elif val == 'Гибрид':
            map_type = 'sat,skl'

    def changeMap(self, b):
        if b:
            f = open('map.png', 'wb')
            f.write(b)
            f.close()
            self.label.setPixmap(QPixmap('map.png'))

    def click(self):
        res = getMap(self.lineEdit.text(), self.lineEdit_2.text())
        self.changeMap(res)

    def keyPressEvent(self, event):  # обработка клавиш
        if event.key() == QtCore.Qt.Key_PageUp:  # увеличение/уменьшение масштаба
            text = self.lineEdit_2.text()
            if text is None:
                text = 1
            else:
                text = int(text)
                text *= 2
                if text > 900000:
                    text = 900000
                text = str(text)
            self.lineEdit_2.setText(text)
            self.click()
        if event.key() == QtCore.Qt.Key_PageDown:
            text = self.lineEdit_2.text()
            if text is None:
                text = 1
            else:
                text = int(text)
                text /= 2
                if text < 1:
                    text = 1
                text = str(text)
            self.lineEdit_2.setText(text)
            self.click()
        if event.key() == QtCore.Qt.Key_Enter:  # должно создавать карту при нажатии на enter, но у меня не заработало
            self.click()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
