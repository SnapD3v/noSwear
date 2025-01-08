import logging
import sys
from typing import Optional

from colorama import init, Fore, Style


class ColorLogger:
    """
    Класс для создания логгера.
    """

    def __init__(self, name: str = __name__, level: int = logging.DEBUG, log_file: Optional[str] = None):
        """
        :param name: Имя логгера (по умолчанию берётся имя модуля).
        :param level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        :param log_file: Путь к файлу лога (если требуется запись в файл).
        """
        self.name = name
        self.level = level
        self.log_file = log_file
        self.logger = logging.getLogger(self.name)
        self._configure_logger()

    def _configure_logger(self) -> None:
        """
        Очищает предыдущие хендлеры, устанавливает уровень логирования
        и настраивает форматирование для консоли и (опционально) файла.
        """
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.setLevel(self.level)

        init(autoreset=True)

        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)

        if sys.version_info >= (3, 7):
            sys.stdout.reconfigure(encoding="utf-8")
        else:
            sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.ColoredFormatter())
        self.logger.addHandler(console_handler)

        if self.log_file:
            file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
            file_handler.setFormatter(self._default_formatter())
            self.logger.addHandler(file_handler)

    class ColoredFormatter(logging.Formatter):
        """
        Внутренний класс для цветного форматирования лога в консоли.
        """
        COLORS = {
            logging.DEBUG: Fore.CYAN,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.RED + Style.BRIGHT,
        }

        debug_info = "%(filename)s:%(lineno)d - %(funcName)s()"
        default_fmt = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                + f"[{debug_info}] - %(message)s"
        )

        def format(self, record: logging.LogRecord) -> str:
            """
            Перегрузка метода format для добавления цвета к сообщениям
            только на время вывода в консоль.
            """
            original_msg = record.msg

            try:
                color = self.COLORS.get(record.levelno, "")
                record.msg = color + str(original_msg) + Style.RESET_ALL
                formatter = logging.Formatter(self.default_fmt)
                return formatter.format(record)
            finally:
                record.msg = original_msg

    @staticmethod
    def _default_formatter() -> logging.Formatter:
        """
        Форматтер для записи лога в файл (без цветных символов).
        """
        debug_info = "%(filename)s:%(lineno)d - %(funcName)s()"
        default_fmt = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                + f"[{debug_info}] - %(message)s"
        )
        return logging.Formatter(default_fmt)

    def get_logger(self) -> logging.Logger:
        """
        Возвращает настроенный логгер.
        """
        return self.logger
