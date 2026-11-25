def score_rang(rang, n):
        if n <= 1:
            return 1.0
        return  (1 - (rang - 1) / (n - 1))

#But : transformer un rang en note.
    # rang est la position obtenue (1 = premier vœu).
    # n est la longueur de la liste.

#Cette formule sert à donner à chaque rang une note entre 0 et 1 :
    #1 si l'étudiant obtient son 1er vœu (le meilleur cas),
    #0 s'il obtient son dernier vœu (le pire cas),
    #et des valeurs régulièrement espacées entre les deux.

    #1. rang − 1 = le nombre de places perdues``
    #2. n − 1 = le nombre de places possibles à perdre
    #3. (rang − 1) / (n − 1) = la part perdue
    #4. 1 - ((rang - 1) / (n - 1)) = la note finale

def satisfaction_etudiants(affectations, pref_etudiants):
    scores = [] 
    premiers = 0
    non_affectes = 0
    for etudiant, prefs in pref_etudiants.items():
        n = len(prefs)
        ecole = affectations.get(etudiant)       # "s1"
        if ecole is None:
            scores.append(0.0)
            non_affectes += 1
        else:
            rang = prefs.index(ecole) + 1
            if rang == 1:
                premiers += 1
            score = score_rang(rang, n)
            scores.append(score)
    if len(scores) == 0:
        return {"moyenne": 0.0, "pct_premier_voeu": 0.0, "non_affectes": 0}
    return {"moyenne": sum(scores) / len(scores),"pct_premier_voeu": 100 * premiers / len(scores), "non_affectes": non_affectes}

def satisfaction_ecoles(affectations, prio_ecoles):
    admis = {s: [] for s in prio_ecoles}      # 1. listes vides
    for etudiant, ecole in affectations.items():   # 2. on remplit
        if ecole is not None:
            admis[ecole].append(etudiant)
    scores = []
    for ecole, prios in prio_ecoles.items():
        n = len(prios)
        if len(admis[ecole]) == 0:
            scores.append(0.0)
        else:
            notes = []
            for etudiant in admis[ecole]:
                rang = prios.index(etudiant) + 1
                notes.append(score_rang(rang, n))
            scores.append(sum(notes) / len(notes))
    if len(scores) == 0:
        return {"moyenne": 0.0, "ecoles_vides": 0}
    return {"moyenne": sum(scores) / len(scores), "ecoles_vides": len([e for e in prio_ecoles if e not in affectations.values()])}


if __name__ == "__main__":
    print(score_rang(1, 3))
    print(score_rang(2, 7))
    print(score_rang(3, 3))
    print(score_rang(1, 1))

    pref_etudiants = {"i1": ["s2", "s1"], "i2": ["s1", "s2"], "i3": ["s1", "s2"]}
    affectations    = {"i1": "s2", "i2": "s1"}     # i3 n'a rien
    print(satisfaction_etudiants(affectations, pref_etudiants))

    prio_ecoles = {"s1": ["i1", "i2", "i3"], "s2": ["i2", "i1", "i3"], "s3": ["i1", "i2", "i3"]}
    affectation = {"i1": "s1", "i3": "s1", "i2": "s2"}
    print(satisfaction_ecoles(affectation, prio_ecoles))