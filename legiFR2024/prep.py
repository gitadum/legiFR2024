# -*- coding: utf-8 -*-

import pandas as pd
from legiFR2024.utils import lire_tables_web, parsage_nombres

MININT  = "https://www.resultats-elections.interieur.gouv.fr"
URLBASE = "/".join([MININT, "legislatives2024", "ensemble_geographique"])

# Dictionnaire de clés techniques du site officiel des élections législatives
# L'URL d'un résultat par département est associé à un identifiant géographique
# ENSGEOS associe le numéros du département (clé) à l'ID géographique (valeur)
ENSGEOS = {"01":"84", "02":"32", "03":"84", "04":"93", "05":"93",
           "06":"93", "07":"84", "08":"44", "09":"76", "10":"44",
           "11":"76", "12":"76", "13":"93", "14":"28", "15":"84",
           "16":"75", "17":"75", "18":"24", "19":"75", "2A":"94", "2B":"94",
           "21":"27", "22":"53", "23":"75", "24":"75", "25":"27",
           "26":"84", "27":"28", "28":"24", "29":"53", "30":"76",
           "31":"76", "32":"76", "33":"75", "34":"76", "35":"53",
           "36":"24", "37":"24", "38":"84", "39":"27", "40":"75",
           "41":"24", "42":"84", "43":"84", "44":"52", "45":"24",
           "46":"76", "47":"75", "48":"76", "49":"52", "50":"28",
           "51":"44", "52":"44", "53":"52", "54":"44", "55":"44",
           "56":"53", "57":"44", "58":"27", "59":"32", "60":"32",
           "61":"28", "62":"32", "63":"84", "64":"75", "65":"76",
           "66":"76", "67":"44", "68":"44", "69":"84", "70":"27",
           "71":"27", "72":"52", "73":"84", "74":"84", "75":"11",
           "76":"28", "77":"11", "78":"11", "79":"75", "80":"32",
           "81":"76", "82":"76", "83":"93", "84":"93", "85":"52",
           "86":"75", "87":"75", "88":"44", "89":"27", "90":"27",
           "91":"11", "92":"11", "93":"11", "94":"11", "95":"11",
           "971":"01", "972":"02", "973":"03", "974":"04", "975":"",
           "976":"06", "986":"", "987":"", "988": "",
           "ZX": "", "ZZ": ""
           }


class Scrutin:
    """
    Scrutin législatif pour une circonscription française donnée
    """
    def __init__(self, dept: str, circ: int, clos: bool = True) -> None:
        self.dept = dept
        self.circ = circ
        self.clos = clos
        self.resultat: pd.DataFrame = None
        self.particip: pd.DataFrame = None
        pass
    
    def recup_resultat(self, tour: int):
        """
        Récupère les tableaux de résultats et participations
        pour le scrutin depuis le site du ministère de l'intérieur
        * tour: détermine si le scrutin est un premier ou un second tour
        """
        clef_dept = str(self.dept).zfill(2)
        clef_circ = clef_dept + str(self.circ).zfill(2)
        num_geo = ENSGEOS[self.dept]
        url =  "/".join([URLBASE, num_geo, clef_dept, clef_circ, "index.html"])
        tables = lire_tables_web(url)
        if tour == 1:
            tables = tables[-2:]
        elif tour == 2:
            tables = tables[:-2]

        self.resultat = tables[0]
        if len(tables) > 1:
            self.particip = tables[1] 
            self.particip.set_index(self.particip.columns[0], inplace=True)
            self.particip.index.name = "Participation"
            
    def prepare_resultat(self):
        resu = self.resultat
        part = self.particip
        cols_a_garder_resu = ["Liste des candidats", "Nuance"]
        cols_a_garder_part = ["Nombre"]
        try:
            assert ("Voix" in list(resu.columns)) and (part is not None)
            cols_a_garder_resu.append("Voix")
            resu = resu.loc[:, cols_a_garder_resu]
            part = part.loc[:, cols_a_garder_part]
            resu.loc[:, "Voix"] = resu["Voix"].map(parsage_nombres)
            resu["Tot. Exprimés"] = resu["Voix"].sum()
            part.loc[:, "Nombre"] = part["Nombre"].map(parsage_nombres)
            resu["Tot. Inscrits"] = part.loc["Inscrits", "Nombre"]
            resu["Pct. Exprimés"] = resu["Voix"] / resu["Tot. Exprimés"]
            resu["Pct. Inscrits"] = resu["Voix"] / resu["Tot. Inscrits"]
        except AssertionError:
            print("Les résultats et la participation ne sont pas disponibles.")
            pass
        finally:
            self.resultat = resu
            self.particip = part

