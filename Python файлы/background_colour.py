import random
import time

from PyQt5.QtCore import QThread


class ColourOnBackground(QThread):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.status = random.randint(1, 6)

        dictionary_of_values = {
            1: (255, 0, random.randint(1, 254)),
            2: (random.randint(1, 254), 0, 255),
            3: (0, random.randint(1, 254), 255),
            4: (0, 255, random.randint(1, 254)),
            5: (random.randint(1, 254), 255, 0),
            6: (255, random.randint(1, 254), 0)
        }

        self.red, self.green, self.blue = dictionary_of_values[self.status]

    def run(self):
        while True:
            if self.status == 1:
                self.blue += 1

                if self.blue == 255:
                    self.status = 2

            elif self.status == 2:
                self.red -= 1

                if self.red == 0:
                    self.status = 3

            elif self.status == 3:
                self.green += 1

                if self.green == 255:
                    self.status = 4

            elif self.status == 4:
                self.blue -= 1

                if self.blue == 0:
                    self.status = 5

            elif self.status == 5:
                self.red += 1

                if self.red == 255:
                    self.status = 6

            elif self.status == 6:
                self.green -= 1

                if self.green == 0:
                    self.status = 1

            try:
                self.main_window.update_colour.emit()

            except RuntimeError:
                pass

            time.sleep(0.05)
