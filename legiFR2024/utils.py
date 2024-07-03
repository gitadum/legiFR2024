# -*- coding: utf-8 -*-

import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

def parsage_nombres(nombre: str) -> float|int:
    """
    Fonction de prétraitement des nombres lus à partir à partir des tableaux web
    """
    trans = {" ": "", ",": ".", "\u202f": ""}
    try:
        nombre_parse = float(nombre.translate(str.maketrans(trans)))
    except:
        nombre_parse = nombre
    # Si le nombre s'y prête on le convertit en valeur entière
    nombre_parse = int(nombre_parse) if nombre_parse % 1 == 0 else nombre_parse
    return nombre_parse

def lire_tables_web(url: str) -> list[pd.DataFrame]:
    """
    Lecture des tableaux de données présents sur une page web depuis une URL
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table")
    dfs = [pd.read_html(StringIO(str(table)), header=None)[0] for table in tables]
    return dfs
