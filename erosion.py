from astropy.io import fits
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

# Ouvrir et lire le fichier FITS
# FITS = Flexible Image Transport System, format standard en astronomie
fits_file = './examples/HorseHead.fits'
hdul = fits.open(fits_file)  # hdul = HDU List (liste des unités de données)

# Afficher les informations sur le fichier
hdul.info()

# Accéder aux données du HDU principal
# HDU = Header Data Unit, chaque HDU contient des données et des métadonnées
# hdul[0] = HDU primaire qui contient généralement l'image principale
data = hdul[0].data

# Accéder aux informations d'en-tête (métadonnées : taille, coordonnées, instrument, etc.)
header = hdul[0].header

# Gérer les images monochromes et couleur
# ndim = nombre de dimensions (2D = monochrome, 3D = couleur)
if data.ndim == 3: # Image couleur car 3 dimensions
    # Image couleur - besoin de transposer en (hauteur, largeur, canaux)
    # Les données FITS peuvent avoir les canaux de couleur en première dimension
    if data.shape[0] == 3:  # Si les canaux sont en premier: (3, hauteur, largeur)
        data = np.transpose(data, (1, 2, 0))  # Réorganise en (hauteur, largeur, canaux)
    # Si déjà (hauteur, largeur, 3), pas de changement nécessaire
    
    # Normaliser toute l'image à [0, 1] pour matplotlib
    # Les données FITS peuvent avoir des valeurs très élevées, on les ramène entre 0 et 1
    data_normalized = (data - data.min()) / (data.max() - data.min())
    
    # Sauvegarder les données comme image png (pas de cmap pour les images couleur)
    # plt.imsave attend des valeurs entre 0 et 1 pour les images couleur
    plt.imsave('./results/original.png', data_normalized) # donc on met data_normalized qui est le résultat d'un calcul qui sera forcément entre 0 et 1
    
    # Normaliser chaque canal séparément à [0, 255] pour OpenCV
    # OpenCV travaille avec des entiers 8 bits (0-255) contrairement à matplotlib
    image = np.zeros_like(data, dtype='uint8')  # uint8 = entiers non signés 8 bits
    for i in range(data.shape[2]):  # Pour chaque canal de couleur
        channel = data[:, :, i]
        # Normalisation canal par canal pour éviter la perte de contraste
        image[:, :, i] = ((channel - channel.min()) / (channel.max() - channel.min()) * 255).astype('uint8')
else:
    # Image monochrome (2D) - cas le plus fréquent en astronomie
    # cmap='gray' = palette de couleurs en niveaux de gris
    plt.imsave('./results/original.png', data, cmap='gray')

    # Convertir en uint8 pour OpenCV (de float vers entiers 0-255)
    # Cette conversion permet d'utiliser les fonctions de traitement d'image d'OpenCV
    image = ((data - data.min()) / (data.max() - data.min()) * 255).astype('uint8')
    # on remet le même calcul que "data_normalized" mais en le multipliant par 255 pour la conversion en uint8


# Définir un noyau pour l'érosion
# Le noyau 3x3 détermine la forme et la taille de l'opération morphologique
kernel = np.ones((3,3), np.uint8)  # Matrice 3x3 remplie de 1
# Effectuer l'érosion
# L'érosion réduit les zones blanches, supprime le bruit et les petits objets
# iterations=1 signifie qu'on applique l'érosion une seule fois
eroded_image = cv.erode(image, kernel, iterations=1)  # 1 itération = une passe

# Sauvegarder l'image érodée
# cv.imwrite sauvegarde directement en format image standard
cv.imwrite('./results/eroded.png', eroded_image)

# Fermer le fichier FITS pour libérer la mémoire
# Bonne pratique pour éviter les fuites mémoire avec les gros fichiers astronomiques
hdul.close()



# TEST DU CODE : 
# Filename: ./examples/HorseHead.fits
# No.    Name      Ver    Type      Cards   Dimensions   Format
# 0  PRIMARY       1 PrimaryHDU     161   (891, 893)   int16   
# 1  er.mask       1 TableHDU        25   1600R x 4C   [F6.2, F6.2, F6.2, F6.2]   

