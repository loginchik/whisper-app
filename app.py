import sys
import os
import time
import datetime
import multiprocessing

import PyQt6.QtWidgets as QtW
from PyQt6 import QtCore
import pandas as pd
import whisper


multiprocessing.freeze_support()


class Transcriber:
    def __init__(self):
        self.model = None
        self.model_level = 'base'
        self.audio_path = None
        self.audio = None

    def load_model(self, model_name: str = None):
        if model_name is not None:
            self.model_level = model_name
        if self.model_level not in self.available_models():
            self.model_level = 'base'

        self.model = whisper.load_model(self.model_level)

    def load_audio(self):
        if self.audio_path is not None and os.path.exists(self.audio_path):
            self.audio = whisper.load_audio(self.audio_path)
        else:
            raise FileNotFoundError('Audio file not found')

    def transcribe_audio(self, language: str = None, fp16: bool = False, no_speech_threshold: float = 0.6, condition_on_previous_text: bool = True):
        if self.audio is None or self.model is None:
            raise AttributeError('Setup the basis first')

        result = self.model.transcribe(audio=self.audio,
                                       language=language,
                                       fp16=fp16,
                                       no_speech_threshold=no_speech_threshold,
                                       condition_on_previous_text=condition_on_previous_text)
        return result

    @staticmethod
    def what_is() -> str:
        return ('Whisper - это модель распознавания речи общего назначения. Она обучается на большом наборе данных '
                'с разнообразной аудиозаписью, а также является многозадачной моделью, которая может выполнять '
                'многоязычное распознавание речи, перевод речи и идентификацию языка.')

    @staticmethod
    def available_models() -> list[str]:
        return ['tiny', 'base', 'small', 'medium', 'large']

    @staticmethod
    def downloaded_models() -> list[str]:
        models_path = os.path.expanduser('~/.cache/whisper')
        available_models = [model.split('.')[0] for model in os.listdir(models_path) if
                            model.endswith('.pt')] if os.path.exists(models_path) else []
        return available_models

    @staticmethod
    def models_table_data() -> dict:
        downloaded_models = Transcriber.downloaded_models()
        available_models = Transcriber.available_models()
        models_table_data = {
            'Необходимо VRAM': ['~1 GB', '~1 GB', '~2 GB', '~5 GB', '~10 GB'],
            'Относительная скорость': ['~32x', '~16x', '~6x', '~2x', '1x'],
            'Пространство на жёстком диске': ['~76 MB', '~146 MB', '~484 MB', '~1.42 GB', '~2.88 GB'],
            'Уже загружена': tuple(map(lambda x: 'Да' if x in downloaded_models else 'Нет', available_models)),
        }
        return models_table_data

    @staticmethod
    def languages() -> dict:
        return {
            "en": "english",
            "zh": "chinese",
            "de": "german",
            "es": "spanish",
            "ru": "russian",
            "ko": "korean",
            "fr": "french",
            "ja": "japanese",
            "pt": "portuguese",
            "tr": "turkish",
            "pl": "polish",
            "ca": "catalan",
            "nl": "dutch",
            "ar": "arabic",
            "sv": "swedisdish",
            "it": "italian",
            "id": "indonesian",
            "hi": "hindi",
            "fi": "finnish",
            "vi": "vietnamese",
            "he": "hebrew",
            "uk": "ukrainian",
            "el": "greek",
            "ms": "malay",
            "cs": "czech",
            "ro": "romanian",
            "da": "danish",
            "hu": "hungarian",
            "ta": "tamil",
            "no": "norwegian",
            "th": "thai",
            "ur": "urdu",
            "hr": "croatian",
            "bg": "bulgarian",
            "lt": "lithuanian",
            "la": "latin",
            "mi": "maori",
            "ml": "malayalam",
            "cy": "welsh",
            "sk": "slovak",
            "te": "telugu",
            "fa": "persian",
            "lv": "latvian",
            "bn": "bengali",
            "sr": "serbian",
            "az": "azerbaijani",
            "sl": "slovenian",
            "kn": "kannada",
            "et": "estonian",
            "mk": "macedonian",
            "br": "breton",
            "eu": "basque",
            "is": "icelandic",
            "hy": "armenian",
            "ne": "nepali",
            "mn": "mongolian",
            "bs": "bosnian",
            "kk": "kazakh",
            "sq": "albanian",
            "sw": "swahili",
            "gl": "galician",
            "mr": "marathi",
            "pa": "punjabi",
            "si": "sinhala",
            "km": "khmer",
            "sn": "shona",
            "yo": "yoruba",
            "so": "somali",
            "af": "afrikaans",
            "oc": "occitan",
            "ka": "georgian",
            "be": "belarusian",
            "tg": "tajik",
            "sd": "sindhi",
            "gu": "gujarati",
            "am": "amharic",
            "yi": "yiddish",
            "lo": "lao",
            "uz": "uzbek",
            "fo": "faroese",
            "ht": "haitian creole",
            "ps": "pashto",
            "tk": "turkmen",
            "nn": "nynorsk",
            "mt": "maltese",
            "sa": "sanskrit",
            "lb": "luxembourgish",
            "my": "myanmar",
            "bo": "tibetan",
            "tl": "tagalog",
            "mg": "malagasy",
            "as": "assamese",
            "tt": "tatar",
            "haw": "hawaiian",
            "ln": "lingala",
            "ha": "hausa",
            "ba": "bashkir",
            "jw": "javanese",
            "su": "sundanese",
            "yue": "cantonese",
        }


