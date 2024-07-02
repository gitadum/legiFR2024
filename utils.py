# -*- coding: utf-8 -*-

import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

def parsage_nombres(nombre: str) -> float|int:
    trans = {" ": "", ",": ".", "\u202f": ""}
    try:
        nombre_parse = float(nombre.translate(str.maketrans(trans)))
    except:
        nombre_parse = nombre
    nombre_parse = int(nombre_parse) if nombre_parse % 1 == 0 else nombre_parse
    return nombre_parse

def lire_tables_web(url: str) -> list[pd.DataFrame]:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table")
    dfs = [pd.read_html(StringIO(str(table)), header=None)[0] for table in tables]
    return dfs
