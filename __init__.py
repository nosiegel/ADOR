# import the main window object (mw) from aqt
from anki.cards import Card
from aqt import mw, deckchooser
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
from PyQt6 import QtWidgets, QtCore
from aqt import *
import math

from anki import *


def open_dayoff_dialog(deck_id=None):
    dialog = DayOffDialog(
        aqt.mw, deck_id=deck_id
    )
    dialog.exec()

def on_deck_browser_will_show_options_menu(menu, deck_id):
    action = menu.addAction("Take The Day Off")
    action.triggered.connect(lambda _, did=deck_id: open_dayoff_dialog(did))

from aqt.gui_hooks import deck_browser_will_show_options_menu
deck_browser_will_show_options_menu.append(on_deck_browser_will_show_options_menu)

class DayOffDialog(QDialog):

    def __init__(
        self,
        mw: "AnkiQt",
        deck_id: Optional[int] = None,
    ):
        self.deck_id = deck_id
        QDialog.__init__(self, parent=mw)
        self.mw = mw
        self.setWindowTitle(
            "Take the Day Off"
        )
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.deckChooser = deckchooser.DeckChooser(self.mw, self.ui.DeckChooser)
        if deck_id is not None:
            if hasattr(self.deckChooser, 'selected_deck_id'): # Anki >= 2.1.45
                self.deckChooser.selected_deck_id = deck_id
            else:
                deck_name = self.mw.col.decks.nameOrNone(deck_id)
                if deck_name:
                    self.deckChooser.setDeckName(deck_name)
    def accept(self) -> None:
        off = self.ui.DaysOff.value()
        into = self.ui.DaysInto.value()
        algo = self.ui.Alogrithm.currentIndex()
        self.deck_id = self.deckChooser.selectedId()
        self.reschedule(self.deck_id, off, into, algo)
        self.deckChooser.cleanup()
        return super().accept()
    def reject(self) -> None:
        return super().reject()
    
    def reschedule(self, did: int, off: int, into: int, algo: int):

        deckChildren = [
        childDeck[1] for childDeck in self.mw.col.decks.children(did)
        ]
        deckChildren.append(did)
        childrenDIDs = "(" + ", ".join(str(did) for did in deckChildren) + ")"

        #showInfo(f"{childrenDIDs} ")

        dueToday=mw.col.find_cards(f"prop:due<{0+off} -is:learn")
        count = 0
        cards:list[Card] = list()

        for cardID in dueToday:
            card = mw.col.get_card(cardID)
            #there has to be a better way to do this
            if childrenDIDs.find(card.current_deck_id().__str__()) != -1:
                count+=1
                cards.append(card)
                
        cards.sort(key=dueSort, reverse=1)
        highestDue: int = cards.__getitem__(0).due
        
        cards.sort(key=ivlSort, reverse=1)
        

        cpd = math.floor(cards.__len__()/(into))

        for i in range(1+(off-1), into+off):
            #print(f"in outer loop with i = {i}")
            for j in range (0, cpd):
                #print(f"in inner loop with i = {i} j = {j}")            
                c: Card= cards.pop()
                c.due = highestDue - (off-1)
                #print(f"Current due date {c.due} new due date {c.due+i} ")
                c.due += i
                c.flush()

        for c in cards:
            #print(f"OVERFLOW Current due date {c.due} new due date {c.due+into+(off-1)} ")
            c.due += into+(off-1)
            c.flush()
        return
    

def ivlSort(e: Card):
  return e.ivl
def dueSort(e: Card):
  return e.due

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 297)
        self.layoutWidget = QtWidgets.QWidget(parent=Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 371, 271))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 5)
        self.label = QtWidgets.QLabel(parent=self.layoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 3)
        self.label_3 = QtWidgets.QLabel(parent=self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.Alogrithm = QtWidgets.QComboBox(parent=self.layoutWidget)
        self.Alogrithm.setEditable(False)
        self.Alogrithm.setObjectName("Alogrithm")
        self.Alogrithm.addItem("Default")
        self.gridLayout.addWidget(self.Alogrithm, 3, 1, 1, 4)
        self.label_2 = QtWidgets.QLabel(parent=self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 4)
        self.DaysInto = QtWidgets.QSpinBox(parent=self.layoutWidget)
        self.DaysInto.setObjectName("DaysInto")
        self.DaysInto.setMinimum(1)
        self.gridLayout.addWidget(self.DaysInto, 2, 4, 1, 1)
        self.DaysOff = QtWidgets.QSpinBox(parent=self.layoutWidget)
        self.DaysOff.setObjectName("DaysOff")
        self.DaysOff.setMinimum(1)
        self.gridLayout.addWidget(self.DaysOff, 1, 4, 1, 1)
        self.DeckChooser = QtWidgets.QWidget(parent=Dialog)
        self.DeckChooser.setObjectName("DeckChooser")
        self.gridLayout.addWidget(self.DeckChooser, 0, 0, 1, 5)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Take The Day Off"))
        self.label.setText(_translate("Dialog", "Days to Take Off"))
        self.label_2.setText(_translate("Dialog", "Days to Reschedule into"))
        self.label_3.setText(_translate("Dialog", "Algorithm"))
