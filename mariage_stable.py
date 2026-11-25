"""Algorithme du mariage stable (Gale-Shapley), les etudiants proposent.

Format des donnees : celui de generateur_preferences.py
    data["etudiants"]      : {"e0": ["s2", "s0", ...]}   voeux, du prefere au moins aime
    data["etablissements"] : {"s0": ["e3", "e1", ...]}   priorites, du prefere au moins aime
    data["capacites"]      : {"s0": 2, ...}              nombre de places

Resultat : affectation = {"e0": "s2", "e1": None, ...}   (None = pas de place)
"""

import sys
from generateur_preferences import charger, exemple_cours


def mariage_stable(data):
    voeux = data["etudiants"]          # les voeux de chaque etudiant
    priorites = data["etablissements"] # le classement des etudiants par chaque etablissement
    cap = data["capacites"]            # nombre de places par etablissement

    # rang[s][e] = position de e dans la liste de s (0 = le meilleur)
    # ca sert juste a comparer deux etudiants facilement
    rang = {s: {e: r for r, e in enumerate(liste)} for s, liste in priorites.items()}

    prochain = {e: 0 for e in voeux}   # pour chaque etudiant, le numero du prochain voeu a essayer
    admis = {s: [] for s in priorites} # les etudiants acceptes par chaque etablissement (pour l'instant)
    libres = list(voeux)               # au debut tout le monde est libre

    while libres:
        e = libres.pop(0)              # on prend le premier etudiant libre

        # s'il a deja tout essaye, il reste sans place
        if prochain[e] >= len(voeux[e]):
            continue

        s = voeux[e][prochain[e]]      # son meilleur voeu pas encore essaye
        prochain[e] += 1               # on avance, comme ca il ne retente jamais le meme
        admis[s].append(e)             # il candidate a s

        # si s a trop d'etudiants, il doit en rejeter un
        if len(admis[s]) > cap[s]:
            pire = max(admis[s], key=lambda x: rang[s][x])  # le moins bien classe par s
            admis[s].remove(pire)      # s le rejette
            libres.append(pire)        # il redevient libre et retentera plus tard

    # on transforme admis (etablissement -> etudiants) en affectation (etudiant -> etablissement)
    affectation = {e: None for e in voeux}
    for s, liste in admis.items():
        for e in liste:
            affectation[e] = s
    return affectation


def est_stable(data, affectation):
    # verifie qu'il n'y a pas de paire bloquante (e, s) :
    # un etudiant e et un etablissement s qui se preferent tous les deux
    # a ce qu'ils ont actuellement
    # renvoie (True, None) si c'est stable, sinon (False, (e, s))
    voeux = data["etudiants"]
    priorites = data["etablissements"]
    cap = data["capacites"]
    rang = {s: {e: r for r, e in enumerate(liste)} for s, liste in priorites.items()}

    # on reconstruit la liste des admis de chaque etablissement
    admis = {s: [] for s in priorites}
    for e, s in affectation.items():
        if s is not None:
            admis[s].append(e)

    for e, liste in voeux.items():
        for s in liste:
            # on regarde les voeux de e du meilleur au moins bon
            if s == affectation[e]:
                break                          # les suivants sont moins bien que ce qu'il a deja
            # ici e prefere s a son affectation actuelle, est-ce que s voudrait de lui ?
            if len(admis[s]) < cap[s]:         # s a encore une place libre
                return False, (e, s)
            if any(rang[s][e] < rang[s][x] for x in admis[s]):
                return False, (e, s)           # s prefere e a l'un de ses admis
    return True, None


if __name__ == "__main__":
    # sans argument : jeu de 5 etudiants (seed 42), sinon le fichier json donne en argument
    from generateur_preferences import generer
    data = charger(sys.argv[1]) if len(sys.argv) > 1 else generer(5, 3, mode="uniforme", seed=42)
    aff = mariage_stable(data)
    stable, contre = est_stable(data, aff)
    non_affectes = sum(1 for s in aff.values() if s is None)
    print(f"stable={stable}, non affectes={non_affectes}")
    if len(aff) <= 10:
        print(aff)