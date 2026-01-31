from gettext import gettext as _
from typing import Dict

import PyQt6.QtWidgets as QtW


class LanguageSelector(QtW.QComboBox):
    def __init__(self, languages: Dict[str, str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.addItem(_("Undefined"))
        for variable in languages.values():
            self.addItem(variable.capitalize())
