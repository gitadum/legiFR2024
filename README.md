# LegiFR2024

Utilitaire Python pour lire les résultats des élections législatives françaises de 2024 depuis le [site du ministère de l'intérieur](https://www.resultats-elections.interieur.gouv.fr/legislatives2024).

## Installation

### Prérequis

* Python 3.12
* Pip 24.1

### Pas à pas

```sh
git clone https://github.com/gitadum/legiFR2024.git
cd legiFR2024
pip install -r requirements.txt
pip install .
```

## Utilisation

### Exemple

```python
>>> from legiFR2024 import PremierTour
>>> circo = PremierTour(dept="01", circ=1) # 1er tour de la 1ère circ. de l'Ain
>>> circo.issue() # Détermine l'issue du scrutin à partir des votes
>>> print(circo.resultat)
    Liste des candidats Nuance   Voix  Tot. Exprimés  Tot. Inscrits  \
0   M. Christophe MAÎTRE     RN  23819          60495          86843   
1       M. Xavier BRETON     LR  14495          60495          86843   
2   M. Sébastien GUERAUD     UG  14188          60495          86843   
3  M. Vincent GUILLERMIN    ENS   7063          60495          86843   
4           M. Éric LAHY    EXG    419          60495          86843   
5      M. Michael MENDES    DSV    314          60495          86843   
6       M. Cyril VINCENT    DSV    197          60495          86843   

  Pct. Exprimés Pct. Inscrits  Eliminé    Elu  Qualifié  
0      0.393735      0.274277    False  False      True  
1      0.239607       0.16691    False  False      True  
2      0.234532      0.163375    False  False      True  
3      0.116753      0.081331     True  False     False  
4      0.006926      0.004825     True  False     False  
5      0.005191      0.003616     True  False     False  
6      0.003256      0.002268     True  False     False  
```
