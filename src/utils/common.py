from os.path import sep
from os.path import isfile

from re import search

from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QPushButton

from automonkey import ALL_ACTIONS

from .constants import COORDS_REGEX

def clean_steps(steps: dict) -> dict:
    """Prepare steps for automonkey chain."""
    cleaned = {}
    for key, value in steps.items():
        if not isfile(value["target"]) and search(COORDS_REGEX, value["target"]):
            step = {value["action"]: tuple(map(int, value["target"].split(",")))}
        else:
            step = {value["action"]: value["target"]}
        for key2, value2 in value.items():
            if key2 not in ("", "skip", "action", "target") + ALL_ACTIONS and value2 not in ("", "action", "target") + ALL_ACTIONS:
                step[key2] = int(value2)
            elif key2 == "skip":
                step[key2] = eval(value2)
        cleaned[key] = step
    return cleaned

def clean_path(path: str) -> str:
    """clean_path by replacing all backslashes with standard os path separator
    Args:
        path (str): path to clean
    Returns:
        str: cleaned path
    """
    return path.replace("\\\\", sep).replace("\\", sep).replace("/", sep)

def filter_settings(layout: any, exception_widget: any, search_bar: any):
    for i in range(layout.count()):
        if isinstance(layout.itemAt(i).widget(), exception_widget):
            if isinstance(layout.itemAt(i).widget().setting_widget, QLineEdit):
                if search_bar.text().lower() in layout.itemAt(i).widget().setting_widget.objectName().lower():
                    layout.itemAt(i).widget().show()
                elif layout.itemAt(i).widget().setting_widget != search_bar:
                    layout.itemAt(i).widget().hide()
            if isinstance(layout.itemAt(i).widget().setting_widget, QComboBox):
                if search_bar.text().lower() in layout.itemAt(i).widget().setting_widget.objectName().lower():
                    layout.itemAt(i).widget().show()
                elif layout.itemAt(i).widget().setting_widget != search_bar:
                    layout.itemAt(i).widget().hide()
            if isinstance(layout.itemAt(i).widget().setting_label, QLabel):
                if search_bar.text().lower() in layout.itemAt(i).widget().setting_label.objectName().lower():
                    layout.itemAt(i).widget().show()
                elif layout.itemAt(i).widget().setting_label != search_bar:
                    layout.itemAt(i).widget().hide()
            if isinstance(layout.itemAt(i).widget().setting_widget, QPushButton):
                if search_bar.text().lower() in layout.itemAt(i).widget().setting_widget.objectName().lower():
                    layout.itemAt(i).widget().show()
                elif layout.itemAt(i).widget().setting_widget != search_bar:
                    layout.itemAt(i).widget().hide()
