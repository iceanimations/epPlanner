'''
Created on Oct 29, 2015

@author: qurban.ali
'''
import sip
sip.setapi('QString', 2)
import sys
sys.path.append('R:/Python_Scripts/plugins/utilities')
sys.path.append('R:/Python_Scripts/plugins')
from src import ui
from PyQt4.QtGui import QApplication, QStyleFactory

if __name__ == '__main__':
    #somethign
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('plastique'))
    win = ui.UI()
    win.show()
    sys.exit(app.exec_())
    'don\'t do this'
