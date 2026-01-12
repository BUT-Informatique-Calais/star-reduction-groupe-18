# ----------------- #
# ---- Modules ---- #
# ----------------- #

import sys, os
from PyQt6.QtWidgets import QApplication, QWidget, QDockWidget, QStackedWidget, QHBoxLayout, QVBoxLayout, QMainWindow
from PyQt6.QtWidgets import QLabel, QPushButton, QSlider, QSpinBox, QFileDialog
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

# ----------------- #
# ---- Classes ---- #
# ----------------- #

class Vue(QMainWindow) :

    # --------------- #
    # --- Signaux --- #
    # --------------- #

    # --- Barre de menu --- #

    # -- Fichier
    chargementFichier : pyqtSignal = pyqtSignal()
    enregistrementImages : pyqtSignal = pyqtSignal(str)

    # -- Options
    reinitialisationParametres : pyqtSignal = pyqtSignal()
    reinitialisationTout : pyqtSignal = pyqtSignal()

    # --- Section centrale --- #

    # -- Image originale
    enregistrementImageOriginale : pyqtSignal = pyqtSignal(str)
    modificationSigmaClipping : pyqtSignal = pyqtSignal(float)

    # -- Image finale
    enregistrementImageFinale : pyqtSignal = pyqtSignal(str)
    miseAJourImages : pyqtSignal = pyqtSignal()

    # --- Section masque étoiles adouci --- #

    enregistrementMasqueEtoilesAdouci : pyqtSignal = pyqtSignal(str)
    modificationFwhm : pyqtSignal = pyqtSignal(float)
    modificationThreshold : pyqtSignal = pyqtSignal(float)
    modificationRayon : pyqtSignal = pyqtSignal(int)
    modificationFlouGaussien : pyqtSignal = pyqtSignal(float)

    # --- Section image sans étoiles --- #
    enregistrementImageSansEtoiles : pyqtSignal = pyqtSignal(str)
    modificationFiltreEtoiles : pyqtSignal = pyqtSignal(int)

    # ------------------ #
    # ---- Méthodes ---- #
    # ------------------ #

    def __init__(self) :

        super().__init__()

        # ----------------- #
        # --- Structure --- #
        # ----------------- #

        # --- Barre de menu --- #

        # Initialisation
        barreMenu = self.menuBar()

        # Initialisation menus
        self.menuFichier = barreMenu.addMenu("&Fichier")
        menuOptions = barreMenu.addMenu("&Options")

        # Initialisation sous-menus

        # -- Fichier
        actionChargerFichier = QAction("Charger un fichier FIT", self)
        self.actionEnregistrerImages = QAction("Enregistrer toutes les images", self)

        # -- Options
        actionReinitialiserParametres = QAction("Réinitialiser les paramètres d'images", self)
        actionReinitialiserTout = QAction("Réinitialiser tout", self)

        # Placement sous-menus

        # -- Fichier
        self.menuFichier.addAction(actionChargerFichier)

        # -- Options
        menuOptions.addAction(actionReinitialiserParametres)
        menuOptions.addAction(actionReinitialiserTout)
        
        # --- Section centrale --- #

        # Initialisation
        sectionCentrale = QWidget()
        sectionCentrale.setMaximumSize(500,700)
        sectionCentraleLayout = QVBoxLayout()
        sectionCentrale.setLayout(sectionCentraleLayout)

        # Initialisation éléments

        # -- Image originale
        intituleImageOriginale = QLabel("Image originale")
        self.imageOriginale = QLabel()
        boutonEnregistrementImageOriginale = QPushButton("Enregistrer")
        
        sigmaClippingSliderLabel = QLabel("Sigma Clipping")
        self.sigmaClippingSlider = QSlider(Qt.Orientation.Horizontal)
        self.sigmaClippingSlider.setMinimum(20)
        self.sigmaClippingSlider.setMaximum(50)
        self.sigmaClippingSlider.setValue(30)

        # -- Image finale
        intituleImageFinale = QLabel("Image finale")
        self.imageFinale = QLabel()
        boutonEnregistrementImageFinale = QPushButton("Enregistrer")
        boutonMiseAJourImages = QPushButton("Mettre à jour les images")

        # -- Aucun fichier chargé
        self.messageChargement = QLabel("Veuillez charger un fichier FIT.")

        # Placement éléments

        # -- Image originale
        intituleImageOriginale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageOriginale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sigmaClippingSliderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sectionCentraleLayout.addWidget(intituleImageOriginale)
        sectionCentraleLayout.addWidget(self.imageOriginale)
        sectionCentraleLayout.addWidget(boutonEnregistrementImageOriginale)
        sectionCentraleLayout.addWidget(sigmaClippingSliderLabel)
        sectionCentraleLayout.addWidget(self.sigmaClippingSlider)

        # -- Image finale
        intituleImageFinale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageFinale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sectionCentraleLayout.addWidget(intituleImageFinale)
        sectionCentraleLayout.addWidget(self.imageFinale)
        sectionCentraleLayout.addWidget(boutonEnregistrementImageFinale)
        sectionCentraleLayout.addWidget(boutonMiseAJourImages)
        sectionCentraleLayout.addStretch()

        # -- Aucun fichier chargé
        self.messageChargement.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Placement dans fenêtre
        self.widgetCentral = QStackedWidget()
        self.widgetCentral.addWidget(self.messageChargement)
        self.widgetCentral.addWidget(sectionCentrale)
        self.widgetCentral.setCurrentIndex(0)
        
        widgetAlignement = QWidget() # Morceau de code pour centrer la section centrale dans la fenêtre
        layoutAlignement = QVBoxLayout()
        layoutAlignement.addStretch()
        layoutAlignement.addWidget(self.widgetCentral, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutAlignement.addStretch()
        widgetAlignement.setLayout(layoutAlignement)
        self.setCentralWidget(widgetAlignement)

        # --- Section masque étoiles adouci --- #

        # Initialisation
        sectionMasqueEtoilesAdouci = QWidget()
        sectionMasqueEtoilesAdouci.setMaximumWidth(500)
        sectionMasqueEtoilesAdouciLayout = QVBoxLayout()
        sectionMasqueEtoilesAdouci.setLayout(sectionMasqueEtoilesAdouciLayout)

        # Initialisation éléments
        intituleMasqueEtoilesAdouci = QLabel("Masque d'étoiles adouci")
        self.masqueEtoilesAdouci = QLabel()
        boutonEnregistrementMasqueEtoilesAdouci = QPushButton("Enregistrer")

        fwhmSliderLabel = QLabel("fwhm")
        self.fwhmSlider = QSlider(Qt.Orientation.Horizontal)
        self.fwhmSlider.setMinimum(15)
        self.fwhmSlider.setMaximum(100)
        self.fwhmSlider.setValue(30)

        thresholdSliderLabel = QLabel("Threshold")
        self.thresholdSlider = QSlider(Qt.Orientation.Horizontal)
        self.thresholdSlider.setMinimum(30)
        self.thresholdSlider.setMaximum(100)
        self.thresholdSlider.setValue(50)

        rayonSliderLabel = QLabel("Rayon étoiles")
        self.rayonSlider = QSlider(Qt.Orientation.Horizontal)
        self.rayonSlider.setMinimum(4)
        self.rayonSlider.setMaximum(6)
        self.rayonSlider.setValue(4)

        flouGaussienSliderLabel = QLabel("Flou gaussien")
        self.flouGaussienSlider = QSlider(Qt.Orientation.Horizontal)
        self.flouGaussienSlider.setMinimum(0)
        self.flouGaussienSlider.setMaximum(30)
        self.flouGaussienSlider.setValue(20)

        # Placement éléments
        intituleMasqueEtoilesAdouci.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.masqueEtoilesAdouci.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fwhmSliderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thresholdSliderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rayonSliderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flouGaussienSliderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sectionMasqueEtoilesAdouciLayout.addWidget(intituleMasqueEtoilesAdouci)
        sectionMasqueEtoilesAdouciLayout.addWidget(self.masqueEtoilesAdouci)
        sectionMasqueEtoilesAdouciLayout.addWidget(boutonEnregistrementMasqueEtoilesAdouci)
        sectionMasqueEtoilesAdouciLayout.addWidget(fwhmSliderLabel)
        sectionMasqueEtoilesAdouciLayout.addWidget(self.fwhmSlider)
        sectionMasqueEtoilesAdouciLayout.addWidget(thresholdSliderLabel)
        sectionMasqueEtoilesAdouciLayout.addWidget(self.thresholdSlider)
        sectionMasqueEtoilesAdouciLayout.addWidget(rayonSliderLabel)
        sectionMasqueEtoilesAdouciLayout.addWidget(self.rayonSlider)
        sectionMasqueEtoilesAdouciLayout.addWidget(flouGaussienSliderLabel)
        sectionMasqueEtoilesAdouciLayout.addWidget(self.flouGaussienSlider)
        sectionMasqueEtoilesAdouciLayout.addStretch()

        # Placement dans fenêtre
        self.dockMasqueEtoilesAdouci = QDockWidget("Masque d'étoiles adouci", self)
        self.dockMasqueEtoilesAdouci.setWidget(sectionMasqueEtoilesAdouci)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockMasqueEtoilesAdouci)
        self.dockMasqueEtoilesAdouci.hide()

        # --- Section image sans étoiles --- #

        # Initialisation
        sectionImageSansEtoiles = QWidget()
        sectionImageSansEtoiles.setMaximumWidth(500)
        sectionImageSansEtoilesLayout = QVBoxLayout()
        sectionImageSansEtoiles.setLayout(sectionImageSansEtoilesLayout)

        # Initialisation éléments
        intituleImageSansEtoiles = QLabel("Image sans étoiles")
        self.imageSansEtoiles = QLabel()
        boutonEnregistrementImageSansEtoiles = QPushButton("Enregistrer")

        filtreEtoilesSpinBoxLabel = QLabel("Filtre d'étoiles")
        self.filtreEtoilesSpinBox = QSpinBox()
        self.filtreEtoilesSpinBox.lineEdit().setReadOnly(True)
        self.filtreEtoilesSpinBox.setMinimum(9)
        self.filtreEtoilesSpinBox.setSingleStep(2)
        self.filtreEtoilesSpinBox.setValue(9)

        # Placement éléments
        intituleImageSansEtoiles.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageSansEtoiles.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filtreEtoilesSpinBoxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sectionImageSansEtoilesLayout.addWidget(intituleImageSansEtoiles)
        sectionImageSansEtoilesLayout.addWidget(self.imageSansEtoiles)
        sectionImageSansEtoilesLayout.addWidget(boutonEnregistrementImageSansEtoiles)
        sectionImageSansEtoilesLayout.addWidget(filtreEtoilesSpinBoxLabel)
        sectionImageSansEtoilesLayout.addWidget(self.filtreEtoilesSpinBox)
        sectionImageSansEtoilesLayout.addStretch()

        # Placement dans fenêtre
        self.dockImageSansEtoiles = QDockWidget("Image sans étoiles", self)
        self.dockImageSansEtoiles.setWidget(sectionImageSansEtoiles)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockImageSansEtoiles)
        self.dockImageSansEtoiles.hide()

        # --- Paramètres fenêtre --- #
        
        self.setMinimumSize(1500, 800)
        self.setWindowTitle("SAE Astrophoto - Interface graphique")
        self.setWindowIcon(QIcon(sys.path[0] + '/../icones/logo_but.png'))
        self.show()

        # ------------------ #
        # --- Évènements --- #
        # ------------------ #

        # --- Barre de menu --- #

        # -- Fichier
        actionChargerFichier.triggered.connect(self.chargerFichier)
        self.actionEnregistrerImages.triggered.connect(self.enregistrerImages)

        # -- Options
        actionReinitialiserParametres.triggered.connect(self.signalReinitialiserParametres)
        actionReinitialiserTout.triggered.connect(self.reinitialiserTout)

        # --- Section centrale --- #

        # -- Image originale
        boutonEnregistrementImageOriginale.clicked.connect(self.enregistrerImageOriginale)
        self.sigmaClippingSlider.valueChanged.connect(self.modifierSigmaClipping)

        # -- Image finale
        boutonEnregistrementImageFinale.clicked.connect(self.enregistrerImageFinale)
        boutonMiseAJourImages.clicked.connect(self.mettreAJourImages)

        # --- Section masque étoiles adouci --- #

        boutonEnregistrementMasqueEtoilesAdouci.clicked.connect(self.enregistrerMasqueEtoilesAdouci)
        self.fwhmSlider.valueChanged.connect(self.modifierFwhm)
        self.thresholdSlider.valueChanged.connect(self.modifierThreshold)
        self.rayonSlider.valueChanged.connect(self.modifierRayon)
        self.flouGaussienSlider.valueChanged.connect(self.modifierFlouGaussien)

        # --- Section image sans étoiles --- #

        boutonEnregistrementImageSansEtoiles.clicked.connect(self.enregistrerImageSansEtoiles)
        self.filtreEtoilesSpinBox.valueChanged.connect(self.modifierFiltreEtoiles)

    def viderFenetre(self) :

        # Maj images
        self.imageOriginale.clear()
        self.masqueEtoilesAdouci.clear()
        self.imageSansEtoiles.clear()
        self.imageFinale.clear()

        # Affichage sections
        self.widgetCentral.setCurrentIndex(0)
        self.dockMasqueEtoilesAdouci.hide()
        self.dockImageSansEtoiles.hide()
        self.menuFichier.removeAction(self.actionEnregistrerImages)

    def remplirFenetre(self, 
                       imageOriginale : QPixmap, 
                       masqueEtoilesAdouci : QPixmap, 
                       imageSansEtoiles : QPixmap, 
                       imageFinale : QPixmap) :
        
        # Maj images
        self.imageOriginale.setPixmap(imageOriginale.scaled(500, 400))
        self.masqueEtoilesAdouci.setPixmap(masqueEtoilesAdouci.scaled(500, 400))
        self.imageSansEtoiles.setPixmap(imageSansEtoiles.scaled(500, 400))
        self.imageFinale.setPixmap(imageFinale.scaled(500, 400))

        # Affichage sections
        self.widgetCentral.setCurrentIndex(1)
        self.dockMasqueEtoilesAdouci.show()
        self.dockImageSansEtoiles.show()
        self.menuFichier.addAction(self.actionEnregistrerImages)

    def setEtatChargement(self, enCours: bool):

        if enCours :
            self.statusBar().showMessage("Génération des images en cours...")
            self.setEnabled(False)
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        else :
            self.statusBar().clearMessage()
            self.setEnabled(True)
            QApplication.restoreOverrideCursor()

    def chargerFichier(self) : 

        self.chargementFichier.emit()

    def enregistrerImages(self) :

        self.enregistrementImages.emit(QFileDialog.getExistingDirectory(None, "Choisir un dossier de sauvegarde"))

    def reinitialiserParametres(self) :

        # --- Section centrale --- #

        # -- Image originale
        self.sigmaClippingSlider.setValue(30)

        # --- Section masque étoiles adouci --- #

        self.fwhmSlider.setValue(30)
        self.thresholdSlider.setValue(50)
        self.rayonSlider.setMinimum(4)
        self.rayonSlider.setMaximum(6)
        self.rayonSlider.setValue(4)
        self.flouGaussienSlider.setValue(20)

        # --- Section image sans étoiles --- #

        self.filtreEtoilesSpinBox.setMinimum(9)
        self.filtreEtoilesSpinBox.setValue(9)

    def signalReinitialiserParametres(self) :

        self.reinitialisationParametres.emit()

    def reinitialiserTout(self) :

        self.reinitialisationTout.emit()

    def enregistrerImageOriginale(self) :

        self.enregistrementImageOriginale.emit(QFileDialog.getSaveFileName(None, "Sauvegarde image", None, "Fichiers PNG (*.png)")[0])

    def enregistrerMasqueEtoilesAdouci(self) :

        self.enregistrementMasqueEtoilesAdouci.emit(QFileDialog.getSaveFileName(None, "Sauvegarde image", None, "Fichiers PNG (*.png)")[0])

    def enregistrerImageSansEtoiles(self) :

        self.enregistrementImageSansEtoiles.emit(QFileDialog.getSaveFileName(None, "Sauvegarde image", None, "Fichiers PNG (*.png)")[0])

    def enregistrerImageFinale(self) :

        self.enregistrementImageFinale.emit(QFileDialog.getSaveFileName(None, "Sauvegarde image", None, "Fichiers PNG (*.png)")[0])

    def mettreAJourImages(self) :

        self.miseAJourImages.emit()

    def modifierSigmaClipping(self) :

        self.modificationSigmaClipping.emit(self.sigmaClippingSlider.value() * 0.1)

    def modifierFwhm(self) :

        # Maj rayon
        self.rayonSlider.setMinimum(int(1.5 * self.fwhmSlider.value() * 0.1))
        self.rayonSlider.setMaximum(int(2.0 * self.fwhmSlider.value() * 0.1))

        if (self.rayonSlider.value() < int(1.5 * self.fwhmSlider.value() * 0.1)
            or self.rayonSlider.value() > int(2.0 * self.fwhmSlider.value() * 0.1)):
            self.rayonSlider.setValue(int(1.5 * self.fwhmSlider.value() * 0.1))

        # Émission signal
        self.modificationFwhm.emit(self.fwhmSlider.value() * 0.1)

    def modifierThreshold(self) :

        self.modificationThreshold.emit(self.thresholdSlider.value() * 0.1)

    def modifierRayon(self) :

        # Maj filtre étoiles
        self.filtreEtoilesSpinBox.setMinimum(2 * self.rayonSlider.value() + 1)

        if self.filtreEtoilesSpinBox.value() < (2 * self.rayonSlider.value() + 1) :
            self.filtreEtoilesSpinBox.setValue(2 * self.rayonSlider.value() + 1)

        # Émission signal
        self.modificationRayon.emit(self.rayonSlider.value())

    def modifierFlouGaussien(self) :

        self.modificationFlouGaussien.emit(self.flouGaussienSlider.value() * 0.1)

    def modifierFiltreEtoiles(self) :

        self.modificationFiltreEtoiles.emit(self.filtreEtoilesSpinBox.value())

# -------------- #
# ---- Main ---- #
# -------------- #
        
if __name__ == "__main__":

    app = QApplication(sys.argv)
    fenetre = Vue()
    sys.exit(app.exec())