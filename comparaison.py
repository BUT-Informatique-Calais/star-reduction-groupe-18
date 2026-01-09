import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.pyplot import imread


# Charger l'image FITS
hdu = fits.open('./examples/test_M31_linear.fits')[0]
data = hdu.data

# --- Vérification de la forme des données ---
# Vérifier la forme des données et extraire une image 2D si nécessaire
print(f"Forme originale des données: {data.shape}")
if data.ndim == 3:
    # Si l'image a 3 dimensions, prendre la première couche
    data = data[0]
    print(f"Nouvelle forme après extraction 2D: {data.shape}")
elif data.ndim > 3:
    # Si plus de 3 dimensions, extraire une slice 2D
    data = data[0, 0]
    print(f"Nouvelle forme après extraction 2D: {data.shape}")

# ==========================================================================
# PHASE 3 : COMPARATEUR AVANT/APRÈS
# Outil de visualisation pour détecter les pertes de détails dans la nébuleuse
# ==========================================================================

def normalize_image(img):
    """Normalise une image entre 0 et 1 en utilisant les percentiles pour éviter les valeurs extrêmes"""
    img = img - np.percentile(img, 1)  # Soustrait le 1er percentile (fond sombre)
    img = img / np.percentile(img, 99)  # Divise par le 99e percentile (évite les pixels saturés)
    return np.clip(img, 0, 1)

# Normaliser les images pour la comparaison
data_normalized = normalize_image(data)

# Charger l'image eroded.png pour la comparaison (utilisation directe)
eroded_image = imread('./results/eroded.png')

# Garder une version couleur pour l'affichage ET une version grise pour les calculs
eroded_color = eroded_image.copy()  # Version couleur pour l'affichage

# Créer une version en niveaux de gris pour les calculs de différence
if eroded_image.ndim == 3:
    # Convertir RGBA ou RGB en niveaux de gris
    if eroded_image.shape[2] == 4:  # RGBA
        eroded_gray = np.mean(eroded_image[:,:,:3], axis=2)
    else:  # RGB
        eroded_gray = np.mean(eroded_image, axis=2)
else:
    eroded_gray = eroded_image

# Normaliser les deux versions
eroded_normalized = normalize_image(eroded_gray)  # Pour les calculs
eroded_color_normalized = normalize_image(eroded_color)  # Pour l'affichage

# --- Animation de clignotement ---
print("=== Animation de clignotement ===")
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(data_normalized, cmap='gray', origin='lower')
ax.set_title("Avant traitement (original)", fontsize=14)
ax.axis('off')

images = [data_normalized, eroded_color_normalized]  # Utilise la version couleur pour l'affichage
titles = ["Avant traitement (original)", "Après traitement (eroded.png)"]
cmaps = ['gray', None]  # None pour les images couleur

def update_frame(frame):
    """Fonction d'animation qui alterne entre les deux images"""
    frame_index = frame % 2  # Alternance entre 0 et 1
    
    # Effacer et redessiner pour éviter les problèmes de dimension
    ax.clear()
    ax.imshow(images[frame_index], cmap=cmaps[frame_index], origin='lower')
    ax.set_title(titles[frame_index], fontsize=14)
    ax.axis('off')
    return [ax]

# Créer l'animation avec un intervalle de 800ms entre les frames
# blit=False pour permettre la mise à jour du titre
animation = FuncAnimation(fig, update_frame, interval=800, blit=False, repeat=True)
plt.show()

# --- Comparaison côte à côte ---
print("=== Comparaison côte à côte ===")
plt.figure(figsize=(16, 6))

plt.subplot(1, 3, 1)
plt.imshow(data_normalized, cmap='gray', origin='lower')
plt.title('Image originale')
plt.axis('off')

plt.subplot(1, 3, 2)
plt.imshow(eroded_color_normalized, origin='lower')  # Affiche la version couleur
plt.title('Image traitée (eroded.png)')
plt.axis('off')

# --- 3.3 : Image de différence (soustraction) ---
print("=== Image de différence ===")
difference = data_normalized - eroded_normalized  # Utilise les versions en niveaux de gris

plt.subplot(1, 3, 3)
plt.imshow(difference, cmap='RdBu', origin='lower', vmin=-0.3, vmax=0.3)
plt.title('Différence (Originale - Traitée)')
plt.axis('off')

plt.tight_layout()
plt.show()

# --- Analyse statistique des pertes ---
print("=== Analyse statistique des pertes ===")
print(f"Différence moyenne : {np.mean(difference):.6f}")
print(f"Différence médiane : {np.median(difference):.6f}")
print(f"Écart-type de la différence : {np.std(difference):.6f}")
print(f"Différence maximale (perte) : {np.max(difference):.6f}")
print(f"Différence minimale (gain) : {np.min(difference):.6f}")

# Calculer le pourcentage de pixels avec des pertes significatives (> 5% de la dynamique)
significant_loss = np.sum(difference > 0.05) / difference.size * 100
significant_gain = np.sum(difference < -0.05) / difference.size * 100
print(f"Pixels avec perte significative (>5%) : {significant_loss:.2f}%")
print(f"Pixels avec gain significatif (<-5%) : {significant_gain:.2f}%")
