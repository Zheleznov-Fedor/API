import sys

import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from scale import scale
from io import BytesIO

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
map_api_server = "http://static-maps.yandex.ru/1.x/"


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def getMap(top, sc='0.005'):
    d = True
    if not sc:
        sc = '0.005'
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
        print(response.json())
        json_response = response.json()
        try:
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
        except IndexError:
            return 0
        toponym_longitude, toponym_lattitude = scale(toponym)
    else:
        toponym_longitude, toponym_lattitude = str(n1), str(n2)
        print(toponym_longitude, toponym_lattitude)
    delta = [str(sc), str(sc)]

    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join(delta),
        "l": "map",
        'pt': ",".join([toponym_longitude, toponym_lattitude, 'round']),  # параметр, отвечающий за точку на карте
    }

    response = requests.get(map_api_server, params=map_params)
    bytes = response.content

    return bytes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.button.clicked.connect(self.click)

    def changeMap(self, b):
        f = open('map.png', 'wb')
        f.write(b)
        f.close()
        self.label.setPixmap(QPixmap('map.png'))

    def click(self):
        res = getMap(self.lineEdit.text(), self.lineEdit_2.text())
        self.changeMap(res)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
