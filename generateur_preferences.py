"""
Projet Aide à la décision — Algorithme du mariage stable
Partie 1 : Génération de préférences aléatoires (étudiants et établissements)

Consigne : chaque établissement a UNE seule place (capacité = 1).
Par défaut il y a autant d'établissements que d'étudiants (m = n) : mariage stable classique 1-1.

Format de sortie (JSON) partagé avec le groupe :
{
  "parametres":     {...},                       # comment le jeu a été généré
  "etudiants":      {"e0": ["s2", "s0", ...]},   # vœux, du préféré au moins aimé
  "etablissements": {"s0": ["e3", "e1", ...]},   # priorités, du préféré au moins aimé
  "capacites":      {"s0": 1, "s1": 1, ...}      # 1 place par établissement
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
      data = generer(10, mode="uniforme", seed=42)   # 10 étudiants, 10 établissements
"""

import json
import os
import random


# ---------------------------------------------------------------------------
# 1. Capacités
# ---------------------------------------------------------------------------
def generer_capacites(m):
    """Consigne de la prof : une seule place par établissement."""
    return [1] * m


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
def generer(n, m=None, mode="uniforme", seed=None, bruit=0.3):
    """
    n     : nombre d'étudiants
    m     : nombre d'établissements (défaut = n, chacun a 1 place)
    mode  : "uniforme" ou "correle"
    seed  : graine aléatoire (même seed => même jeu de données)
    bruit : écart-type du bruit en mode corrélé (scores communs dans [0,1])
    """
    if m is None:
        m = n
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

    cap = generer_capacites(m)

    return {
        "parametres": {"n": n, "m": m, "mode": mode, "seed": seed,
                       "places": sum(cap),
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
    assert all(c == 1 for c in data["capacites"].values()), "Capacité différente de 1"
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
                       "places": 3, "bruit": None},
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
    # (nom,                  n,    m,    mode,       bruit)
    ("petit_uniforme",       5,    5,    "uniforme", None),
    ("moyen_uniforme",       50,   50,   "uniforme", None),
    ("grand_uniforme",       200,  200,  "uniforme", None),
    ("moyen_correle_fort",   50,   50,   "correle",  0.1),   # forte concurrence
    ("moyen_correle_faible", 50,   50,   "correle",  1.0),   # proche de l'uniforme
    ("grand_correle",        200,  200,  "correle",  0.3),
    ("moyen_desequilibre",   60,   50,   "uniforme", None),  # plus d'étudiants que de places
]


def generer_tous(dossier="jeux_de_donnees", seeds=(1, 2, 3)):
    os.makedirs(dossier, exist_ok=True)
    sauvegarder(exemple_cours(), os.path.join(dossier, "exemple_cours.json"))
    nb = 1
    for nom, n, m, mode, bruit in SCENARIOS:
        for seed in seeds:
            kwargs = {"bruit": bruit} if bruit is not None else {}
            data = generer(n, m, mode=mode, seed=seed, **kwargs)
            verifier(data)
            sauvegarder(data, os.path.join(dossier, f"{nom}_{n}x{m}_seed{seed}.json"))
            nb += 1
    print(f"{nb} jeux de données générés dans '{dossier}/'")


if __name__ == "__main__":
    # Démo sur un petit jeu
    demo = generer(5, mode="uniforme", seed=42)
    verifier(demo)
    afficher(demo)
    print()
    # Reproductibilité : même seed => même résultat
    assert generer(5, seed=42) == demo
    print("Reproductibilité OK (même seed => même jeu)")
    generer_tous()
