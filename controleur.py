# ----------------- #
# ---- Modules ---- #
# ----------------- #

import sys
from modele import Modele
from vue import Vue
from PyQt6.QtWidgets import QApplication, QFileDialog

# ----------------- #
# ---- Classes ---- #
# ----------------- #

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

            self.modele.enregistrerImageOriginale(cheminDossier + "original.png")
            self.modele.enregistrerMasqueEtoilesAdouci(cheminDossier + "masque_etoiles.png")
            self.modele.enregistrerImageSansEtoiles(cheminDossier + "sans_etoiles.png")
            self.modele.enregistrerImageFinale(cheminDossier + "final.png")

    def reinitialiserParametres(self) :

        self.modele.reinitialiserModele()
        self.vue.reinitialiserParametres()

    def reinitialiserTout(self) :

        self.modele.reinitialiserModele()
        self.modele.setCheminImage(None)

        self.vue.reinitialiserParametres()
        self.vue.viderFenetre()

    def enregistrerImageOriginale(self, cheminImage : str) :

        self.modele.enregistrerImageOriginale(cheminImage)

    def enregistrerMasqueEtoilesAdouci(self, cheminImage : str) :

        self.modele.enregistrerMasqueEtoilesAdouci(cheminImage)

    def enregistrerImageSansEtoiles(self, cheminImage : str) :

        self.modele.enregistrerImageSansEtoiles(cheminImage)

    def enregistrerImageFinale(self, cheminImage : str) :

        self.modele.enregistrerImageFinale(cheminImage)

    def modifierSigmaClipping(self, valeur : float) :

        self.modele.setSigmaClipping(valeur)
        self.vue.remplirFenetre(self.modele.getPixmapImageOriginale(),
                                    self.modele.getPixmapMasqueEtoilesAdouci(),
                                    self.modele.getPixmapImageSansEtoiles(),
                                    self.modele.getPixmapImageFinale())

    def modifierFwhm(self, valeur : float) :

        self.modele.setFwhm(valeur)
        self.vue.remplirFenetre(self.modele.getPixmapImageOriginale(),
                                    self.modele.getPixmapMasqueEtoilesAdouci(),
                                    self.modele.getPixmapImageSansEtoiles(),
                                    self.modele.getPixmapImageFinale())

    def modifierThreshold(self, valeur : float) :

        self.modele.setThreshold(valeur)
        self.vue.remplirFenetre(self.modele.getPixmapImageOriginale(),
                                    self.modele.getPixmapMasqueEtoilesAdouci(),
                                    self.modele.getPixmapImageSansEtoiles(),
                                    self.modele.getPixmapImageFinale())

    def modifierRayon(self, valeur : int) :

        self.modele.setRayon(valeur)
        self.vue.remplirFenetre(self.modele.getPixmapImageOriginale(),
                                    self.modele.getPixmapMasqueEtoilesAdouci(),
                                    self.modele.getPixmapImageSansEtoiles(),
                                    self.modele.getPixmapImageFinale())

    def modifierFlouGaussien(self, valeur : float) :

        self.modele.setFlouGaussien(valeur)
        self.vue.remplirFenetre(self.modele.getPixmapImageOriginale(),
                                    self.modele.getPixmapMasqueEtoilesAdouci(),
                                    self.modele.getPixmapImageSansEtoiles(),
                                    self.modele.getPixmapImageFinale())

    def modifierFiltreEtoiles(self, valeur : int) :

        self.modele.setFiltreEtoiles(valeur)
        self.vue.remplirFenetre(self.modele.getPixmapImageOriginale(),
                                    self.modele.getPixmapMasqueEtoilesAdouci(),
                                    self.modele.getPixmapImageSansEtoiles(),
                                    self.modele.getPixmapImageFinale())
        
# -------------- #
# ---- Main ---- #
# -------------- #

if __name__ == "__main__":

    app = QApplication(sys.argv)
    controleur : Controleur = Controleur()
    sys.exit(app.exec())