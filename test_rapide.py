"""
Test de bout en bout : charge un jeu de données (format de generateur_preferences.py),
lance Gale-Shapley avec capacités (étudiants qui proposent puis établissements qui proposent),
vérifie la stabilité et affiche la satisfaction.

Utilisation :
  python test_rapide.py                                   -> exemple du cours
  python test_rapide.py jeux_de_donnees/xxx.json          -> un jeu précis
"""

import sys
from statistics import mean, pstdev
from generateur_preferences import charger, exemple_cours


# ---------------------------------------------------------------------------
# Gale-Shapley (acceptation différée), étudiants proposants, avec capacités
# ---------------------------------------------------------------------------
def gale_shapley_etudiants(data):
    prefs_e = data["etudiants"]
    prefs_s = data["etablissements"]
    cap = data["capacites"]
    rang_s = {s: {e: i for i, e in enumerate(l)} for s, l in prefs_s.items()}

    prochain = {e: 0 for e in prefs_e}         # index du prochain vœu à tenter
    admis = {s: [] for s in prefs_s}           # admis temporairement
    libres = list(prefs_e)

    while libres:
        e = libres.pop(0)
        if prochain[e] >= len(prefs_e[e]):     # a épuisé tous ses vœux
            continue
        s = prefs_e[e][prochain[e]]
        prochain[e] += 1
        admis[s].append(e)
        admis[s].sort(key=lambda x: rang_s[s][x])   # meilleurs en tête
        if len(admis[s]) > cap[s]:
            rejete = admis[s].pop()                 # le moins bien classé sort
            libres.append(rejete)

    affectation = {e: None for e in prefs_e}
    for s, liste in admis.items():
        for e in liste:
            affectation[e] = s
    return affectation


# ---------------------------------------------------------------------------
# Gale-Shapley, établissements proposants, avec capacités
# ---------------------------------------------------------------------------
def gale_shapley_etablissements(data):
    prefs_e = data["etudiants"]
    prefs_s = data["etablissements"]
    cap = data["capacites"]
    rang_e = {e: {s: i for i, s in enumerate(l)} for e, l in prefs_e.items()}

    prochain = {s: 0 for s in prefs_s}
    admis = {s: [] for s in prefs_s}
    affectation = {e: None for e in prefs_e}
    a_traiter = [s for s in prefs_s]

    while a_traiter:
        s = a_traiter.pop(0)
        while len(admis[s]) < cap[s] and prochain[s] < len(prefs_s[s]):
            e = prefs_s[s][prochain[s]]
            prochain[s] += 1
            actuel = affectation[e]
            if actuel is None:
                affectation[e] = s
                admis[s].append(e)
            elif rang_e[e][s] < rang_e[e][actuel]:   # l'étudiant préfère s
                admis[actuel].remove(e)
                affectation[e] = s
                admis[s].append(e)
                a_traiter.append(actuel)             # actuel a une place libre
    return affectation


# ---------------------------------------------------------------------------
# Vérification de stabilité : aucune "envie justifiée"
# ---------------------------------------------------------------------------
def est_stable(data, affectation):
    prefs_e, prefs_s, cap = data["etudiants"], data["etablissements"], data["capacites"]
    rang_s = {s: {e: i for i, e in enumerate(l)} for s, l in prefs_s.items()}
    admis = {s: [e for e, x in affectation.items() if x == s] for s in prefs_s}
    for e, liste in prefs_e.items():
        actuel = affectation[e]
        for s in liste:
            if s == actuel:
                break                                  # vœux suivants : moins aimés
            # e préfère s à son affectation : s a-t-il une place libre
            # ou un admis moins prioritaire que e ?
            if len(admis[s]) < cap[s]:
                return False, (e, s)
            if any(rang_s[s][e] < rang_s[s][x] for x in admis[s]):
                return False, (e, s)
    return True, None


# ---------------------------------------------------------------------------
# Satisfaction (rang normalisé, 1 = premier choix, 0 = dernier ou non affecté)
# ---------------------------------------------------------------------------
def sat_rang(rang, n):
    return 1.0 if n == 1 else 1 - (rang - 1) / (n - 1)


def satisfaction(data, affectation):
    prefs_e, prefs_s = data["etudiants"], data["etablissements"]
    m, n = len(prefs_s), len(prefs_e)
    sat_e = {e: (sat_rang(prefs_e[e].index(s) + 1, m) if s else 0.0)
             for e, s in affectation.items()}
    sat_s = {}
    for s in prefs_s:
        admis = [e for e, x in affectation.items() if x == s]
        sat_s[s] = mean(sat_rang(prefs_s[s].index(e) + 1, n) for e in admis) if admis else 0.0
    return sat_e, sat_s


def resume(nom, valeurs):
    v = list(valeurs.values())
    return f"{nom:15s} moyenne={mean(v):.3f}  écart-type={pstdev(v):.3f}  min={min(v):.3f}"


def lancer(data):
    for titre, algo in [("Étudiants proposants", gale_shapley_etudiants),
                        ("Établissements proposants", gale_shapley_etablissements)]:
        aff = algo(data)
        stable, contre_ex = est_stable(data, aff)
        sat_e, sat_s = satisfaction(data, aff)
        print(f"=== {titre} ===")
        if len(aff) <= 10:
            print("  Affectation :", aff)
        print("  Stable :", stable, "" if stable else f"(paire bloquante {contre_ex})")
        print("  Non affectés :", sum(1 for x in aff.values() if x is None))
        print("  " + resume("Étudiants", sat_e))
        print("  " + resume("Établissements", sat_s))
        print()


if __name__ == "__main__":
    data = charger(sys.argv[1]) if len(sys.argv) > 1 else exemple_cours()
    print("Jeu :", data["parametres"], "\n")
    lancer(data)
