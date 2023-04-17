import datetime
import os
import random
import sqlite3
import sys
import time

import language
import run_music
import editor_elements
import data_base
import background_colour
import get_audio_file

from language import find_necessary_text

from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QTime
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, \
    QHeaderView, QAbstractItemView, QMessageBox

from Ui_Main_window import Ui_audio_editor


class StartMusic(QThread):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        run_music.run(self.main_window, self.main_window.audio_slider)


class MainWindow(QMainWindow, Ui_audio_editor):
    update_window, turn_on_music, update_colour, update_to_base, audio_error = \
        pyqtSignal(), pyqtSignal(), pyqtSignal(), pyqtSignal(), pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.number_of_phrase = random.randint(900, 910)

        self.language_first_change = True
        self.set_language()
        self.language_first_change = False

        self.values_of_data = None

        self.program_finished = False
        self.stop_time_text = False

        self.connection = sqlite3.connect('../Файлы базы данных/base_playlist_data_base.sqlite_sys')
        self.cursor = self.connection.cursor()

        self.colour_class = background_colour.ColourOnBackground(self)
        self.colour_class.start()

        self.initUI()
        self.configure_playlist()

    def initUI(self):
        self.logo = QIcon('../Иконки/Логотип.png')
        self.setWindowIcon(self.logo)

        self.play_picture = QIcon('../Иконки/Воспроизвести.png')
        self.play_btn.setIcon(self.play_picture)
        self.play_btn.setIconSize(QSize(80, 80))

        self.pause_picture = QIcon('../Иконки/Пауза.png')
        self.pause_btn.setIcon(self.pause_picture)
        self.pause_btn.setIconSize(QSize(80, 80))

        self.stop_picture = QIcon('../Иконки/Стоп.png')
        self.stop_btn.setIcon(self.stop_picture)
        self.stop_btn.setIconSize(QSize(80, 80))

        self.rew_back_picture = QIcon('../Иконки/Назад.png')
        self.rewind_back_btn.setIcon(self.rew_back_picture)
        self.rewind_back_btn.setIconSize(QSize(56, 56))

        self.rew_forward_picture = QIcon('../Иконки/Вперёд.png')
        self.rewind_forward_btn.setIcon(self.rew_forward_picture)
        self.rewind_forward_btn.setIconSize(QSize(56, 56))

        self.prev_comp_picture = QIcon('../Иконки/Предыдущая.png')
        self.prev_comp_btn.setIcon(self.prev_comp_picture)
        self.prev_comp_btn.setIconSize(QSize(56, 56))

        self.next_comp_picture = QIcon('../Иконки/Следующая.png')
        self.next_comp_btn.setIcon(self.next_comp_picture)
        self.next_comp_btn.setIconSize(QSize(56, 56))

        self.rep_comp_picture = QIcon('../Иконки/Повторить.png')
        self.repeat_comp_btn.setIcon(self.rep_comp_picture)
        self.repeat_comp_btn.setIconSize(QSize(48, 48))

        self.add_file_picture = QIcon('../Иконки/Добавить.png')
        self.add_file_btn.setIcon(self.add_file_picture)
        self.add_file_btn.setIconSize(QSize(42, 42))

        self.del_file_picture = QIcon('../Иконки/Удалить.png')
        self.delete_file_btn.setIcon(self.del_file_picture)
        self.delete_file_btn.setIconSize(QSize(42, 42))

        self.clear_pl_picture = QIcon('../Иконки/Очистить.png')
        self.clear_playlist_btn.setIcon(self.clear_pl_picture)
        self.clear_playlist_btn.setIconSize(QSize(42, 42))

        self.save_pl_picture = QIcon('../Иконки/Сохранить.png')
        self.save_playlist_btn.setIcon(self.save_pl_picture)
        self.save_playlist_btn.setIconSize(QSize(42, 42))

        self.open_pl_picture = QIcon('../Иконки/Открыть.png')
        self.open_playlist_btn.setIcon(self.open_pl_picture)
        self.open_playlist_btn.setIconSize(QSize(42, 42))

        self.play_btn.clicked.connect(self.play_audio)
        self.play_mn.triggered.connect(self.play_audio)

        self.pause_btn.clicked.connect(self.pause_audio)
        self.pause_mn.triggered.connect(self.pause_audio)

        self.stop_btn.clicked.connect(lambda: self.stop_audio())
        self.stop_mn.triggered.connect(lambda: self.stop_audio())

        self.repeat_comp_btn.clicked.connect(self.repeat_composition)
        self.repeat_composition_mn.triggered.connect(self.repeat_composition)

        self.rewind_back_btn.clicked.connect(self.rewind_back)
        self.rewind_back_mn.triggered.connect(self.rewind_back)

        self.rewind_forward_btn.clicked.connect(self.rewind_forward)
        self.rewind_forward_mn.triggered.connect(self.rewind_forward)

        self.prev_comp_btn.clicked.connect(self.previous_composition)
        self.previous_composition_mn.triggered.connect(self.previous_composition)

        self.next_comp_btn.clicked.connect(self.next_composition)
        self.next_composition_mn.triggered.connect(self.next_composition)

        self.add_file_btn.clicked.connect(self.add_to_playlist)
        self.add_file_mn.triggered.connect(self.add_to_playlist)

        self.delete_file_btn.clicked.connect(self.delete_from_playlist)
        self.delete_file_mn.triggered.connect(self.delete_from_playlist)

        self.clear_playlist_btn.clicked.connect(self.clear_playlist)
        self.clear_playlist_mn.triggered.connect(self.clear_playlist)

        self.save_playlist_btn.clicked.connect(self.save_playlist)
        self.save_playlist_mn.triggered.connect(self.save_playlist)

        self.open_playlist_btn.clicked.connect(self.open_playlist)
        self.open_playlist_mn.triggered.connect(self.open_playlist)

        self.language_options_mn.triggered.connect(self.set_language)

        self.open_editor_window_mn.triggered.connect(self.open_editor)

        self.playlist.doubleClicked.connect(self.set_number_of_audio)

        self.audio_slider.sliderMoved.connect(self.change_time)
        self.audio_slider.sliderReleased.connect(self.set_time)

        self.open_file_mn.triggered.connect(self.open_file)
        self.open_folder_mn.triggered.connect(self.open_folder)

        self.volume_slider.valueChanged.connect(self.change_volume)

        self.volume_minus_mn.triggered.connect(self.reduce_volume)
        self.volume_plus_mn.triggered.connect(self.increase_volume)
        self.volume_off_mn.triggered.connect(self.off_volume)

        self.update_window.connect(lambda: self.set_options(*self.values_of_data))
        self.turn_on_music.connect(self.play_audio)
        self.update_to_base.connect(self.make_base_options)
        self.audio_error.connect(lambda: run_music.activate_audio_error(self))

        for speed_button in self.speed_menu.actions():
            speed_button.triggered.connect(self.change_speed)

        self.update_colour.connect(self.change_colour)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F:
            self.play_audio()

        if event.key() == Qt.Key_G:
            self.pause_audio()

        if event.key() == Qt.Key_H:
            self.stop_audio()

        if event.key() == Qt.Key_J:
            self.previous_composition()

        if event.key() == Qt.Key_K:
            self.repeat_composition()

        if event.key() == Qt.Key_L:
            self.next_composition()

        if event.key() == Qt.Key_N:
            self.rewind_back()

        if event.key() == Qt.Key_M:
            self.rewind_forward()

        if event.key() == Qt.Key_A:
            self.open_playlist()

        if event.key() == Qt.Key_S:
            self.save_playlist()

        if event.key() == Qt.Key_D:
            self.add_to_playlist()

        if event.key() == Qt.Key_C:
            self.off_volume()

        if event.key() == Qt.Key_V:
            self.reduce_volume()

        if event.key() == Qt.Key_B:
            self.increase_volume()

        if event.key() == Qt.Key_E:
            self.open_editor()

    def closeEvent(self, event):
        self.program_finished = True

    def set_language(self):  # установка нужного языка в программе
        language.language_is_changing = not self.language_first_change
        language.set_language_for_player(self)

    def change_colour(self):
        self.main_widget.setStyleSheet(f'''background-color: 
        rgb({self.colour_class.red}, {self.colour_class.green}, {self.colour_class.blue})''')

    def configure_playlist(self):
        connection = sqlite3.connect('../Файлы базы данных/base_playlist_data_base.sqlite_sys')
        cursor = connection.cursor()

        self.playlist.setColumnCount(5)
        self.playlist.setSelectionBehavior(QAbstractItemView.SelectRows)

        rows = cursor.execute('''SELECT * FROM audio_files''').fetchall()

        for number_of_row in range(len(rows)):
            self.playlist.insertRow(number_of_row)

            for number_of_column in range(5):
                if number_of_column == 1:
                    continue

                if number_of_column == 3:
                    self.playlist.setItem(number_of_row, number_of_column,
                                          QTableWidgetItem(cursor.execute(
                                              f'''SELECT title FROM file_formats WHERE id = 
                                                    {list(rows)[number_of_row][3]}''').fetchone()[0]))

                else:
                    self.playlist.setItem(number_of_row, number_of_column,
                                          QTableWidgetItem(str(rows[number_of_row][number_of_column])))

                item = self.playlist.item(number_of_row, number_of_column)

                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                item.setBackground(QColor('#E7E9FF'))
                item.setForeground(QBrush(QColor('#000735')))
                item.setTextAlignment(Qt.AlignCenter)

        for attempt in range(2):
            self.playlist.removeColumn(0)

        self.playlist.setHorizontalHeaderLabels((find_necessary_text(800),
                                                 find_necessary_text(801),
                                                 find_necessary_text(802)))

        self.playlist.resizeColumnsToContents()
        self.playlist.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def update_playlist(self):
        for number_of_row in range(self.playlist.rowCount()):
            self.playlist.removeRow(0)

        self.configure_playlist()

    def clear_playlist(self):
        data_base.clear_playlist()
        self.stop_audio()
        run_music.number_of_audio_file = 1

        self.update_playlist()

    def add_to_playlist(self):
        data_base.add_file_to_data_base()
        self.update_playlist()

    def delete_from_playlist(self):
        data_base.delete_from_playlist(set(index.row() for index in self.playlist.selectedIndexes()))
        self.update_playlist()

    def save_playlist(self):
        data_base.save_playlist(self)

    def save_dialog(self):
        if self.playlist.rowCount():
            save_question = QMessageBox(self)
            save_question.setWindowTitle(find_necessary_text(1100))
            save_question.setIcon(QMessageBox.Warning)
            save_question.setText(find_necessary_text(1101))

            yes_button = save_question.addButton(find_necessary_text(1110), QMessageBox.YesRole)
            save_question.addButton(find_necessary_text(1111), QMessageBox.NoRole)
            cancel_button = save_question.addButton(find_necessary_text(521), QMessageBox.RejectRole)

            save_question.exec()

            if save_question.clickedButton() != cancel_button:
                if save_question.clickedButton() == yes_button:
                    data_base.save_playlist(self)
                    self.hide()

                if not data_base.status:
                    self.show()
                    return

                self.clear_playlist()

            else:
                return False

        return True

    def open_playlist(self):
        if self.save_dialog():
            data_base.open_playlist()
            self.configure_playlist()

        self.show()

    def open_file(self):
        if self.save_dialog():
            self.play_audio()

        self.show()

    def open_folder(self):
        if self.save_dialog():
            folder = get_audio_file.GetFolder().get_folder()

            if folder:
                for file in os.listdir(folder):
                    data_base.add_file_to_data_base(f'{folder}/{file}')

            self.configure_playlist()
            self.show()

    def set_number_of_audio(self):
        self.stop_audio(False)
        run_music.number_of_audio_file = self.playlist.currentRow() + 1
        self.play_audio()

    def get_values_from_slider(self):
        slider_value = self.audio_slider.value()

        audio_title_text = run_music.title[run_music.title.rindex('\\') + 1:run_music.title.rindex('.wav')]
        audio_slider_value = round(self.audio_slider.maximum() / run_music.quantity_of_frames * slider_value)

        planned_number_of_frame = slider_value * run_music.quantity_of_frames / self.audio_slider.maximum()
        seconds = str(datetime.timedelta(seconds=int(planned_number_of_frame / run_music.rate_of_file)))

        if 'day' in seconds:
            seconds = str(int(seconds[:seconds.index(' day')]) * 24 +
                          int(seconds[seconds.index(', ') + 2])) + ':' + \
                      seconds[seconds.index(':') + 1:]

        audio_time_now_text = QTime(
            int(seconds[:-6]),
            int(seconds[-5:-3]),
            int(seconds[-2:]))

        total_seconds = str(datetime.timedelta(seconds=int(run_music.quantity_of_frames / run_music.rate_of_file)))

        if 'day' in total_seconds:
            total_seconds = str(int(total_seconds[:total_seconds.index(' day')])
                                * 24 + int(total_seconds[total_seconds.index(', ') + 2])) + ':' + \
                            total_seconds[total_seconds.index(':') + 1:]

        audio_time_total_text = QTime(
            int(total_seconds[:-6]),
            int(total_seconds[-5:-3]),
            int(total_seconds[-2:]))

        return audio_title_text, audio_slider_value, audio_time_now_text, audio_time_total_text

    def set_options(self, audio_title_text, audio_slider_text, audio_time_now_text, audio_time_total_text):
        if audio_time_now_text.toString()[0:2] != '00':
            self.audio_time_now.setDisplayFormat('h:mm:ss')

        else:
            self.audio_time_now.setDisplayFormat('m:ss')

        if audio_time_total_text.toString()[0:2] != '00':
            self.audio_time_total.setDisplayFormat('h:mm:ss')

        else:
            self.audio_time_total.setDisplayFormat('m:ss')

        self.audio_title.setText(f'{run_music.number_of_audio_file}. {audio_title_text}') \
            if run_music.audio_file is not None \
            else self.audio_title.setText(audio_title_text)

        self.audio_slider.setValue(audio_slider_text) if not self.stop_time_text else None

        self.audio_time_now.setTime(audio_time_now_text)
        self.audio_time_total.setTime(audio_time_total_text)

    def make_base_options(self):
        self.number_of_phrase = random.randint(900, 910)
        self.values_of_data = find_necessary_text(self.number_of_phrase), 0, QTime(0, 0, 0), QTime(0, 0, 0)
        self.set_options(*self.values_of_data)

    def start_thread(self):
        self.target_music = StartMusic(self)
        self.target_music.start()

    def change_volume(self):
        run_music.volume = self.volume_slider.value()
        self.volume_value.setText(str(self.volume_slider.value()))

    def reduce_volume(self):
        self.volume_slider.setValue(self.volume_slider.value() - 10)

    def increase_volume(self):
        self.volume_slider.setValue(self.volume_slider.value() + 10)

    def off_volume(self):
        self.volume_slider.setValue(0)

    def change_time(self):
        if run_music.audio_played == 'run':
            self.stop_time_text = True
            self.values_of_data = self.get_values_from_slider()
            self.set_options(*self.values_of_data)

    def set_time(self):
        if run_music.audio_played == 'run':
            self.stop_time_text = False
            run_music.new_position = True

    def change_speed(self):
        run_music.speed = float(self.sender().text())
        run_music.speed_changed = True

    def manage_audio(self, need_start_music):  # подключение аудиопотока для работы аудиофайла
        if run_music.audio_played != 'run':
            if run_music.audio_file is None and need_start_music:
                try:
                    run_music.get_file(self)
                    self.start_thread()

                except FileNotFoundError:
                    pass

            else:
                self.start_thread()

    def play_audio(self):  # воспроизведение
        time.sleep(0.1)
        self.manage_audio(True)
        run_music.audio_played = 'run' if run_music.audio_file is not None else 'stop'

    def pause_audio(self):  # пауза
        time.sleep(0.1)
        run_music.audio_played = 'pause'

    def stop_audio(self, stop_btn=True):  # стоп
        time.sleep(0.1)
        run_music.audio_played = 'stop'
        run_music.audio_file = None
        self.make_base_options()

        if stop_btn:
            run_music.number_of_audio_file = 1

    def repeat_composition(self):  # повторение
        run_music.audio_started_again = True

    def rewind_back(self):  # перемотка назад
        run_music.audio_rewind_back = True

    def rewind_forward(self):  # перемотка вперёд
        run_music.audio_rewind_forward = True

    def previous_composition(self):  # предыдущая композиция
        if run_music.audio_played != 'stop':
            self.stop_audio(False)
            run_music.number_of_audio_file -= 1 if run_music.number_of_audio_file - 1 != 0 else 0
            self.play_audio()

    def next_composition(self):  # следующая композиция
        if run_music.audio_played != 'stop':
            self.stop_audio(False)
            run_music.number_of_audio_file = run_music.number_of_audio_file + 1 \
                if run_music.number_of_audio_file < self.playlist.rowCount() else 1
            run_music.error = False
            self.play_audio() if run_music.number_of_audio_file != 1 else None

    def open_editor(self):  # запуск редактора
        editor_elements.open_editor_window()


if __name__ == '__main__':
    application = QApplication(sys.argv)
    player_example = MainWindow()
    player_example.show()
    sys.exit(application.exec())