class AppWindow(QtW.QMainWindow):
    def __init__(self):
        super().__init__()

        # Создаём транскрибер
        self.transcriber = Transcriber()

        # Настраиваем название окна и его размеры
        self.setWindowTitle('Whisper App')
        self.setMinimumWidth(600)
        self.setMaximumWidth(800)
        self.setMinimumHeight(500)
        self.setMaximumHeight(700)

        self.model_check_final = QtW.QCheckBox()
        self.audio_check_final = QtW.QCheckBox()
        self.language_selector = QtW.QComboBox()
        self.fp16_check = QtW.QCheckBox()
        self.no_speech_threshold = QtW.QDoubleSpinBox()
        self.condition_on_prev = QtW.QCheckBox()

        # Виджет для выбора типа модели
        model_block = self.choose_model_tab()
        # Виджет для настройки модели
        setup_block = self.set_parameters_tab()
        # Виджет для загрузки аудио
        audio_uploader = self.choose_audio_tab()
        # Виджет для запуска расшифровки
        run_tab_contents = self.run_tab()

        center = QtW.QTabWidget()
        center.addTab(model_block, 'Выбор и загрузка модели')
        center.addTab(audio_uploader, 'Выбор и загрузка аудио')
        center.addTab(setup_block, 'Настройка модели')
        center.addTab(run_tab_contents, 'Запуск')

        self.setCentralWidget(center)

    def choose_model_tab(self) -> QtW.QWidget:

        model_ready_label = QtW.QLabel('Модель готова')
        model_ready_label.setVisible(False)

        def model_ready_visibility():
            model_ready_label.setVisible(self.model_check_final.isChecked())
        self.model_check_final.stateChanged.connect(model_ready_visibility)

        # Текст о том, что такое модель и на что она влияет
        what_is_label = QtW.QLabel(self.transcriber.what_is())
        what_is_label.setWordWrap(True)
        # Таблица с доступными моделями
        self.models_table = QtW.QTableWidget()
        self.fill_models_table()

        # Выбор модели
        self.models_selector = QtW.QComboBox()
        for m in self.models_list_for_selector():
            self.models_selector.addItem(m)
        # Галочка о понимании, что всё зависнет
        understand_checkbox = QtW.QCheckBox()
        understand_label = QtW.QLabel('Я понимаю, что на время загрузки модели приложение зависнет')
        # Кнопка для загрузки модели
        download_button = QtW.QPushButton('Загрузить и выбрать модель')

        # Итоговая раскладка вкладки
        tab_layout = QtW.QVBoxLayout()
        tab_layout.addWidget(what_is_label)
        tab_layout.addWidget(self.models_table)
        # Выбор модели: лейбл и выбор
        choose_model_form = QtW.QHBoxLayout()
        choose_model_form.addWidget(QtW.QLabel('Выберите модель'))
        choose_model_form.addWidget(self.models_selector)
        choose_model_form.setContentsMargins(0, 0, 0, 0)
        choose_model_form_block = QtW.QWidget()
        choose_model_form_block.setLayout(choose_model_form)
        tab_layout.addWidget(choose_model_form_block)
        # Кнопка понимания: галочка и текст
        understand_form = QtW.QHBoxLayout()
        understand_form.addWidget(understand_checkbox)
        understand_form.addWidget(understand_label)
        understand_form.addStretch()
        understand_form.setContentsMargins(0, 0, 0, 0)
        understand_form_block = QtW.QWidget()
        understand_form_block.setLayout(understand_form)
        tab_layout.addWidget(understand_form_block)
        # Кнопка загрузки
        tab_layout.addWidget(download_button)
        tab_layout.addWidget(model_ready_label)
        # Поднимаем всё наверх
        tab_layout.addStretch()

        # Итоговое содержимое вкладки
        tab_contents = QtW.QWidget()
        tab_contents.setLayout(tab_layout)

        # Галочка активирует и деактивирует кнопку загрузки
        def get_understanding(check):
            download_button.setEnabled(check)
        understand_checkbox.stateChanged.connect(get_understanding)
        download_button.setEnabled(understand_checkbox.isChecked())

        # Отключаем галочку каждый раз, когда меняется выбор модели
        def disable_understanding():
            understand_checkbox.setChecked(False)
            check_result = self.transcriber.model is not None and self.transcriber.model_level == self.models_selector.currentText().replace('*', '').strip()
            self.model_check_final.setChecked(check_result)
        self.models_selector.currentTextChanged.connect(disable_understanding)

        # Функционал кнопки для загрузки модели
        def download_model():
            if understand_checkbox.isChecked():
                download_button.setEnabled(False)
                understand_checkbox.setEnabled(False)
                self.models_selector.setEnabled(False)

                time.sleep(.5)
                currently_selected = self.models_selector.currentText().replace('*', '').strip()
                self.transcriber.load_model(currently_selected)
                time.sleep(.5)

                download_button.setEnabled(True)
                understand_checkbox.setEnabled(True)
                understand_checkbox.setChecked(False)

                # Переделываем селектор, чтобы загруженная модель была со звёздочкой
                self.models_selector.clear()
                for m in self.models_list_for_selector():
                    self.models_selector.addItem(m)
                self.models_selector.setEnabled(True)
                # Обновляем таблицу
                self.fill_models_table()

        download_button.clicked.connect(download_model)

        return tab_contents

    def choose_audio_tab(self) -> QtW.QWidget:
        audio_prepared_complete = QtW.QLabel('Аудио готово')
        audio_prepared_complete.setVisible(False)

        def prepare_label_visibility():
            audio_prepared_complete.setVisible(self.audio_check_final.isChecked())
        self.audio_check_final.stateChanged.connect(prepare_label_visibility)

        file_path = QtW.QLineEdit()
        file_path.setEnabled(False)

        select_file_button = QtW.QPushButton('Выбрать файл')

        understand_checkbox = QtW.QCheckBox()
        understand_label = QtW.QLabel('Я понимаю, что в процессе обработки приложение зависнет')
        understand_layout = QtW.QHBoxLayout()
        understand_layout.addWidget(understand_checkbox)
        understand_layout.addWidget(understand_label)
        understand_layout.addStretch()
        understand_layout.setContentsMargins(0, 0, 0, 0)
        understand_block = QtW.QWidget()
        understand_block.setLayout(understand_layout)

        prepare_button = QtW.QPushButton('Подготовить аудио')

        tab_layout = QtW.QVBoxLayout()
        tab_layout.addWidget(file_path)
        tab_layout.addWidget(select_file_button)
        tab_layout.addWidget(understand_block)
        tab_layout.addWidget(prepare_button)
        tab_layout.addWidget(audio_prepared_complete)
        tab_layout.addStretch()

        tab_contents = QtW.QWidget()
        tab_contents.setLayout(tab_layout)

        def choose_audio_file():
            dialog = QtW.QFileDialog()
            dialog.setNameFilter('*.mp3 *.mp4 *m4a ·*webm *mpga *wav *mpe')
            success = dialog.exec()
            if success == 1:
                selected_filepath = dialog.selectedFiles()[0]
                file_path.setText(selected_filepath)
        select_file_button.clicked.connect(choose_audio_file)

        def audio_checkbox_switch():
            if file_path.text() == self.transcriber.audio_path and self.transcriber.audio is not None:
                self.audio_check_final.setChecked(True)
            else:
                self.audio_check_final.setChecked(False)

        def enable_prepare_button():
            if understand_checkbox.isChecked() and os.path.exists(file_path.text()):
                prepare_button.setEnabled(True)
            else:
                prepare_button.setEnabled(False)
            audio_checkbox_switch()

        file_path.textChanged.connect(enable_prepare_button)
        understand_checkbox.stateChanged.connect(enable_prepare_button)
        enable_prepare_button()

        def prepare_audio_file():
            self.transcriber.audio_path = file_path.text()
            time.sleep(.5)
            self.transcriber.load_audio()
            time.sleep(.5)
            audio_checkbox_switch()
        prepare_button.clicked.connect(prepare_audio_file)
        return tab_contents

    def set_parameters_tab(self) -> QtW.QWidget:
        # Выбор языка
        language_label = QtW.QLabel('Выберите язык')
        self.language_selector.addItem('Не определён')
        for lang in sorted(self.transcriber.languages().values()):
            self.language_selector.addItem(lang)

        # Fp16
        fp16_label = QtW.QLabel('FP16')

        # No speech threshold
        self.no_speech_threshold.setMinimum(0.0)
        self.no_speech_threshold.setMaximum(1.0)
        self.no_speech_threshold.setSingleStep(0.05)
        self.no_speech_threshold.setValue(0.6)
        no_speech_threshold_label = QtW.QLabel('No speech threshold')
        condition_on_prev_label = QtW.QLabel('Condition on previous text')
        self.condition_on_prev.setChecked(True)

        form_layout = QtW.QFormLayout()
        form_layout.addRow(language_label, self.language_selector)
        form_layout.addRow(fp16_label, self.fp16_check)
        form_layout.addRow(no_speech_threshold_label, self.no_speech_threshold)
        form_layout.addRow(condition_on_prev_label, self.condition_on_prev)
        form_layout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        form_contents = QtW.QWidget()
        form_contents.setLayout(form_layout)

        return form_contents

    def run_tab(self) -> QtW.QWidget:
        complete_label = QtW.QLabel('Проверьте папку с аудио, там должны появиться транскрипции')
        complete_label.setWordWrap(True)
        complete_label.setVisible(False)

        # Галочка, что модель готова
        model_block_layout = QtW.QHBoxLayout()
        model_block_layout.addWidget(self.model_check_final)
        self.model_check_final.setEnabled(False)
        model_block_layout.addWidget(QtW.QLabel('Модель загружена и установлена'))
        model_block_layout.setContentsMargins(0, 0, 0, 0)
        model_block_layout.addStretch()
        model_block = QtW.QWidget()
        model_block.setLayout(model_block_layout)

        # Галочка, что аудио готово
        audio_block_layout = QtW.QHBoxLayout()
        audio_block_layout.addWidget(self.audio_check_final)
        self.audio_check_final.setEnabled(False)
        audio_block_layout.addWidget(QtW.QLabel('Аудио загружено и предобработано'))
        audio_block_layout.setContentsMargins(0, 0, 0, 0)
        audio_block_layout.addStretch()
        audio_block = QtW.QWidget()
        audio_block.setLayout(audio_block_layout)

        # Галочка, что приложение зависнет
        understand_checkbox = QtW.QCheckBox()
        understand_label = QtW.QLabel('Я понимаю, что в процессе транскрибации приложение зависнет')
        understand_block_layout = QtW.QHBoxLayout()
        understand_block_layout.addWidget(understand_checkbox)
        understand_block_layout.addWidget(understand_label)
        understand_block_layout.addStretch()
        understand_block_layout.setContentsMargins(0, 0, 0, 0)
        understand_block = QtW.QWidget()
        understand_block.setLayout(understand_block_layout)

        # Поясняющий текст
        explanation_block = QtW.QLabel('Процесс может занимать от нескольких минут до нескольких часов')
        # Кнопка запуска
        start_button = QtW.QPushButton('Запустить')

        tab_contents = QtW.QVBoxLayout()
        tab_contents.addWidget(model_block)
        tab_contents.addWidget(audio_block)
        tab_contents.addWidget(explanation_block)
        tab_contents.addWidget(understand_block)
        tab_contents.addWidget(start_button)
        tab_contents.addWidget(complete_label)
        tab_contents.addStretch()

        tab_block = QtW.QWidget()
        tab_block.setLayout(tab_contents)

        def enable_start():
            if self.model_check_final.isChecked() and self.audio_check_final.isChecked() and understand_checkbox.isChecked():
                start_button.setEnabled(True)
                complete_label.setVisible(False)
            else:
                start_button.setEnabled(False)
        self.model_check_final.stateChanged.connect(enable_start)
        self.audio_check_final.stateChanged.connect(enable_start)
        understand_checkbox.stateChanged.connect(enable_start)
        enable_start()

        def start_transcribe():
            # Получаем настройку языка
            language_selected = self.language_selector.currentText()
            language_code = None
            for code, value in self.transcriber.languages().items():
                if value == language_selected:
                    language_code = code
                    break
            # Получаем настройку fp16
            fp16_value = self.fp16_check.isChecked()
            # Получаем настройку фильтрации речи
            try:
                no_speech_value = float(self.no_speech_threshold.text().replace(',', '.'))
            except ValueError:
                no_speech_value = 0.6
            # Получаем настройку промпта
            condition_prev = self.condition_on_prev.isChecked()

            # Транскрибируем
            result = self.transcriber.transcribe_audio(language=language_code, fp16=fp16_value,
                                                       no_speech_threshold=no_speech_value,
                                                       condition_on_previous_text=condition_prev)
            time.sleep(1)

            # Формируем название итогового файла
            filename_base = 'transcript_' + datetime.datetime.now().strftime('%Y%m%d%H%M')
            target_folder = os.path.join(os.path.split(self.transcriber.audio_path)[0], filename_base)
            os.makedirs(target_folder, exist_ok=True)

            full_filename = filename_base + '_full_text.txt'
            segments_filename = filename_base + '_segments.csv'
            segments_text_filename = filename_base + '_segments_text.txt'

            full_filepath = os.path.join(target_folder, full_filename)
            segments_filepath = os.path.join(target_folder, segments_filename)
            segments_text_filepath = os.path.join(target_folder, segments_text_filename)

            with open(full_filepath, 'w', encoding='utf-8', errors='replace') as f:
                f.write(result['text'])
            time.sleep(1)

            segments = pd.DataFrame(result['segments'])
            segments.to_csv(segments_filepath, index=False, encoding='utf-8', errors='replace')
            time.sleep(1)
            with open(segments_text_filepath, 'w', encoding='utf-8', errors='replace') as f:
                for seg in segments['text']:
                    f.write(seg + '\n')
            time.sleep(1)
            understand_checkbox.setChecked(False)
            complete_label.setVisible(True)
        start_button.clicked.connect(start_transcribe)

        return tab_block

    def models_list_for_selector(self):
        available = self.transcriber.available_models()
        downloaded = self.transcriber.downloaded_models()
        return tuple(map(lambda x: x + '*' if x in downloaded else x, available))

    def fill_models_table(self):
        self.models_table.clear()
        available_models = self.transcriber.available_models()
        models_table_data = self.transcriber.models_table_data()
        self.models_table.setColumnCount(len(models_table_data))
        self.models_table.setRowCount(len(available_models))
        self.models_table.setHorizontalHeaderLabels(list(models_table_data.keys()))
        self.models_table.setVerticalHeaderLabels(available_models)

        for col_i, col_data in enumerate(models_table_data.keys()):
            column = models_table_data[col_data]
            for cell_i, cell_data in enumerate(column):
                self.models_table.setItem(cell_i, col_i, QtW.QTableWidgetItem(cell_data))


def app_main():
    app = QtW.QApplication(sys.argv)
    window = AppWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    app_main()

