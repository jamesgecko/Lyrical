#!/usr/bin/env python
import sys
import os, errno
from PySide.QtCore import Qt
from PySide.QtGui import QApplication
from PySide.QtGui import QDesktopWidget
from PySide.QtGui import QMessageBox
from PySide.QtGui import QWidget
from model import Database, Song
from sys import stderr

from lyrical_projector import LyricalProjector
from lyrical_control import LyricalControl

def get_database():
    db_path = "{}/songs.sqlite".format(os.path.expanduser('~/.lyrical'))

    if os.path.isfile(db_path):
        db = Database(db_path)
    else:
        try:
            db = Database(db_path)
            db.create_tables()
        except e:
            dialog = ModalDialog()
            dialog.error('Database init error {}: {}'.format(e.errno, e.strerror))
            raise
    return db

class ModalDialog(QWidget):
    def error(self, message):
        QMessageBox.critical(self, "Error", message)

def main():
    db = get_database()
    projection_screen = 1

    app = QApplication(sys.argv)
    projector = LyricalProjector(projection_screen)
    controller = LyricalControl(projector, db)
    projector.controller = controller

    controller.show()
    controller.raise_()

    #editor = LyricalEditor(db)
    #editor.show()

    song = Song(None, 'Amazing Grace', """Amazing Grace, how sweet the sound,
That saved a wretch like me
I once was lost but now am found,
Was blind but now I see.

'Twas Grace that taught
my heart to fear
And Grace, my fears relieved
How precious did that Grace appear
the hour I first believed""")
    controller.add_song(song)

    if QDesktopWidget().screenCount() < 2:
        error = ModalDialog()
        error.error('Need at least two screens connected.')
        sys.exit()
    else:
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
