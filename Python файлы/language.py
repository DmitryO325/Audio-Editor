import csv

from PyQt5.QtWidgets import QInputDialog

language_is_changing = False


def change_language(window):
    with open('../Текстовые файлы/preferences.txt', 'r+', encoding='utf8') as preferences_file:
        language_now = preferences_file.readline()[10:-1]

        # отдельный виджет создал, чтобы текст кнопок "ОК" и "Отмена" изменялся в соответствии с выбранным языком

        dialog_window_with_language_settings = QInputDialog(window)
        dialog_window_with_language_settings.setFixedSize(250, 100)
        dialog_window_with_language_settings.setWindowTitle(find_necessary_text(500))
        dialog_window_with_language_settings.setLabelText(find_necessary_text(501))
        dialog_window_with_language_settings.setComboBoxItems((find_necessary_text(510),
                                                               find_necessary_text(511))
                                                              if language_now == 'russian'
                                                              else (find_necessary_text(511),
                                                                    find_necessary_text(510)))
        dialog_window_with_language_settings.setOkButtonText(find_necessary_text(520))
        dialog_window_with_language_settings.setCancelButtonText(find_necessary_text(521))

        if dialog_window_with_language_settings.exec():
            new_language = dialog_window_with_language_settings.textValue()

            preferences_file.seek(10)

            if new_language == find_necessary_text(510):
                preferences_file.write('russian\n')

            elif new_language == find_necessary_text(511):
                preferences_file.write('english\n')


def set_language_for_player(window):  # устанавливает язык в проигрывателе
    global reader, language

    if language_is_changing:
        change_language(window)

    with open('../CSV файлы/strings.csv', encoding='utf8') as csv_file:
        reader = list(csv.reader((line.replace('; ', ';') for line in csv_file), delimiter=';'))

    with open('../Текстовые файлы/preferences.txt', encoding='utf8') as preferences_file:
        language = preferences_file.readline()[10:-1]

    reader = list(filter(len, reader))

    window.setWindowTitle(f'{find_necessary_text(1)} - {find_necessary_text(10)}')

    dictionary_of_actions = {
        window.open_file_mn: 101,
        window.open_folder_mn: 102,
        window.rewind_back_mn: 210,
        window.rewind_forward_mn: 211,
        window.specified_time_mn: 212,
        window.play_mn: 220,
        window.pause_mn: 221,
        window.stop_mn: 222,
        window.previous_composition_mn: 230,
        window.next_composition_mn: 231,
        window.repeat_composition_mn: 240,
        window.volume_minus_mn: 310,
        window.volume_plus_mn: 311,
        window.volume_off_mn: 312,
        window.language_options_mn: 401,
        window.open_editor_window_mn: 601,
        window.add_file_mn: 710,
        window.delete_file_mn: 711,
        window.clear_playlist_mn: 720,
        window.save_playlist_mn: 721,
        window.open_playlist_mn: 722
    }

    dictionary_of_menu = {
        window.file_menu: 100,
        window.playback_menu: 200,
        window.speed_menu: 201,
        window.audio_menu: 300,
        window.settings_menu: 400,
        window.editor_menu: 600,
        window.playlist_menu: 700
    }

    for value, key in dictionary_of_actions.items():
        value.setText(find_necessary_text(key))

    for value, key in dictionary_of_menu.items():
        value.setTitle(find_necessary_text(key))

    window.playlist.setHorizontalHeaderLabels((find_necessary_text(800),
                                               find_necessary_text(801),
                                               find_necessary_text(802)))
    window.playlist.resizeColumnsToContents()

    window.audio_title.setText(find_necessary_text(window.number_of_phrase))


def set_language_for_editor(window):  # устанавливает язык в редакторе
    global reader, language

    if language_is_changing:
        change_language(window)

    with open('../CSV файлы/strings.csv', encoding='utf8') as csv_file:
        reader = list(csv.reader((line.replace('; ', ';') for line in csv_file), delimiter=';'))

    with open('../Текстовые файлы/preferences.txt', encoding='utf8') as preferences_file:
        language = preferences_file.readline()[10:-1]

    reader = list(filter(len, reader))

    window.setWindowTitle(f'{find_necessary_text(1)} - {find_necessary_text(11)}')

    window.edit_table.setHorizontalHeaderLabels((find_necessary_text(1700), find_necessary_text(1701)))
    window.edit_table.setVerticalHeaderLabels((find_necessary_text(1710), find_necessary_text(1711),
                                               find_necessary_text(1712), find_necessary_text(1713)))

    dictionary_of_labels_and_buttons_and_radio_buttons = {
        window.source_time_lbl: 1800,
        window.final_time_lbl: 1801,
        window.volume_lbl: 1810,
        window.new_link_label: 1820,

        window.crop_on_left: 1900,
        window.crop_on_right: 1901,
        window.select_link: 1910,
        window.select_file: 1911,
        window.save_audio: 1920
    }

    for value, key in dictionary_of_labels_and_buttons_and_radio_buttons.items():
        value.setText(find_necessary_text(key))


def find_necessary_text(text_id):  # для удобства
    return reader[reader.index(
        list(filter(lambda x: x[0] == str(text_id), reader))[0])][reader[0].index(language)]
