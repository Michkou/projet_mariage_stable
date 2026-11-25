"""Lance mariage_stable sur tous les jeux de jeux_de_donnees/ et affiche un tableau.

Utilisation :  python3 bilan_mariage_stable.py
"""

import glob
import os

from generateur_preferences import charger
from mariage_stable import mariage_stable, est_stable, rang_obtenu

fichiers = sorted(glob.glob("jeux_de_donnees/*.json"))

print(f"{'jeu de donnees':42s} {'etu':>4s} {'plc':>4s} {'stable':>7s} {'non aff.':>8s} "
      f"{'rang moy.':>9s} {'1er voeu':>9s} {'pire':>5s}")
print("-" * 98)

tout_stable = True
for f in fichiers:
    data = charger(f)
    aff = mariage_stable(data)
    stable, _ = est_stable(data, aff)
    tout_stable = tout_stable and stable
    rangs = [r for r in rang_obtenu(data, aff).values() if r is not None]
    n = len(data["etudiants"])
    places = sum(data["capacites"].values())
    premier = sum(1 for r in rangs if r == 1)
    nom = os.path.basename(f).replace(".json", "")
    print(f"{nom:42s} {n:4d} {places:4d} {str(stable):>7s} {n - len(rangs):8d} "
          f"{sum(rangs) / len(rangs):9.2f} {premier:4d}/{len(rangs):<4d} {max(rangs):5d}")

print("-" * 98)
print("Tous les jeux sont stables." if tout_stable else "ATTENTION : au moins un jeu n'est pas stable.")