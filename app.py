import sys
import os, errno
from PySide.QtGui import QApplication, QMainWindow, QWidget
from PySide.QtGui import QDesktopWidget
from PySide import QtCore
from gui.ui_mainwindow import Ui_MainWindow
from gui.ui_projector import Ui_Projector
from gui.ui_editor import Ui_Editor
from gui.ui_picker import Ui_Picker
from model import Database, Song
from sys import stderr

class Slide(object):
    def __init__(self, title, content):
        self.title = title
        self.content = self.convert_line_breaks(content)

    def convert_line_breaks(self, text):
        return text.replace('\n', '<br>')


class LyricalProjector(QWidget, Ui_Projector):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.style = '''
        color: white;
        background-color: black;
        padding-top: 20px;
        padding-left: 20px;
        font-size: 40px;
        text-align: center;
        ''' #TODO: text-align doesn't work with QTextBrowser widgets
        self.content.setStyleSheet(self.style)

    def update(self, slide):
        '''set title and content to slide
        '''
        self.title.setText(slide.title)
        self.content.setText(slide.content)

    def focusInEvent(self):
        '''When focused, set the focus back to the control window.
        '''
        pass

class LyricalControl(QMainWindow, Ui_MainWindow):
    def __init__(self, projector_window):
        QMainWindow.__init__(self)
        self.projector = projector_window
        self.setupUi(self)
        self.songs = []

        self.lyrics.clicked.connect(self.update_screen)
        self.add_button.clicked.connect(self.show_picker)

    def add_song(self, song):
        self.songs.append(song)
        self.song_list.addItem(song.title)

    def remove_song(self):
        #controller.song_list.removeCurrentRow(0)
        pass

    def edit_song(self):
        #controller.song_list.getCurrentRow()
        pass

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            sys.exit()

    @QtCore.Slot()
    def update_screen(self):
        title = self.song_list.currentItem().text()
        content = self.lyrics.currentItem().text()
        self.projector.update(Slide(title, content))

    @QtCore.Slot()
    def show_picker(self):
        db = get_database() #TODO: is multiple sqlite db handles the best way?
        self.picker = LyricalPicker(db, self)
        self.picker.show()


class LyricalPicker(QMainWindow, Ui_Picker):
    def __init__(self, db, controller):
        QMainWindow.__init__(self)
        self.db = db
        self.songs = []
        self.controller = controller
        self.setupUi(self)

        self.song_list.clicked.connect(self.click_song)
        self.song_list.doubleClicked.connect(self.add_song)
        self.add_button.clicked.connect(self.add_song)
        self.edit_button.clicked.connect(self.edit_song)
        self.cancel_button.clicked.connect(self.close_window)
        self.search_text.textChanged.connect(self.search)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    @QtCore.Slot()
    def click_song(self):
        '''Show song in self.lyrics
        '''
        #get index of item in song_list clicked
        #self.songs[index].lyrics_list
        pass

    @QtCore.Slot()
    def add_song(self):
        '''Give LyricalControl the song id
        '''
        song = self.song_list.currentItem()
        if song:
            self.controller.add_song(song)

    @QtCore.Slot()
    def edit_song(self):
        '''Give LyricalEdit the song id
        '''
        pass

    @QtCore.Slot()
    def new_song(self):
        '''Create a new song and add it to LyricalControl
        '''
        pass

    @QtCore.Slot()
    def search(self):
        results = self.db.find_songs(self.search_text.text())
        self.songs = results
        lyrics = [song.lyrics_list() for song in results]
        for lyric in lyrics:
            self.lyrics.insertItems(0, lyric)
            self.lyrics.setCurrentRow(0)

        titles = [song.title for song in results]
        for title in titles:
            self.song_list.insertItems(0, title)
            self.song_list.setCurrentRow(0)

    @QtCore.Slot()
    def close_window(self):
        self.close()


class LyricalEditor(QMainWindow, Ui_Editor):
    def __init__(self, db, song=None):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.db = db
        if not song:
            song = Song('','')

    @QtCore.Slot()
    def close_window(self):
        pass

    @QtCore.Slot()
    def save_edits(self):
        self.song.title = self.title
        self.song.lyrics = self.lyrics

        validation = self.song.validate

        if validation:
            self.db.push_song(song)
            self.close_window()
        else:
            pass # show error dialog


def get_database():
    data_directory = os.path.expanduser('~/.lyrical')
    try:
        os.makedirs(data_directory)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
    db = Database(data_directory + '/songs.sqlite')
    return db

def main():
    app = QApplication(sys.argv)
    projector = LyricalProjector()
    controller = LyricalControl(projector)
    projector.show()
    controller.show()

    #db = get_database()
    #editor = LyricalEditor(db)
    #editor.show()

    song = Song()
    controller.lyrics.insertItems(0, song.lyrics_list())
    controller.lyrics.setCurrentRow(0)
    controller.song_list.addItem(song.title)
    controller.song_list.setCurrentRow(0)

    desktop = QDesktopWidget()
    if desktop.screenCount() < 2:
        stderr.write('Need at least two screens connected.')
        sys.exit()
    else:
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
