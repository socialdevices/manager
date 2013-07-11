try:    import json
except: import simplejson as json

from urlparse import urlparse
import httplib, time

try:    from PySide import QtGui, QtCore
except: from PyQt4 import QtGui, QtCore


class Screen(QtGui.QWidget):
    
    show_url_photo = QtCore.Signal(str, QtCore.Qt.CaseSensitive)
        
    def __init__(self, orchestrator_connetion):
        
        QtGui.QWidget.__init__(self, None)
        self.setWindowTitle('Screen Interface')
        self.orchestrator_connetion = orchestrator_connetion
        self.photoWidget = None
        
        
    def showUrlPhoto(self, params):
        
        params = json.loads(params)
        photo_url = params.get('photo_url')

        self.showPhotoOnWidget(photo_url)
        self.setStyleSheet("QWidget { background-color: black }")
        self.showFullScreen()
        self.show()
        return 
    

    def closeEvent(self, event):        
        self.photoShown()

   
    def clearLayout(self,widget=None):
        if not widget:
            widget = self
        if widget.layout() is not None:
            old_layout = widget.layout()
            for i in reversed(range(old_layout.count())):
                old_layout.itemAt(i).widget().setParent(None)
        
        L = widget.layout()
        L.deleteLater()
        QtCore.QCoreApplication.sendPostedEvents(L, QtCore.QEvent.DeferredDelete)

  

    def photoShown(self):
        self.orchestrator_connetion.continue_qt()
        #self.clearLayout(self.photoWidget)
        self.photoWidget.close()
        self.close()
        

    def showPhotoOnWidget(self,uri):

        image_data = self.get_image_data(uri)
        
        pixmap = QtGui.QPixmap()
        photo_label = ClickLabel()
        
        qimg = QtGui.QImage.fromData(image_data)
        qimg = qimg.scaledToWidth(QtGui.QApplication.desktop().screenGeometry().right()-20)
        qimg = qimg.scaledToHeight(QtGui.QApplication.desktop().screenGeometry().bottom()-20)
        
                
        pixmap = QtGui.QPixmap.fromImage(qimg)
        photo_label.setPixmap(pixmap)        
        
        layout = QtGui.QVBoxLayout()
        
        
        self.photoWidget = QtGui.QWidget(parent=self)
        self.photoWidget.setWindowTitle('PhotoWidget')

        self.photoWidget.setLayout(layout)

        photo_label.clicked.connect(self.photoShown)
        layout.addWidget(photo_label)
        
        self.photoWidget.setStyleSheet("QWidget { background-color: black }")
        
        self.photoWidget.showFullScreen()
        self.photoWidget.show()
        
        return
    
 
        
    def get_image_data(self, image_uri):
        print("Fetching image: " +str(image_uri))
        uri = urlparse(str(image_uri))
        conn = httplib.HTTPConnection(uri.hostname)
        conn.request("GET", uri.path)
        r1 = conn.getresponse()
        image_data = r1.read()
        print("Image fetched!")
        return image_data            
        
        
        
class ClickLabel(QtGui.QLabel):

    clicked = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(ClickLabel, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        event.accept()
        self.clicked.emit()
        
        
        
        
        
        