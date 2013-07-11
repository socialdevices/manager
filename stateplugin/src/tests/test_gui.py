#!/usr/bin/python
 
import sys
 
import PySide
from PySide.QtGui import QApplication
from PySide.QtGui import QMessageBox
from PySide.QtGui import QLabel
from PySide.QtGui import QPushButton
from PySide.QtGui import QWidget
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QHBoxLayout

def foo(parent):

    vbox = QHBoxLayout()

    vbox.addWidget( QLabel('this is the label of component', parent) )
    vbox.addWidget( QPushButton(parent, 'button') )

    return vbox
 
# Create the application object
app = QApplication(sys.argv)
 
# Create a simple dialog box
mainw = QWidget(sys.argv)
mainw.resize(250,150)
mainw.setWindowTitle('Mainview (plugins)')
mainlayout = QVBoxLayout()
mainlayout.addLayout( foo(mainw) )

mainw.setLayout( mainlayout )
mainw.show()
sys.exit(app.exec_())


