import struct
import pyaudio
import wave
import time
import datetime

from language import find_necessary_text

from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QMessageBox


class AudioFile:
    chunk = 1024

    def __init__(self, file, window):
        self.number_of_frame = 0

        self.wave_file = wave.open(file, 'r')
        self.pyaudio_file = pyaudio.PyAudio()
        self.open_stream(window)

    def open_stream(self, window):
        global quantity_of_frames, rate_of_file, error, number_of_audio_file

        try:
            self.stream = self.pyaudio_file.open(
                format=self.pyaudio_file.get_format_from_width(self.wave_file.getsampwidth()),
                channels=self.wave_file.getnchannels(),
                rate=int(self.wave_file.getframerate() * speed),
                output=True
            )

        except OSError:  # может возникнуть, если каналов в аудио больше, чем в звуковой карте компьютера
            try:
                self.stream = self.pyaudio_file.open(
                    format=self.pyaudio_file.get_format_from_width(self.wave_file.getsampwidth()),
                    channels=2,  # 2 канала есть абсолютно на всех звуковых картах
                    rate=int(self.wave_file.getframerate() * self.wave_file.getnchannels() // 2 * speed),
                    # сохраняем скорость, как должно было быть при каналах, установленных в аудиофайле
                    output=True
                )

            except OSError:
                error = True
                window.stop_audio(False)
                window.audio_error.emit()

        quantity_of_frames = self.wave_file.getnframes()
        rate_of_file = self.wave_file.getframerate()

    def play(self, window, audio_slider):
        global audio_file, audio_played, audio_started_again, audio_rewind_back, audio_rewind_forward, \
            number_of_audio_file, new_position, title, quantity_of_frames, rate_of_file, speed_changed, error

        while (data := self.wave_file.readframes(self.chunk)) != b'':
            if speed_changed:
                self.open_stream(window)
                speed_changed = False

            try:
                frames = struct.unpack("<" + str(self.chunk * self.wave_file.getnchannels()) + "h", data)

                new_frames = tuple([frame * volume // 100 for frame in frames])

                data = struct.pack("<" + str(len(new_frames)) + "h", *new_frames)

            except struct.error:
                pass

            audio_rewind_back = audio_rewind_forward = False

            self.stream.write(data)
            self.number_of_frame += self.chunk

            if not window.stop_time_text:
                window.values_of_data = self.get_values_from_audio(audio_slider)

            if audio_started_again:  # воспроизведение аудиофайла сначала
                time.sleep(0.1)
                self.wave_file.setpos(0)
                self.number_of_frame = 0
                audio_started_again = False

            if audio_rewind_back:  # перемотка назад на 10 секунд
                time.sleep(0.1)

                if self.wave_file.tell() - self.wave_file.getframerate() * 10 < 0:
                    self.number_of_frame = 0
                    self.wave_file.setpos(self.number_of_frame)

                else:
                    self.number_of_frame -= self.wave_file.getframerate() * 10
                    self.wave_file.setpos(self.number_of_frame)

                audio_rewind_back = False

            if audio_rewind_forward:  # перемотка вперёд на 10 секунд
                time.sleep(0.1)

                if self.wave_file.tell() + self.wave_file.getframerate() * 10 >= self.wave_file.getnframes():
                    self.number_of_frame = self.wave_file.getnframes() - 1
                    self.wave_file.setpos(self.number_of_frame)

                else:
                    self.number_of_frame += self.wave_file.getframerate() * 10
                    self.wave_file.setpos(self.number_of_frame)

                audio_rewind_forward = False

            if new_position:
                time.sleep(0.1)

                self.number_of_frame = audio_slider.value() * self.wave_file.getnframes() // audio_slider.maximum()
                self.wave_file.setpos(self.number_of_frame)

                window.values_of_data = self.get_values_from_audio(audio_slider)
                window.update_window.emit()
                new_position = False

            if audio_played != 'stop':
                if not window.stop_time_text:
                    window.update_window.emit()

            else:
                window.update_to_base.emit()

            if audio_played != 'run' or window.program_finished:
                break

        else:
            audio_played = 'stop'
            window.make_base_options()
            audio_file = title = quantity_of_frames = rate_of_file = None

            number_of_audio_file += 1

            if number_of_audio_file > window.playlist.rowCount():
                number_of_audio_file = 1

            else:
                window.turn_on_music.emit()

    def get_values_from_audio(self, audio_slider):
        audio_title_text = title[title.rindex('\\') + 1:title.rindex('.wav')]
        audio_slider_value = round(audio_slider.maximum() / self.wave_file.getnframes() * self.number_of_frame)

        seconds = str(datetime.timedelta(seconds=int(self.number_of_frame / self.wave_file.getframerate())))

        if 'day' in seconds:
            seconds = str(int(seconds[:seconds.index(' day')]) * 24 +
                          int(seconds[seconds.index(', ') + 2])) + ':' + \
                      seconds[seconds.index(':') + 1:]

        audio_time_now_text = QTime(
            int(seconds[:-6]),
            int(seconds[-5:-3]),
            int(seconds[-2:]))

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

        return audio_title_text, audio_slider_value, audio_time_now_text, audio_time_total_text


audio_file = title = quantity_of_frames = rate_of_file = None
audio_played = 'stop'  # проверка, проигрывается ли трек или нет
audio_started_again = audio_rewind_back = audio_rewind_forward = previous_audio = next_audio = False
wrong_format = new_position = speed_changed = error = False
number_of_audio_file = 1
volume = 100
speed = 1.0


def check_file():
    return audio_file


def get_file(window):
    global audio_file, title, number_of_audio_file, wrong_format, audio_played

    try:
        if not window.playlist.rowCount():
            window.add_to_playlist()

        title = window.cursor.execute(f'''SELECT path FROM audio_files WHERE id = 
                            {number_of_audio_file}''').fetchone()[0]
        title = title.replace('/', '\\')

        try:
            audio_file = AudioFile(title, window)

        except wave.Error:
            play_error = QMessageBox(window)
            file_type = title[title.rindex('.') + 1:].upper()
            play_error.setWindowTitle(find_necessary_text(1000).format(file_type))
            play_error.setIcon(QMessageBox.Critical)
            play_error.setText(find_necessary_text(1001).format(file_type))
            play_error.exec()

            number_of_audio_file += 1
            wrong_format = True

            if number_of_audio_file > window.playlist.rowCount():
                number_of_audio_file = 1

    except TypeError:
        pass


def run(window, audio_slider):
    global wrong_format, error

    if audio_played == 'run' and not wrong_format and not error:
        audio_file.play(window, audio_slider)

    else:
        wrong_format = error = False
        window.turn_on_music.emit() if number_of_audio_file != 1 else None


def activate_audio_error(window):
    audio_error = QMessageBox(window)
    audio_error.setWindowTitle(find_necessary_text(2100))
    audio_error.setIcon(QMessageBox.Critical)
    audio_error.setText(find_necessary_text(2101))
    audio_error.exec()
