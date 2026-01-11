from astropy.io import fits
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

# FITS, format standard en astronomie (images, et données precises)
fits_file = './examples/test_M31_linear.fits'
hdul = fits.open(fits_file)  # hdul = HDU List (liste des unités de données)

hdul.info() # affiche les informations hdu

# Accéder aux données du HDU principal
# HDU, chaqueHDU contient des données et métadonnées
# hdul[0] = HDU primaire qui contient l'image
data = hdul[0].data

# Accéder aux métadonnées : taille, coordonnées, instrument et autres
header = hdul[0].header

# Gérer les images monochromes et couleur
# ndim = nombre de dimensions (2D = monochrome, 3D = couleur)
if data.ndim == 3: # Image couleur car 3 dimensions
     # Les données FITS peuvent avoir les canaux de couleur en première dimension
    if data.shape[0] == 3:  # vérifie la dimension avant utilisation
        data = np.transpose(data, (1, 2, 0))  # Changement en hauteur, largeur, canaux
    
    # Normaliser image à [0, 1] pour matplotlib
    # Évite les gros nombres et les bugs associés avec le format [0, 1]
    data_normalized = (data - data.min()) / (data.max() - data.min())
    
    # Sauvegarder les données comme image png
    plt.imsave('./results/original.png', data_normalized)
    
    # Normaliser chaque canal séparément à [0, 255] pour OpenCV
    image = np.zeros_like(data, dtype='uint8')
    for i in range(data.shape[2]):
        channel = data[:, :, i]
        image[:, :, i] = ((channel - channel.min()) / (channel.max() - channel.min()) * 255).astype('uint8')
else:
    # Sauvegarde version monochrome
    plt.imsave('./results/original.png', data, cmap='gray')

    # Convertir en uint8 pour OpenCV (de float vers entiers 0-255)
    image = ((data - data.min()) / (data.max() - data.min()) * 255).astype('uint8') # même calcul que data_normalized avec conve


# Définir un noyau pour l'érosion
# Le noyau 3x3 détermine la forme et la taille de l'opération morphologique
kernel = np.ones((3,3), np.uint8)  # Matrice 3x3 remplie de 1

# Effectue l'érosion en fonction de l'image couleur et monochromes
if data.ndim == 3:  # Image couleur
    # Pour les images en couleur on applique l'érosion sur chaque canal
    eroded_image = np.zeros_like(image, dtype='uint8')
    for i in range(image.shape[2]):  # Pour chaque canal de couleur (R, G, B)
        eroded_image[:, :, i] = cv.erode(image[:, :, i], kernel, iterations=1)
    
    # Convertir en format [0, 1] pour matplotlib (comme l'image originale)
    eroded_normalized = eroded_image.astype('float32') / 255.0
    # Sauvegarder avec matplotlib pour préserver les couleurs
    plt.imsave('./results/eroded.png', eroded_normalized)
else:  # Image monochrome
    # Érosion simple d'itération unique
    eroded_image = cv.erode(image, kernel, iterations=1)
    # On sauvegarde l'image érodée
    cv.imwrite('./results/eroded.png', eroded_image)
    print("Érosion simple effectuée pour l'image monochrome")

# Fermer pour valider et éviter les fuites de mémoire
hdul.close()
