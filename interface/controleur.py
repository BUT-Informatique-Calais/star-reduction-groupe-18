# ----------------- #
# ---- Modules ---- #
# ----------------- #

import sys
from modele import Modele
from vue import Vue
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtCore import QObject, QThread, pyqtSignal

# ----------------- #
# ---- Classes ---- #
# ----------------- #

class GenerateurImages(QObject) :

    imagesPretes : pyqtSignal() = pyqtSignal()

    def __init__(self, modele : Modele) :

        super().__init__()
        self.modele : Modele = modele

    def genererImages(self) :

        self.modele.genererImages()
        self.imagesPretes.emit()

class Controleur() :

    def __init__(self) :

        self.modele : Modele = Modele()
        self.vue : Vue = Vue()

        # --------------- #
        # --- Signaux --- #
        # --------------- #

        # --- Barre de menu --- #

        # -- Fichier
        self.vue.chargementFichier.connect(self.chargerFichier)
        self.vue.enregistrementImages.connect(self.enregistrerImages)

        # -- Options
        self.vue.reinitialisationParametres.connect(self.reinitialiserParametres)
        self.vue.reinitialisationTout.connect(self.reinitialiserTout)

        # --- Section centrale --- #

        # -- Image originale
        self.vue.enregistrementImageOriginale.connect(self.enregistrerImageOriginale)
        self.vue.modificationSigmaClipping.connect(self.modifierSigmaClipping)

        # -- Image finale
        self.vue.enregistrementImageFinale.connect(self.enregistrerImageFinale)
        self.vue.miseAJourImages.connect(self.mettreAJourImages)

        # --- Section masque étoiles adouci --- #

        self.vue.enregistrementMasqueEtoilesAdouci.connect(self.enregistrerMasqueEtoilesAdouci)
        self.vue.modificationFwhm.connect(self.modifierFwhm)
        self.vue.modificationThreshold.connect(self.modifierThreshold)
        self.vue.modificationRayon.connect(self.modifierRayon)
        self.vue.modificationFlouGaussien.connect(self.modifierFlouGaussien)

        # --- Section image sans étoiles --- #

        self.vue.enregistrementImageSansEtoiles.connect(self.enregistrerImageSansEtoiles)
        self.vue.modificationFiltreEtoiles.connect(self.modifierFiltreEtoiles)

    def chargerFichier(self) :

        fichierLu = QFileDialog.getOpenFileName(None, "Lecture fichier FITS", None, "Fichiers FITS (*.fits)")[0]

        if fichierLu != '' :

            self.modele.reinitialiserModele()
            self.modele.setCheminImage(fichierLu)

            self.vue.reinitialiserParametres()
            self.vue.remplirFenetre(self.modele.getPixmapImageOriginale(),
                                    self.modele.getPixmapMasqueEtoilesAdouci(),
                                    self.modele.getPixmapImageSansEtoiles(),
                                    self.modele.getPixmapImageFinale())
            
    def enregistrerImages(self, cheminDossier : str) :

        if cheminDossier != '' :

            self.modele.enregistrerImageOriginale(cheminDossier + "/original")
            self.modele.enregistrerMasqueEtoilesAdouci(cheminDossier + "/masque_etoiles")
            self.modele.enregistrerImageSansEtoiles(cheminDossier + "/sans_etoiles")
            self.modele.enregistrerImageFinale(cheminDossier + "/final")

    def reinitialiserParametres(self) :

        self.modele.reinitialiserModele()
        self.vue.reinitialiserParametres()

    def reinitialiserTout(self) :

        self.modele.reinitialiserModele()
        self.modele.setCheminImage(None)

        self.vue.reinitialiserParametres()
        self.vue.viderFenetre()

    def enregistrerImageOriginale(self, cheminImage : str) :

        if cheminImage != '' :

            self.modele.enregistrerImageOriginale(cheminImage)

    def enregistrerMasqueEtoilesAdouci(self, cheminImage : str) :

        if cheminImage != '' :

            self.modele.enregistrerMasqueEtoilesAdouci(cheminImage)

    def enregistrerImageSansEtoiles(self, cheminImage : str) :

        if cheminImage != '' :

            self.modele.enregistrerImageSansEtoiles(cheminImage)

    def enregistrerImageFinale(self, cheminImage : str) :

        if cheminImage != '' :

            self.modele.enregistrerImageFinale(cheminImage)

    def mettreAJourImages(self) :

        self.vue.setEtatChargement(True) # Blocage vue tant que la génération d'images n'est pas achevée

        self.threadGenerationImages : QThread = QThread()
        self.generateurImages : GenerateurImages = GenerateurImages(self.modele)
        self.generateurImages.moveToThread(self.threadGenerationImages)

        self.threadGenerationImages.started.connect(self.generateurImages.genererImages)
        self.generateurImages.imagesPretes.connect(self.terminerMiseAJourImages)
        self.generateurImages.imagesPretes.connect(self.threadGenerationImages.quit)
        self.generateurImages.imagesPretes.connect(self.generateurImages.deleteLater)
        self.threadGenerationImages.finished.connect(self.threadGenerationImages.deleteLater)

        self.threadGenerationImages.start() # Lancement processus génération images

    def terminerMiseAJourImages(self) : # Déclenché lorsque la génération d'images du modèle est terminée

        self.vue.remplirFenetre( # Mise à jour images dans vue
            self.modele.getPixmapImageOriginale(),
            self.modele.getPixmapMasqueEtoilesAdouci(),
            self.modele.getPixmapImageSansEtoiles(),
            self.modele.getPixmapImageFinale()
        )

        self.vue.setEtatChargement(False) # Déblocage vue

    def modifierSigmaClipping(self, valeur : float) :

        self.modele.setSigmaClipping(valeur)

    def modifierFwhm(self, valeur : float) :

        self.modele.setFwhm(valeur)

    def modifierThreshold(self, valeur : float) :

        self.modele.setThreshold(valeur)

    def modifierRayon(self, valeur : int) :

        self.modele.setRayon(valeur)

    def modifierFlouGaussien(self, valeur : float) :

        self.modele.setFlouGaussien(valeur)

    def modifierFiltreEtoiles(self, valeur : int) :

        self.modele.setFiltreEtoiles(valeur)
        
# -------------- #
# ---- Main ---- #
# -------------- #

if __name__ == "__main__":

    app = QApplication(sys.argv)
    controleur : Controleur = Controleur()
    sys.exit(app.exec())