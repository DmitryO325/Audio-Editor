from language import find_necessary_text

from PyQt5.QtWidgets import QWidget, QFileDialog


class GetFile(QWidget):
    def __init__(self):
        super().__init__()

    def get_file(self, several=False):
        if not several:
            wave_filename = QFileDialog.getOpenFileName(self, find_necessary_text(1202),
                                                        '../Аудио', f'{find_necessary_text(1210)} (*.wav);;'
                                                                    f'{find_necessary_text(1210)} (*.wav; *.mp3; '
                                                                    '*.ogg; *.mid; *.aac; *.flac; *.wma)', '.*.')[0]

            return wave_filename

        else:
            wave_filenames = QFileDialog.getOpenFileNames(self, find_necessary_text(1203),
                                                          '../Аудио', f'{find_necessary_text(1210)} (*.wav);;'
                                                                      f'{find_necessary_text(1210)} (*.wav; *.mp3; '
                                                                      '*.ogg; *.mid; *.aac; *.flac; *.wma)', '.*.')[0]

            return wave_filenames


class GetFolder(QWidget):
    def __init__(self):
        super().__init__()

    def get_folder(self):
        folder = QFileDialog.getExistingDirectory(self, find_necessary_text(1204), '')

        return folder
