import sqlite3

class Song(object):
    def __init__(self, id=None, title=None, lyrics=None, copyright=None):
        self.title = title
        self.lyrics = lyrics
        self.copyright = copyright
        self.id = id

    def lyrics_list(self):
        return self.lyrics.split('\n\n')

    def validate(self):
        if not self.title:
            return False, 'Title cannot be blank'
        elif not self.lyrics:
            return False, 'Lyrics cannot be empty'
        else:
            return True, ''

    def __repr__(self):
        return '{!r} - {!r}\n{!r}\n{!r}'.format(self.id, self.title,
                                        self.lyrics, self.copyright)


class Database(object):
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()

    def create_tables(self):
        self.c.execute('CREATE TABLE songs ( '
                       'id INTEGER PRIMARY KEY, '
                       'title STRING, '
                       'lyrics STRING, '
                       'copyright STRING)')

    def add_song(self, *songs):
        rowids = []
        for song in songs:
            self.c.execute('INSERT INTO songs (title, lyrics, copyright) '
                            'VALUES (?, ?, ?)',
                            (song.title, song.lyrics, song.copyright))
            rowids.append(self.c.lastrowid)
        self.conn.commit()
        if len(rowids) == 1:
            return rowids[0]
        else:
            return rowids

    def update_song(self, song):
        self.c.execute('UPDATE songs SET title=?, lyrics=?, copyright=? '
                        'WHERE id=?',
                        (song.title, song.lyrics, song.copyright, song.id))
        self.conn.commit()

    def push_song(self, song):
        valid, reason = song.validate()
        assert valid == True,\
            "Song is not valid: {} \n {!r}".format(reason, song)
        if song.id:
            return self.update_song(song)
        else:
            return self.add_song(song)

    def find_songs(self, query=None):
        '''Returns a list of Song objects containing the query string.
        If the query is empty, return all of them.
        '''
        if query:
            query = "%%%s%%" % query
            self.c.execute("SELECT DISTINCT id, title, lyrics, copyright "
                           "FROM songs WHERE title LIKE ? OR lyrics LIKE ?",
                           (query, query))
        else:
            self.c.execute("SELECT id, title, lyrics, copyright FROM songs")
        results = self.c.fetchall()
        return [Song(r[0], r[1], r[2], r[3]) for r in results]

    def get_song(self, id):
        self.c.execute("SELECT TOP 1 title, lyrics, copyright"
                       "FROM songs where id = ?", (id,))
        return Song(*self.c.fetchone())

    def __del__(self):
        self.c.close()
