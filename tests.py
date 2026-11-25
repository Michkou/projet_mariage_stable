from satisfaction import satisfaction_etudiants, satisfaction_ecoles
from generateur_preferences import generer
from mariage_stable import mariage_stable
import matplotlib.pyplot as plt

pref = {"i1": ["s2", "s1", "s3"], "i2": ["s1", "s2", "s3"], "i3": ["s1", "s2", "s3"]}
prio = {"s1": ["i1", "i3", "i2"], "s2": ["i2", "i1", "i3"], "s3": ["i2", "i1", "i3"]}

aff_gs     = {"i1": "s1", "i2": "s2", "i3": "s3"}
aff_boston = {"i1": "s2", "i2": "s3", "i3": "s1"}

res = satisfaction_etudiants(aff_gs, pref)
print("GS étudiants     :", round(res["moyenne"], 3))

res = satisfaction_ecoles(aff_gs, prio)
print("GS écoles         :", round(res["moyenne"], 3))

res = satisfaction_etudiants(aff_boston, pref)
print("Boston étudiants :", round(res["moyenne"], 3))

res = satisfaction_ecoles(aff_boston, prio)
print("Boston écoles     :", round(res["moyenne"], 3))

data = generer(60, 50, mode="uniforme", seed=1)
aff = mariage_stable(data)

print("Satisfaction étudiants :", satisfaction_etudiants(aff, data["etudiants"]))
print("Satisfaction écoles     :", satisfaction_ecoles(aff, data["etablissements"]))

def lancer(n, m, mode):
    liste_etu = [] 
    liste_eco = []
    liste_premier = []
    liste_non_aff = []
    for seed in range(20):
        data = generer(n, m, mode=mode, seed=seed)
        aff = mariage_stable(data)
        liste_etudiants = satisfaction_etudiants(aff, data["etudiants"])
        liste_ecoles = satisfaction_ecoles(aff, data["etablissements"])
        liste_etu.append(liste_etudiants["moyenne"])
        liste_eco.append(liste_ecoles["moyenne"])
        liste_premier.append(liste_etudiants["pct_premier_voeu"])
        liste_non_aff.append(liste_etudiants["non_affectes"])

    moy_etu = sum(liste_etu) / len(liste_etu)
    moy_eco = sum(liste_eco) / len(liste_eco)
    moy_premier = sum(liste_premier) / len(liste_premier)
    moy_non_aff = sum(liste_non_aff) / len(liste_non_aff)
    return { "moyenne_etudiants": moy_etu, "moyenne_ecoles": moy_eco, "pct_premier_voeu": moy_premier, "non_affectes": moy_non_aff }


print(f"{'Scénario':<20} {'Moyenne Étudiants':<20} {'Moyenne Écoles':<20} {'% Premier Vœu':<20} {' Non Affectés':<20}")


noms = []
sat_etu = []
sat_eco = []

scenarios = [
    (5, 5, "uniforme"),
    (50, 50, "uniforme"),
    (200, 200, "uniforme"),
    (50, 50, "correle"),
    (60, 50, "uniforme"),
]

for n, m, mode in scenarios:
    res = lancer(n, m, mode)
    nom = f"{n}x{m} {mode}"
    noms.append(nom)
    sat_etu.append(res["moyenne_etudiants"])
    sat_eco.append(res["moyenne_ecoles"])
    print(f"{nom:<20} {res['moyenne_etudiants']:<20.3f} {res['moyenne_ecoles']:<20.3f} {res['pct_premier_voeu']:<20.1f} {res['non_affectes']:<20.1f}")

print("\nRésumé des scénarios :")
for nom, s_etu, s_eco in zip(noms, sat_etu, sat_eco):
    print(f"{nom:<20} {s_etu:<20.3f} {s_eco:<20.3f}")

x = list(range(len(noms)))
plt.bar([i - 0.2 for i in x], sat_etu, width=0.4, label="Étudiants")
plt.bar([i + 0.2 for i in x], sat_eco, width=0.4, label="Écoles")
plt.xticks(x, noms, rotation=45, ha="right")
plt.ylabel("Satisfaction moyenne")
plt.title("Satisfaction moyenne des étudiants et des écoles selon le scénario")
plt.legend()
plt.tight_layout()
plt.savefig("satisfaction_scenarios.png", dpi=150, bbox_inches="tight")
plt.show()