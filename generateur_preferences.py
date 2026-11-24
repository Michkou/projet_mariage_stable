"""
Projet Aide à la décision — Algorithme du mariage stable
Partie 1 : Génération de préférences aléatoires (étudiants et établissements)

Format de sortie (JSON) partagé avec le groupe :
{
  "parametres":     {...},                       # comment le jeu a été généré
  "etudiants":      {"e0": ["s2", "s0", ...]},   # vœux, du préféré au moins aimé
  "etablissements": {"s0": ["e3", "e1", ...]},   # priorités, du préféré au moins aimé
  "capacites":      {"s0": 2, "s1": 1, ...}      # nombre de places
}

Deux modes de génération :
  - "uniforme" : chaque agent classe l'autre côté au hasard (permutation aléatoire).
  - "correle"  : chaque établissement a une popularité et chaque étudiant un niveau.
                 Chaque agent classe selon  score_commun + bruit_individuel.
                 bruit petit  -> goûts très similaires -> forte concurrence
                 bruit grand  -> on se rapproche du mode uniforme

Utilisation :
  python generateur_preferences.py            -> génère tous les jeux de test dans ./jeux_de_donnees
  ou dans un autre fichier :
      from generateur_preferences import generer, charger
      data = generer(10, 3, mode="uniforme", seed=42)
"""

import json
import os
import random


# ---------------------------------------------------------------------------
# 1. Capacités
# ---------------------------------------------------------------------------
def generer_capacites(n, m, rng, total_places=None):
    """Répartit `total_places` places entre m établissements (au moins 1 chacun).
    Par défaut total_places = n (autant de places que d'étudiants)."""
    if total_places is None:
        total_places = n
    total_places = max(total_places, m)          # au moins 1 place par établissement
    cap = [1] * m
    for _ in range(total_places - m):
        cap[rng.randrange(m)] += 1
    return cap


# ---------------------------------------------------------------------------
# 2. Préférences
# ---------------------------------------------------------------------------
def prefs_uniformes(agents, cibles, rng):
    """Chaque agent reçoit une permutation aléatoire des cibles."""
    return {a: rng.sample(cibles, len(cibles)) for a in agents}


def prefs_correlees(agents, cibles, scores_cibles, bruit, rng):
    """Chaque agent trie les cibles par (score commun + bruit gaussien individuel)."""
    prefs = {}
    for a in agents:
        note = {c: scores_cibles[c] + rng.gauss(0, bruit) for c in cibles}
        prefs[a] = sorted(cibles, key=lambda c: note[c], reverse=True)
    return prefs


# ---------------------------------------------------------------------------
# 3. Générateur principal
# ---------------------------------------------------------------------------
def generer(n, m, mode="uniforme", seed=None, total_places=None, bruit=0.3):
    """
    n            : nombre d'étudiants
    m            : nombre d'établissements
    mode         : "uniforme" ou "correle"
    seed         : graine aléatoire (même seed => même jeu de données)
    total_places : somme des capacités (défaut = n)
    bruit        : écart-type du bruit en mode corrélé (scores communs dans [0,1])
    """
    rng = random.Random(seed)                    # générateur local => reproductible
    E = [f"e{i}" for i in range(n)]
    S = [f"s{j}" for j in range(m)]

    if mode == "uniforme":
        prefs_e = prefs_uniformes(E, S, rng)
        prefs_s = prefs_uniformes(S, E, rng)
    elif mode == "correle":
        popularite = {s: rng.random() for s in S}  # attractivité des établissements
        niveau = {e: rng.random() for e in E}       # niveau des étudiants
        prefs_e = prefs_correlees(E, S, popularite, bruit, rng)
        prefs_s = prefs_correlees(S, E, niveau, bruit, rng)
    else:
        raise ValueError("mode doit être 'uniforme' ou 'correle'")

    cap = generer_capacites(n, m, rng, total_places)

    return {
        "parametres": {"n": n, "m": m, "mode": mode, "seed": seed,
                       "total_places": sum(cap),
                       "bruit": bruit if mode == "correle" else None},
        "etudiants": prefs_e,
        "etablissements": prefs_s,
        "capacites": dict(zip(S, cap)),
    }


