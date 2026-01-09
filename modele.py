import numpy as np
from astropy.io import fits
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, median_filter
from PyQt6.QtGui import QImage, QPixmap
import os, cv2

class Modele() :

    def __init__(self, 
                 cheminImage : str = None,
                 sigmaClipping : float = 3.0,
                 fwhm : float = 3.0, 
                 threshold : float = 5.0,
                 rayon : int = 4,
                 flouGaussien : float = 2.0,
                 filtreEtoiles : int = 5) :
        
        # --- Chemin image chargée --- #

        self.__cheminImage = cheminImage

        if cheminImage != None :

            # Vérifications validité chemin image

            if not os.path.isfile(cheminImage) : # Fichier inexistant
                raise FileNotFoundError(f"Fichier introuvable : {cheminImage}")

            if not cheminImage.lower().endswith(('.fits', '.fit', '.fts')) : # Format incorrect
                raise ValueError("Le fichier à charger doit être un fichier FITS (.fits, .fit, .fts)")

            try : # Données image inexistantes
                with fits.open(cheminImage, memmap=False) as hdul :
                    if hdul[0].data is None :
                        raise ValueError("Le fichier FITS ne contient pas de données image")
            except Exception as e :
                raise ValueError(f"Le fichier à charger n'est pas un FITS valide : {e}")

        # --- Sigma clipping (pour estimation correcte fond et bruit de l'image) --- #

        self.__sigmaClipping = sigmaClipping
        
        if self.__sigmaClipping < 2.0 or self.__sigmaClipping > 5.0 : # Correction valeurs invalides
            self.__sigmaClipping = 3.0
        
        # --- Fwhm (taille approximative étoiles en pixels pour DAOStarFinder) --- #

        self.__fwhm = fwhm

        if self.__fwhm < 1.5 or self.__fwhm > 10.0 : # Correction valeurs invalides
            self.__fwhm = 3.0

        # --- Threshold (seuil détection pour DAOStarFinder) --- #

        self.__threshold = threshold

        if self.__threshold < 3.0 or self.__threshold > 10.0 : # Correction valeurs invalides
            self.__threshold = 5.0

        # --- Rayon (rayon étoiles pour masque étoiles adouci) --- #

        self.__rayon = rayon

        if self.__rayon < (1.5 * self.__fwhm) or self.__rayon > (2 * self.__fwhm) : # Correction valeurs invalides
            self.__rayon = int(1.5 * self.__fwhm)

        # --- Flou gaussien (taux adoucissement bords étoiles pour masque étoiles adouci) --- #

        self.__flouGaussien = flouGaussien

        if self.__flouGaussien < 0.0 or self.__flouGaussien > 3.0 : # Correction valeurs invalides
            self.__flouGaussien = 2.0
        
        # --- Filtre étoiles (pour image sans étoiles) --- #

        self.__filtreEtoiles = filtreEtoiles

        if self.__filtreEtoiles < (2 * self.__rayon + 1) or self.__filtreEtoiles % 2 == 0 : # Correction valeurs invalides
            self.__filtreEtoiles = (2 * self.__rayon + 1)

        # --- Initialisation images --- #

        self.genererImages()

    def genererImages(self) :

        if self.__cheminImage == None :

            self.__imageOriginale = None
            self.__masqueEtoilesAdouci = None
            self.__imageSansEtoiles = None
            self.__imageFinale = None
        
        else :

            # --- Image originale --- #

            with fits.open(self.__cheminImage, memmap=False) as hdul:
                self.__imageOriginale = hdul[0].data


            if self.__imageOriginale.ndim == 3:
                self.__imageOriginale = self.__imageOriginale[0] # Si image 3D : prendre première couche
                # self.__imageOriginale[self.__imageOriginale.shape[0]//2] pour prendre couche centrale
            elif self.__imageOriginale.ndim > 3:
                self.__imageOriginale = self.__imageOriginale[0, 0] # Si + de 3 dimensions, extraire une slice 2D

            mean, median, std = sigma_clipped_stats(self.__imageOriginale, sigma=self.__sigmaClipping) # Calcul statistiques images

            # --- Masque étoiles adouci --- #

            # Détection étoiles avec DAOStarFinder
            daofind = DAOStarFinder(fwhm=self.__fwhm, threshold=self.__threshold*std) 
            # Soustraction médiane par rapport à image pour améliorer détection étoiles
            # sources contient tableau avec coordonées étoiles détectées et leurs propriétés (magnitude, largeur, etc...)
            sources = daofind(self.__imageOriginale  - median)
            # Création image vide en fonction de image originale (dtype=int pour avoir masque binaire)
            mask = np.zeros_like(self.__imageOriginale, dtype=int)

            # Pour chaque étoiles détectée dans sources : création cercle dans masque à position de étoile
            # -- zip parcourt simultanément listes de coordonnées grâce aux "xcentroid" et "ycentroid" qui sont les coordonnées des centres des étoiles détectées --
            if sources is not None : # Évite plantage si aucune étoile détectée

                for x, y in zip(sources['xcentroid'], sources['ycentroid']):

                    y = int(y) ; x = int(x)

                    # Définition limites cercle en fonction du rayon (Utilisation max et min pour ne pas sortir des limites de l'image)
                    y_min = max(y-self.__rayon, 0) ; y_max = min(y+self.__rayon+1, mask.shape[0])
                    x_min = max(x-self.__rayon, 0) ; x_max = min(x+self.__rayon+1, mask.shape[1])
                    
                    # Génération cercle
                    yy, xx = np.ogrid[y_min:y_max, x_min:x_max] # Génération grille coordonnées
                    circle = (yy - y)**2 + (xx - x)**2 <= self.__rayon**2 # Équation cercle
                    mask[y_min:y_max, x_min:x_max][circle] = 1 # Mise à valeurs des pixels du masque qui sont dans cercle à 1 pour marquer position étoile

            # Création masque étoiles avec bords adoucis par flou gaussien (qui évite transitions brutales entre étoile et fond)
            self.__masqueEtoilesAdouci = gaussian_filter(mask.astype(float), sigma=self.__flouGaussien)

            # --- Image sans étoiles --- #

            # Utilisation filtre médian pour estimer fond et supprimer étoiles
            self.__imageSansEtoiles = median_filter(self.__imageOriginale, size=self.__filtreEtoiles)

            # --- Image finale --- #
        
            # Calcul image finale par interpolation
            # Image finale = (masque × image sans étoiles) + ((1 - masque) × image originale)
            # Là où masque = 1 (étoiles) : image sans étoiles
            # Là où masque = 0 (fond), image originale
            self.__imageFinale = (self.__masqueEtoilesAdouci * self.__imageSansEtoiles) + ((1 - self.__masqueEtoilesAdouci) * self.__imageOriginale)

    def reinitialiserModele(self) :

        # --- Réinitialisation paramètres --- #

        self.__sigmaClipping = 3.0
        self.__fwhm = 3.0
        self.__threshold = 5.0
        self.__rayon = int(1.5 * self.__fwhm)
        self.__flouGaussien = 2.0
        self.__filtreEtoiles = (2 * self.__rayon + 1)

        # --- Initialisation images --- #

        self.genererImages()

    def getCheminImage(self) :

        return self.__cheminImage
    
    def getSigmaClipping(self) :

        return self.__sigmaClipping
    
    def getFwhm(self) :

        return self.__fwhm
    
    def getThreshold(self) :

        return self.__threshold
    
    def getRayon(self) :

        return self.__rayon
    
    def getFlouGaussien(self) :

        return self.__flouGaussien
    
    def getFiltreEtoiles(self) :

        return self.__filtreEtoiles
    
    def getImageOriginale(self) :

        return self.__imageOriginale
    
    def getMasqueEtoilesAdouci(self) :

        return self.__masqueEtoilesAdouci
    
    def getImageSansEtoiles(self) :

        return self.__imageSansEtoiles
    
    def getImageFinale(self) :

        return self.__imageFinale
    
    def getPixmapImageOriginale(self) :

        return self.convertirImageEnPixmap(self.normaliserImage(self.__imageOriginale))
    
    def getPixmapMasqueEtoilesAdouci(self) :

        return self.convertirImageEnPixmap(self.normaliserImage(self.__masqueEtoilesAdouci))
    
    def getPixmapImageSansEtoiles(self) :

        return self.convertirImageEnPixmap(self.normaliserImage(self.__imageSansEtoiles))
    
    def getPixmapImageFinale(self) :

        return self.convertirImageEnPixmap(self.normaliserImage(self.__imageFinale))
    
    def setCheminImage(self, cheminImage : str) :

        # Vérifications validité chemin image

        if os.path.isfile(cheminImage) : # Fichier existant

            if cheminImage.lower().endswith(('.fits', '.fit', '.fts')) : # Format correct

                try : # Données image existantes

                    with fits.open(cheminImage, memmap=False) as hdul :
                        if not hdul[0].data is None : 
                            self.__cheminImage = cheminImage
                            self.genererImages() # Maj images

                except Exception as e :
                    raise ValueError(f"Le fichier à charger n'est pas un FITS valide : {e}")
                
    def setSigmaClipping(self, sigmaClipping : float) :

        if sigmaClipping >= 2.0 and sigmaClipping <= 5.0 : # Vérification validité
            self.__sigmaClipping = sigmaClipping
            self.genererImages() # Maj images

    def setFwhm(self, fwhm : float) :

        if fwhm >= 1.5 and fwhm <= 10.0 : # Vérification validité
            self.__fwhm = fwhm
            # Maj rayon si devenu invalide par rapport à modification fwhm
            if self.__rayon < (1.5 * self.__fwhm) or self.__rayon > (2 * self.__fwhm) :
                self.setRayon(int(1.5 * self.__fwhm))
            # Sinon : maj images directement
            else :
                self.genererImages() 

    def setThreshold(self, threshold : float) :

        if threshold >= 3.0 and threshold <= 10.0 : # Vérification validité
            self.__threshold = threshold
            self.genererImages() # Maj images

    def setRayon(self, rayon : int) :

        rayon = int(rayon) # Conversion rayon en entier (par sécurité)

        if rayon >= int(1.5 * self.__fwhm) and rayon <= int(2 * self.__fwhm) : # Vérification validité
            self.__rayon = rayon
            # Maj filtre étoiles si devenu invalide par rapport à modification rayon
            if self.__filtreEtoiles < (2 * self.__rayon + 1) :
                self.setFiltreEtoiles(2 * self.__rayon + 1)
            # Sinon : maj images directement
            else :
                self.genererImages() 

    def setFlouGaussien(self, flouGaussien : float) :

        if flouGaussien >= 0.0 and flouGaussien <= 3.0 : # Vérification validité
            self.__flouGaussien = flouGaussien
            self.genererImages() # Maj images

    def setFiltreEtoiles(self, filtreEtoiles : int) :

        if filtreEtoiles >= (2 * self.__rayon + 1) and filtreEtoiles % 2 == 1 : # Vérification validité
            self.__filtreEtoiles = filtreEtoiles
            self.genererImages() # Maj images

    def normaliserImage(self, image) :

        # Conversion valeurs image en float 64 bits (évite problèmes arrondis et divisions par 0)
        image = image.astype(np.float64) 

        # Si pixels tous de même couleur : retour tableau rempli de 0 de type np.uint8 (évite divisions par 0)
        if np.max(image) == np.min(image) : return np.zeros_like(image, dtype=np.uint8)

        # Sinon : retour image normalisée
        return ((image - np.min(image)) / (np.max(image) - np.min(image)) * 255).astype(np.uint8)
    
    def convertirImageEnPixmap(self, image : np.uint8) :

        if image.ndim == 2:  # Image en niveaux de gris

            height, width = image.shape
            bytes_per_line = width
            qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)

        elif image.ndim == 3 and image.shape[2] == 3:  # RGB

            height, width, channels = image.shape
            bytes_per_line = 3 * width
            qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        else:

            raise ValueError("Format numpy non supporté pour QImage")
        
        return QPixmap.fromImage(qimage)

    def enregistrerImageOriginale(self, cheminImage : str) :

        if not cheminImage.lower().endswith(".png") : raise ValueError("Le fichier de sortie doit être un PNG (.png)")
        cv2.imwrite(cheminImage, self.normaliserImage(self.__imageOriginale)) # Enregistrement image

    def enregistrerMasqueEtoilesAdouci(self, cheminImage : str) :

        if not cheminImage.lower().endswith(".png") : raise ValueError("Le fichier de sortie doit être un PNG (.png)")
        cv2.imwrite(cheminImage, self.normaliserImage(self.__masqueEtoilesAdouci)) # Enregistrement image

    def enregistrerImageSansEtoiles(self, cheminImage : str) :

        if not cheminImage.lower().endswith(".png") : raise ValueError("Le fichier de sortie doit être un PNG (.png)")
        cv2.imwrite(cheminImage, self.normaliserImage(self.__imageSansEtoiles)) # Enregistrement image

    def enregistrerImageFinale(self, cheminImage : str) :

        if not cheminImage.lower().endswith(".png") : raise ValueError("Le fichier de sortie doit être un PNG (.png)")
        cv2.imwrite(cheminImage, self.normaliserImage(self.__imageFinale)) # Enregistrement image