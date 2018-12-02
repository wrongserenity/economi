class NewWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(NewWindow, self).__init__()
        # запускаем метод рисующий виджеты окна

        self.initUI()

    # пусть по умолчанию строка
    # будет пустой
    # в этой строке мы можем передать путь
    # к папке полученноый из диалога выбора директории
    def initUI(self, str=""):
        # описываем действие ("действие" - это понятие из QT -см. ссылки выше листинга)

        self.showFullScreen()
