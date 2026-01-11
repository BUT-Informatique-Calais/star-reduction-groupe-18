import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import sys 

fits_path = "./examples/test_M31_linear.fits"
output_png = "./results/image_multicanal.png"
stretch_factor = 5.0

if len(sys.argv) < 4: 
    print("Usage : python script.py rouge vert bleu") 
    sys.exit(1) 
    
red = float(sys.argv[1]) 
green = float(sys.argv[2]) 
blue = float(sys.argv[3])

# Ouverture du fichier FITS
with fits.open(fits_path) as hdul:
    img = hdul[0].data.astype(np.float32)

# Normalisation par canal -> [0, 1]
img_norm = np.zeros_like(img) 
for c in range(img.shape[0]): 
    cmin = np.min(img[c]) 
    cmax = np.max(img[c]) 
    img_norm[c] = (img[c] - cmin) / (cmax - cmin)

# Étirement asinh
img_stretched = np.arcsinh(stretch_factor * img_norm) / np.arcsinh(stretch_factor)

# Réorganisation pour matplotlib 
# (H, W, C)
img_rgb = np.moveaxis(img_stretched, 0, -1)

img_rgb = np.clip(img_rgb, 0, 1)
tint = np.array([red, green, blue]) # R, G, B 
img_tinted = img_rgb * tint 
img_tinted = np.clip(img_tinted, 0, 1)

# Afficher et sauvegarder
plt.figure(figsize=(6, 6))
plt.imshow(img_tinted, origin="lower")
plt.axis("off")
plt.savefig(output_png, dpi=300, bbox_inches="tight", pad_inches=0)
plt.show()

plt.close()

print("Image générée vers le chemin :", output_png)
