import os
from PySide2 import QtWidgets, QtCore, QtGui

from image import CustomImage

class Worker(QtCore.QObject):
    finished = QtCore.Signal() #on crée le signal finished
    image_converted = QtCore.Signal(object, bool)
     #on cree le signal qui va envoyer des infos : - object car on va envoyer un list widget
     #                                             - bool, car on va envoyer True ou False pour l'attribut processed

    def __init__(self, images_to_convert, quality, size, folder):
        super().__init__()
        
        self.images_to_convert = images_to_convert
        self.quality = quality
        self.size = size
        self.folder = folder
        self.runs = True #pour stoper le worker lors d'un click sur annuler dans la boite dialog de convertion def abord()

    def convert_worker_images(self):                 
        for image_lw_item in self.images_to_convert:                      
            if not image_lw_item.processed and self.runs:                                               
                image = CustomImage(image_lw_item.text(), self.folder)                     
                success = image.reduce_image(self.size, self.quality) #renvoi True or False, voir class CustomImage
                self.image_converted.emit(image_lw_item, success)

        self.finished.emit() # emet le signal finished, que MainWindow va pouvoir récuperer    
        
                
class MainWindow(QtWidgets.QWidget):
    def __init__(self, ctx):
        super(MainWindow, self).__init__()
        self.ctx = ctx
        self.setWindowTitle("PyConverter")
        self.setupUi()            

    def setupUi(self):
        self.createWidgets()
        self.modifyWidgets()
        self.createLayout()
        self.addWidgetsToLayouts()
        self.setup_connections()

    def createWidgets(self):
        self.lbl_quality = QtWidgets.QLabel("Quality: ")
        self.spn_quality = QtWidgets.QSpinBox()
        self.lbl_size = QtWidgets.QLabel("Size: ")
        self.spn_size = QtWidgets.QSpinBox()
        self.lbl_dossierOut = QtWidgets.QLabel("Out Folder :")
        self.le_dossierOut = QtWidgets.QLineEdit()
        self.lw_files = QtWidgets.QListWidget()
        self.btn_convert = QtWidgets.QPushButton("Convert")
        self.lbl_dropInfo = QtWidgets.QLabel("^ Drop image in the interface")

    def modifyWidgets(self):
        #Feuille de style
        #chemin = r"C:\Users\AP\PycharmProjects\pythonProject\formation_udemy\ressource"
        #with open(os.path.join(chemin, "style.css"), "r") as f:
        #    self.setStyleSheet(f.read())        

        #Alignment
        self.spn_quality.setAlignment(QtCore.Qt.AlignRight)
        self.spn_size.setAlignment(QtCore.Qt.AlignRight)
        self.le_dossierOut.setAlignment(QtCore.Qt.AlignRight)

        #Range
        self.spn_quality.setRange(1,100)
        self.spn_quality.setValue(75)
        self.spn_size.setRange(1,100)
        self.spn_size.setValue(50)

        #Divers
        self.le_dossierOut.setPlaceholderText("Type Out Folder here ... ")
        self.le_dossierOut.setText("reduced")
        self.lbl_dropInfo.setVisible(False)
        self.lw_files.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)

        #DragAndDrop
        self.setAcceptDrops(True)        

    def createLayout(self):
        self.layout = QtWidgets.QGridLayout(self)

    def addWidgetsToLayouts(self):
        self.layout.addWidget(self.lbl_quality, 0,0,1,1)
        self.layout.addWidget(self.lbl_size, 1,0,1,1)
        self.layout.addWidget(self.lbl_dossierOut, 2,0,1,1)
        self.layout.addWidget(self.spn_quality, 0,1,1,1)
        self.layout.addWidget(self.spn_size, 1,1,1,1)
        self.layout.addWidget(self.le_dossierOut, 2,1,1,1)
        self.layout.addWidget(self.lw_files, 3,0,1,2)
        self.layout.addWidget(self.lbl_dropInfo, 4,0,1,2)
        self.layout.addWidget(self.btn_convert, 5,0,1,2)

    def setup_connections(self):
        QtWidgets.QShortcut(QtGui.QKeySequence("Del"), self.lw_files, self.delete_selected_items)
        self.btn_convert.clicked.connect(self.convert_images)

    ### METHODES SPECIALES###

    @property
    def img_checked(self):
        chemin = os.path.dirname(__file__)
        return QtGui.QIcon(os.path.join(chemin, "checked.png"))
    
    @property
    def img_unchecked(self):
        chemin = os.path.dirname(__file__)
        return QtGui.QIcon(os.path.join(chemin, "unchecked.png"))

    def convert_images(self):
        
        quality = self.spn_quality.value()
        size = self.spn_size.value() / 100.0 #100.0 pour récuperer un nombre decimal
        folder = self.le_dossierOut.text()
                
        lw_items = [self.lw_files.item(i) for i in range(self.lw_files.count())]
        images_to_convert = [1 for lw_item in lw_items if not lw_item.processed]
        if not images_to_convert : #une liste vide est false. Si pas d'image à convertir, on rentre dans la boucle
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,"Error", "No image to convert")
            msg_box.exec_()
            #vérifie s'il y a des images a convertir dans le lw_items. 
            #si image a convertir != []  il y a des images à convertir
            return False
        
        self.thread = QtCore.QThread(self) # bien utiliser self.thread et non just thread. Sinon thread est détruit a la fin de la conversion
        self.worker = Worker(images_to_convert=lw_items, quality=quality,size=size, folder=folder)
        self.worker.moveToThread(self.thread)
        self.worker.image_converted.connect(self.image_converted)
        self.thread.started.connect(self.worker.convert_worker_images) 
        #On connecte le thread sur la méthode convert_images de worker. 
        #Quand on demarre le thread il lance la convertion des images. Le signal started correspond au "clicked" mais pour les threads
        self.worker.finished.connect(self.thread.quit) #quand le signal finished est emis par le worker, on quit le thread
        self.thread.start()

        self.prg_dialog = QtWidgets.QProgressDialog("Conversion des images", "Annuler...", 1, len(images_to_convert)) 
        #len(image_to_convert) contient le nombre d'image a convertir, car elle contient une liste de 1 si image a convertir
        self.prg_dialog.canceled.connect(self.abord) # canceled méthode du bouton annuler d'un dialog
        self.prg_dialog.show()
        
    def abord(self):
        self.thread.quit() #quit le thread, mais il faut l'arrêter également car worker toujours actif
        self.worker.runs = False #on modifie l'attribut runs de worker de True a False, pour quitter la boucle de def convert_worker_images(self)

    def image_converted(self, lw_item, success):
        if success:
            lw_item.setIcon(self.img_checked)
            lw_item.processed = True
            self.prg_dialog.setValue(self.prg_dialog.value() + 1)

    def delete_selected_items(self):
        for lw_item in self.lw_files.selectedItems():
            row = self.lw_files.row(lw_item)
            self.lw_files.takeItem(row)

    def dragEnterEvent(self, event):
        #Surcharge de dragEnterEvent en rajoutant notre label_dropInfo
        self.lbl_dropInfo.setVisible(True)
        event.accept()

    def dragLeaveEvent(self, event):
        #Surcharge de dragEnterEvent en rajoutant notre label_dropInfo
        self.lbl_dropInfo.setVisible(False)

    def dropEvent(self, event):
        #Surcharge de dropEvent pour rajouter les urls des images dans lw_files
        event.accept() 
        for url in event.mimeData().urls():
            #récupere le Path complet de l'image
            self.add_file(path=url.toLocalFile())            
        self.lbl_dropInfo.setVisible(False)        

    def add_file(self, path):
        items = [self.lw_files.item(i).text() for i in range(self.lw_files.count())]
        if path not in items:
            #lw_item = QtWidgets.QListWidgetItem(path.split("/")[-1])
            lw_item = QtWidgets.QListWidgetItem(path)
            lw_item.setIcon(self.img_unchecked)
            #lw_item.path = path
            lw_item.processed = False #on rajoute un attribut processed pour checked dans def convert_images()     
            self.lw_files.addItem(lw_item)                   

if __name__ == '__main__':
    app = QtWidgets.QApplication([])      
    window = MainWindow(ctx=app)
    window.resize(1920 / 4, 1200 / 2)
    window.show()
    app.exec_()