# ---------------------------------------------------------------------------
# 4. Vérification
# ---------------------------------------------------------------------------
def verifier(data):
    """Vérifie que le jeu de données est bien formé. Lève une erreur sinon."""
    E = set(data["etudiants"])
    S = set(data["etablissements"])
    for e, liste in data["etudiants"].items():
        assert len(liste) == len(set(liste)) == len(S) and set(liste) == S, \
            f"Liste de {e} invalide (doublon ou oubli)"
    for s, liste in data["etablissements"].items():
        assert len(liste) == len(set(liste)) == len(E) and set(liste) == E, \
            f"Liste de {s} invalide (doublon ou oubli)"
    assert set(data["capacites"]) == S, "Capacités manquantes"
    assert all(c >= 1 for c in data["capacites"].values()), "Capacité < 1"
    return True


# ---------------------------------------------------------------------------
# 5. Sauvegarde / chargement
# ---------------------------------------------------------------------------
def sauvegarder(data, chemin):
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def charger(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def afficher(data):
    """Affichage lisible (pratique pour les petits jeux)."""
    print("Étudiants (vœux) :")
    for e, l in data["etudiants"].items():
        print(f"  {e} : {' > '.join(l)}")
    print("Établissements (priorités) :")
    for s, l in data["etablissements"].items():
        print(f"  {s} (cap={data['capacites'][s]}) : {' > '.join(l)}")


# ---------------------------------------------------------------------------
# 6. Exemple du cours (Part 4-bis) — pour valider l'algo à la main
# ---------------------------------------------------------------------------
def exemple_cours():
    return {
        "parametres": {"n": 3, "m": 3, "mode": "exemple_cours", "seed": None,
                       "total_places": 3, "bruit": None},
        "etudiants": {"i1": ["s2", "s1", "s3"],
                      "i2": ["s1", "s2", "s3"],
                      "i3": ["s1", "s2", "s3"]},
        "etablissements": {"s1": ["i1", "i3", "i2"],
                           "s2": ["i2", "i1", "i3"],
                           "s3": ["i2", "i1", "i3"]},
        "capacites": {"s1": 1, "s2": 1, "s3": 1},
    }


# ---------------------------------------------------------------------------
# 7. Génération de tous les jeux de test
# ---------------------------------------------------------------------------
SCENARIOS = [
    # (nom,                        n,    m,  mode,       places, bruit)
    ("petit_uniforme",             5,    3,  "uniforme", None,   None),
    ("moyen_uniforme",             100,  10, "uniforme", None,   None),
    ("grand_uniforme",             1000, 50, "uniforme", None,   None),
    ("moyen_correle_fort",         100,  10, "correle",  None,   0.1),   # forte concurrence
    ("moyen_correle_faible",       100,  10, "correle",  None,   1.0),   # proche de l'uniforme
    ("grand_correle",              1000, 50, "correle",  None,   0.3),
    ("moyen_uniforme_tendu",       100,  10, "uniforme", 80,     None),  # moins de places que d'étudiants
    ("moyen_correle_tendu",        100,  10, "correle",  80,     0.3),
    ("moyen_uniforme_large",       100,  10, "uniforme", 130,    None),  # plus de places
]


def generer_tous(dossier="jeux_de_donnees", seeds=(1, 2, 3)):
    os.makedirs(dossier, exist_ok=True)
    sauvegarder(exemple_cours(), os.path.join(dossier, "exemple_cours.json"))
    nb = 1
    for nom, n, m, mode, places, bruit in SCENARIOS:
        for seed in seeds:
            kwargs = {"total_places": places}
            if bruit is not None:
                kwargs["bruit"] = bruit
            data = generer(n, m, mode=mode, seed=seed, **kwargs)
            verifier(data)
            sauvegarder(data, os.path.join(dossier, f"{nom}_{n}x{m}_seed{seed}.json"))
            nb += 1
    print(f"{nb} jeux de données générés dans '{dossier}/'")


if __name__ == "__main__":
    # Démo sur un petit jeu
    demo = generer(5, 3, mode="uniforme", seed=42)
    verifier(demo)
    afficher(demo)
    print()
    # Reproductibilité : même seed => même résultat
    assert generer(5, 3, seed=42) == demo
    print("Reproductibilité OK (même seed => même jeu)")
    generer_tous()
