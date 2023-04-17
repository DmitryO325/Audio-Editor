import datetime
import shutil
import struct
import sys
import wave
import os

import get_audio_file
import language

from language import find_necessary_text

from PyQt5.QtCore import Qt, QTime, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, \
    QFileDialog, QMessageBox, QApplication

from Ui_Widget import Ui_main_widget


class SaveFile(QWidget):
    def __init__(self):
        super().__init__()

    def get_information(self, filename):
        os.chdir('../Аудио')

        wave_filename_information = QFileDialog.getSaveFileName(self, find_necessary_text(1200),
                                                                filename, f'{find_necessary_text(1210)} '
                                                                          f'(*.wav)', '.*.')

        return wave_filename_information


class WrongFormat(Exception):
    pass


# class DownloadBar(QThread):
#     def __init__(self, main_window, new_frames_in_struct_start, new_frames_in_struct_final,
#                  volume_value, download_progress):
#         super().__init__()
#         self.main_window = main_window
#         self.new_frames_in_struct_start = new_frames_in_struct_start
#         self.new_frames_in_struct_final = new_frames_in_struct_final
#         self.volume_value = volume_value
#         self.download_progress = download_progress
#
#     def run(self):
#         global thread_works
#
#         thread_works = True
#         for number_of_element in range(len(self.new_frames_in_struct_start)):
#             self.new_frames_in_struct_final.append(
#                 self.new_frames_in_struct_start[number_of_element] *
#                 self.volume_value // 100)
#             self.download_progress.setValue((number_of_element + 1) * 100 //
#                                             len(self.new_frames_in_struct_start))
#
#         thread_works = False


