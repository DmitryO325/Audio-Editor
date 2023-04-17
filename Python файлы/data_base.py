import datetime
import os
import shutil
import sqlite3
import wave

from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox

import get_audio_file

from language import find_necessary_text

from PyQt5.QtCore import QTime

status = 1


class SaveDataBase(QWidget):
    def __init__(self):
        super().__init__()
        os.chdir('../Файлы базы данных')

    def get_information(self, title):
        data_base_information = QFileDialog.getSaveFileName(self, find_necessary_text(1200),
                                                            title, f'{find_necessary_text(1211)} '
                                                                   f'(*.sqlite)', '.*.')[0]

        return data_base_information


class OpenDataBase(QWidget):
    def __init__(self):
        super().__init__()
        os.chdir('../Файлы базы данных')

    def get_information(self):
        data_base_information = QFileDialog.getOpenFileName(self, find_necessary_text(1201),
                                                            '', f'{find_necessary_text(1201)} '
                                                                f'(*.sqlite)', '.*.')[0]

        return data_base_information


def add_file_to_data_base(file=False):
    try:
        connection = sqlite3.connect('../Файлы базы данных/base_playlist_data_base.sqlite_sys')
        cursor = connection.cursor()

        if not file:
            list_of_paths = get_audio_file.GetFile().get_file(True)

        else:
            list_of_paths = [file]

        for path in list_of_paths:
            if path:
                path = path.replace('/', '\\')

            try:
                if path.endswith('.wav'):
                    file = wave.open(path)
                    seconds = str(datetime.timedelta(seconds=int(file.getnframes() / file.getframerate())))

                    cursor.execute('''
                INSERT INTO audio_files (
                                           path,
                                           title,
                                           file_format,
                                           duration,
                                           frequency,
                                           channels
                                       )
                                       VALUES (
                                           '{}',
                                           '{}',
                                            {},
                                           '{}',
                                            {},
                                            {}
                                       );
                '''.format(path, path[path.rindex('\\') + 1:path.rindex('.')],
                           cursor.execute("""SELECT id FROM file_formats WHERE title = '{}'""".format(
                               path[path.rindex(".") + 1:].upper())).fetchone()[0],
                           QTime(int(seconds[:-6]), int(seconds[-5:-3]), int(seconds[-2:])).toString('h:mm:ss'),
                           file.getframerate(), file.getnchannels()))

                else:
                    if file:
                        raise TypeError

                    cursor.execute('''
                INSERT INTO audio_files (
                                            path,
                                            title,
                                            file_format
                                        )
                                        VALUES (
                                            '{}',
                                            '{}',
                                             {}
                                        );
                '''.format(path, path[path.rindex('\\') + 1:path.rindex('.')],
                           cursor.execute("""SELECT id FROM file_formats WHERE title = 
                                         '{}'""".format(path[path.rindex(".") + 1:].upper())).fetchone()[0]))

            except sqlite3.IntegrityError:
                pass

            except EOFError:
                pass

        connection.commit()
        connection.close()

    except (FileNotFoundError, ValueError, TypeError):
        connection.commit()
        connection.close()


def delete_from_playlist(audio_files):
    connection = sqlite3.connect('../Файлы базы данных/base_playlist_data_base.sqlite_sys')
    cursor = connection.cursor()

    list_of_files = sorted(audio_files, reverse=True)
    list_of_files = [number + 1 for number in list_of_files]

    for number_of_file in list_of_files:
        cursor.execute(f'''DELETE FROM audio_files WHERE id = {number_of_file}''')

    tuple_of_all_id = cursor.execute('''SELECT * FROM audio_files''').fetchall()

    for id_of_file in range(1, len(tuple_of_all_id) + 1):
        cursor.execute(f'''UPDATE audio_files SET id = {id_of_file} 
                           WHERE id = {tuple_of_all_id[id_of_file - 1][0]}''')

    connection.commit()
    connection.close()


def clear_playlist():
    connection = sqlite3.connect('../Файлы базы данных/base_playlist_data_base.sqlite_sys')
    cursor = connection.cursor()

    cursor.execute('''DELETE FROM audio_files''')

    connection.commit()
    connection.close()


def save_playlist(window):
    global status

    if not window.playlist.rowCount():
        return

    number = 1
    base_title = find_necessary_text(1500)

    if f'{base_title}.sqlite' in os.listdir():
        while True:
            title = f'{base_title} ({str(number)})'

            if f'{title}.sqlite' not in os.listdir():
                break

            number += 1

    else:
        title = base_title

    try:
        final_file = SaveDataBase().get_information(title).replace('/', '\\')
        base_file_error = 0
        status = 1

        try:
            if final_file[final_file.rindex('\\') + 1:] == '../Файлы базы данных/base_playlist_data_base.sqlite_sys':
                base_file_error = 1
                raise PermissionError

            if os.path.isfile(final_file):
                os.remove(final_file)

            shutil.copy('../Файлы базы данных/base_playlist_data_base.sqlite_sys', final_file)

        except PermissionError:
            status = 0

            save_error = QMessageBox(window)
            save_error.setWindowTitle(find_necessary_text(1600))
            save_error.setIcon(QMessageBox.Critical)

            if base_file_error:
                save_error.setText('{} "{}".'.format(find_necessary_text(1601),
                                                     final_file[final_file.rindex('\\') + 1:]))

            else:
                save_error.setText('{} "{}" {}.'.format(find_necessary_text(1000).title(),
                                                        final_file[final_file.rindex('\\') + 1:],
                                                        find_necessary_text(1020)))

            save_error.exec()
            window.show()

    except ValueError:
        pass


def open_playlist():
    playlist = OpenDataBase().get_information()

    source_connection = sqlite3.connect(playlist)
    source_cursor = source_connection.cursor()

    final_connection = sqlite3.connect('../Файлы базы данных/base_playlist_data_base.sqlite_sys')
    final_cursor = final_connection.cursor()

    try:
        files = source_cursor.execute('''SELECT * FROM audio_files''').fetchall()

        clear_playlist()

        for file in files:
            final_cursor.execute('''INSERT INTO audio_files VALUES (?, ?, ?, ?, ?, ?, ?)''', file)

    except sqlite3.OperationalError:
        pass

    source_connection.commit()
    source_connection.close()

    final_connection.commit()
    final_connection.close()