class PremierTour(Scrutin):

    def est_elu(candidat):
        """
        Détermine si un candidat est en situation d'être élu dès le 1er tour.
        Rappel de la règle :
        Pour être élu député dès le 1er tour, un candidat doit rassembler au moins :
        * 50% des suffrages exprimés
        * 25% des électeurs inscrits
        """
        if (candidat["Pct. Exprimés"] >= .5) and (candidat["Pct. Inscrits"] >= .25):
            return True
        else:
            return False
    
    def est_qualifie(candidat):
        """
        Détermine si un candidat est en situation d'être qualifié au 2nd tour.
        Rappel de la règle :
        Pour être qualifié pour le 2nd tour, un candidat :
        * Ne doit pas avoir été élu
        * Ne doit pas avoir été éliminé
        * Doit rassembler au moins 12,5% des électeurs inscrits
        """
        if  candidat["Elu"] or candidat["Eliminé"]:
            return False
        elif candidat["Pct. Inscrits"] < .125:
            return False
        else:
            return True

    def est_elimine(candidat):
        """
        Acte l'élimination d'un candidat qui n'est pas élu ni qualifié.
        À utiliser après application des méthodes `est_elu` et `est_qualifie`
        """
        if candidat["Elu"] or candidat["Qualifié"]:
            return False
        else:
            return True

    def issue(self):
        self.recup_resultat(tour=1)
        self.prepare_resultat()
        if self.clos:
            resu = self.resultat
            resu["Eliminé"] = False
            # Détermine si un candidat est élu dès le 1er tour
            resu["Elu"] = resu.apply(PremierTour.est_elu, axis=1)
            # Si un candidat est élu dès le 1er tour, les autres sont éliminés
            if resu[resu["Elu"]].shape[0] != 0:
                resu.loc[~resu["Elu"], "Eliminé"] = True
            # Détermine quels candidats sont qualifiés pour le 2nd tour
            resu["Qualifié"] = resu.apply(PremierTour.est_qualifie, axis=1)
            # Élimine les candidats qui ne sont ni élus ni qualifiés
            resu["Eliminé"] = resu.apply(PremierTour.est_elimine, axis=1)
            # Si aucun des candidats n'est élu
            # et qu'il y n'y a pas au moins 2 candidats qualifiés,
            # on prend les 2 premiers candidats par nombre de voix,
            # et on qualifie ces candidats pour le 2nd tour
            if (resu[resu["Elu"]].shape[0] == 0) and (resu[resu["Qualifié"]].shape[0] < 2):
                deux_premiers = resu.sort_values(by="Voix", ascending=False)[:2].index
                resu.loc[deux_premiers, "Qualifié"] = True
                resu.loc[deux_premiers, "Eliminé"] = False
            self.resultat = resu


class SecondTour(Scrutin):

    def __init__(self, dept: str, circ: int, clos: bool = True) -> None:
        Scrutin.__init__(self, dept, circ, clos)
        t1 = PremierTour(self.dept, self.circ)
        t1.issue()
        self.resultat_t1 = t1.resultat

    def est_maintenu(self):
        resu_t1 = self.resultat_t1
        if resu_t1[resu_t1["Elu"]].shape[0] == 1:
            return False
        else:
            return True

    def issue(self):
        if self.est_maintenu():
            self.recup_resultat(tour=2)
            self.prepare_resultat()
            if self.clos:
                resu = self.resultat
                resu["Elu"] = False
                candidat_elu = resu.sort_values(by="Voix", ascending=False)[0].index
                resu.loc[candidat_elu, "Elu"] = True
                self.resultat = resu
        else:
            resu = self.resultat_t1
            resu = resu[resu["Elu"]]
            self.resultat = resu
