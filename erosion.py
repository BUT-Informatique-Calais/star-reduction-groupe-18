from modele import Modele
import matplotlib.pyplot as plt

modele : Modele = Modele('./examples/test_M31_linear.fits')
modele.enregistrerImageOriginale("a.png")
modele.enregistrerMasqueEtoilesAdouci("b.png")
modele.enregistrerImageSansEtoiles("c.png")
modele.enregistrerImageFinale("d.png")

# --- Affichage des résultats ---
# Afficher l'image originale, le masque adouci, l'image érodée et le résultat final
plt.figure(figsize=(20, 5))

plt.subplot(1, 4, 1)
plt.imshow(modele.getImageOriginale(), cmap='gray', origin='lower')
plt.title('Image originale')

plt.subplot(1, 4, 2)
plt.imshow(modele.getMasqueEtoilesAdouci(), cmap='gray', origin='lower')
plt.title('Masque d\'étoiles adouci')

plt.subplot(1, 4, 3)
plt.imshow(modele.getImageSansEtoiles(), cmap='gray', origin='lower')
plt.title('Image sans étoiles')

plt.subplot(1, 4, 4)
plt.imshow(modele.getImageFinale(), cmap='gray', origin='lower')
plt.title('Image finale (réduction localisée)')

plt.tight_layout()
plt.show()