class EditorWindow(QWidget, Ui_main_widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.link_text = self.last_link = ''
        self.wave_file = None
        self.number_of_frame = 0

        self.language_first_change = True
        self.set_language()
        self.language_first_change = False

        self.initUI()

        self.start_number_of_frame = self.final_number_of_frame = None
        self.download_progress.hide()

    def initUI(self):
        self.logo = QIcon('Иконки/Логотип.png')
        self.setWindowIcon(self.logo)

        self.open_wave()

        self.select_link.clicked.connect(self.open_link)
        self.select_file.clicked.connect(self.open_file)

        self.save_audio.clicked.connect(self.change_audio)
        self.track.valueChanged.connect(self.change_time)
        self.volume.valueChanged.connect(self.change_volume)

        self.crop_on_left.clicked.connect(self.crop_audio_on_left)
        self.crop_on_right.clicked.connect(self.crop_audio_on_right)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.open_file()

        if event.key() == Qt.Key_S:
            if self.save_audio.setEnabled(True):
                self.change_audio()

        if event.key() == Qt.Key_K:
            self.crop_audio_on_left()

        if event.key() == Qt.Key_L:
            self.crop_audio_on_right()

    def set_language(self):  # установка нужного языка в программе
        language.language_is_changing = not self.language_first_change
        language.set_language_for_editor(self)

    def open_link(self):
        self.link_text = self.last_link = self.new_link.text()
        self.open_wave()

    def open_file(self):
        self.last_link = self.link_text
        self.link_text = get_audio_file.GetFile().get_file()
        self.new_link.setText(self.link_text)
        self.open_wave()

    def open_wave(self):
        try:
            self.wave_file = wave.open(self.link_text, 'rb')
            self.link_text = self.link_text.replace('/', '\\')
            self.new_link.setText(self.link_text)
            self.edit_table.setItem(0, 0, QTableWidgetItem(self.link_text[
                                                           self.link_text.rindex('\\') + 1:
                                                           self.link_text.rindex('.wav')]))
            self.edit_table.setItem(1, 0, QTableWidgetItem(str(self.wave_file.getframerate())))
            self.edit_table.setItem(2, 0, QTableWidgetItem(str(self.wave_file.getnchannels())))
            self.edit_table.setItem(3, 0, QTableWidgetItem(str(self.wave_file.getnframes())))

            number = 1
            while True:
                new_link_text = self.link_text[self.link_text.rindex('\\') + 1: self.link_text.rindex('.wav')] + \
                                f' ({str(number)})' + '.wav'

                if new_link_text not in os.listdir():
                    self.edit_table.setItem(0, 1, QTableWidgetItem(new_link_text[:new_link_text.rindex('.wav')]))
                    break

                number += 1

            self.edit_table.setItem(1, 1, QTableWidgetItem(str(self.wave_file.getframerate())))
            self.edit_table.setItem(2, 1, QTableWidgetItem(str(self.wave_file.getnchannels())))
            self.edit_table.setItem(3, 1, QTableWidgetItem(str(self.wave_file.getnframes())))

            total_seconds = str(datetime.timedelta(seconds=int(self.wave_file.getnframes() /
                                                               self.wave_file.getframerate())))

            if 'day' in total_seconds:
                total_seconds = str(int(total_seconds[:total_seconds.index(' day')])
                                    * 24 + int(total_seconds[total_seconds.index(', ') + 2])) + ':' + \
                                total_seconds[total_seconds.index(':') + 1:]

            audio_time_total_text = QTime(
                int(total_seconds[:-6]),
                int(total_seconds[-5:-3]),
                int(total_seconds[-2:]))

            self.source_audio_time_total.setTime(audio_time_total_text)
            self.final_audio_time_finish.setTime(audio_time_total_text)
            self.final_audio_time_start.setTime(QTime(0, 0, 0))

            self.link_now.setText(self.link_text)
            self.link_label.setText(find_necessary_text(1300))

            self.crop_error.clear()
            self.file_error.clear()
            self.save_audio.setEnabled(True)

            self.track.setValue(0)
            self.source_audio_time_now.setTime(QTime(0, 0, 0))
            self.volume.setValue(100)

            self.start_number_of_frame = 0
            self.final_number_of_frame = self.wave_file.getnframes() - 1

        except FileNotFoundError:
            self.crop_error.clear()

            if self.link_text:
                self.file_error.setText(find_necessary_text(1310))

            self.new_link.setText(self.last_link)

        except EOFError:
            error_dialog = QMessageBox(self)
            error_dialog.setWindowTitle("Проблемка...")
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Аудиофайл недоступен.")
            error_dialog.exec()

        finally:
            self.prohibit_editing()

            self.edit_table.resizeColumnsToContents()
            self.edit_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def change_time(self):
        if self.wave_file is not None:
            self.number_of_frame = self.number_of_frame = self.track.value() * \
                                                          self.wave_file.getnframes() // self.track.maximum()

            seconds = str(datetime.timedelta(seconds=int(self.number_of_frame / self.wave_file.getframerate())))

            if 'day' in seconds:
                seconds = str(int(seconds[:seconds.index(' day')]) * 24 +
                              int(seconds[seconds.index(', ') + 2])) + ':' + \
                          seconds[seconds.index(':') + 1:]

            audio_time_now_text = QTime(
                int(seconds[:-6]),
                int(seconds[-5:-3]),
                int(seconds[-2:]))

            self.source_audio_time_now.setTime(audio_time_now_text)

    def change_volume(self):
        self.volume_number.display(self.volume.value())

    def check_cropping(self):
        self.file_error.clear()

        if self.start_number_of_frame >= self.final_number_of_frame:
            self.crop_error.setText(find_necessary_text(1320))
            self.save_audio.setEnabled(False)

        else:
            self.crop_error.clear()
            self.save_audio.setEnabled(True)

    def crop_audio_on_left(self):
        if self.wave_file is not None:
            self.final_audio_time_start.setTime(self.source_audio_time_now.time())
            self.start_number_of_frame = self.track.value() * self.wave_file.getnframes() // self.track.maximum()
            self.check_cropping()

    def crop_audio_on_right(self):
        if self.wave_file is not None:
            self.final_audio_time_finish.setTime(self.source_audio_time_now.time())
            self.final_number_of_frame = self.track.value() * self.wave_file.getnframes() // self.track.maximum()
            self.check_cropping()

    def prohibit_editing(self):
        for number_of_row in range(self.edit_table.rowCount()):
            item = self.edit_table.item(number_of_row, 0)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def change_audio(self):
        try:
            information_about_new_wave_file = SaveFile().get_information(self.edit_table.item(0, 1).text())

            if information_about_new_wave_file[1] == '.*.':
                raise FileNotFoundError

            if not information_about_new_wave_file[0].endswith('.wav'):
                raise WrongFormat

            shutil.copy(self.link_now.text(), self.link_now.text() + '___')

            source_file = wave.open(self.link_now.text() + '___', 'rb')

            new_file = wave.open(information_about_new_wave_file[0], 'wb')

            frames = struct.unpack("<" + str(source_file.getnframes() * source_file.getnchannels()) + "h",
                                   source_file.readframes(source_file.getnframes()))

            new_frames_in_struct_start = frames[self.start_number_of_frame * self.wave_file.getnchannels():
                                                (self.final_number_of_frame + 1) * self.wave_file.getnchannels()]

            new_frames_in_struct_final = []
            volume_value = self.volume_number.intValue()
            self.download_progress.show()

            for number_of_element in range(len(new_frames_in_struct_start)):
                new_frames_in_struct_final.append(
                    new_frames_in_struct_start[number_of_element] *
                    volume_value // 100)
                self.download_progress.setValue((number_of_element + 1) * 100 //
                                                len(new_frames_in_struct_start))

            new_frames_in_struct_final = tuple(new_frames_in_struct_final)

            new_frames = struct.pack("<" + str(len(new_frames_in_struct_final)) + "h",
                                     *new_frames_in_struct_final)

            new_file.setparams(source_file.getparams())
            new_file.setframerate(int(self.edit_table.item(1, 1).text()))
            new_file.setnchannels(int(self.edit_table.item(2, 1).text()))

            new_file.writeframes(new_frames)

            source_file.close()
            new_file.close()

            os.remove(self.link_now.text() + '___')

            confirmation_of_saving = QMessageBox(self)
            confirmation_of_saving.setWindowTitle(find_necessary_text(1400))
            confirmation_of_saving.setIcon(QMessageBox.Information)
            confirmation_of_saving.setText(find_necessary_text(1401))
            confirmation_of_saving.exec()

            self.download_progress.hide()
            self.download_progress.setValue(0)

        except FileNotFoundError:
            pass

        except WrongFormat:
            confirmation_of_saving = QMessageBox(self)
            confirmation_of_saving.setWindowTitle(find_necessary_text(1410))
            confirmation_of_saving.setIcon(QMessageBox.Critical)
            confirmation_of_saving.setText(find_necessary_text(1411))
            confirmation_of_saving.exec()


def open_editor_window():
    global editor_example

    editor_example = EditorWindow()
    editor_example.show()


if __name__ == '__main__':
    application = QApplication(sys.argv)
    open_editor_window()
    sys.exit(application.exec())
