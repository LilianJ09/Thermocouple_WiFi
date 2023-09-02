"""
JAOUANNE Lilian & GARCON Bastian PEI2   04-2023
Script contenant des fonctions, importé dans le Soft Application Thermocouple WiFI
"""

import time
import os
import math

def Valide_extension(nom_fichier):
    # Lire les 4 derniers caractères de la chaîne pour connaitre l extension ou a defaut la non existance d extension
    extension = nom_fichier[-4:]
    if(extension != '.csv'):
        nom_fichier = nom_fichier + ".csv"
    return nom_fichier

def Nommer():
    # Chemin du fichier CSV à créer demande a l utilisateur
    nom_fichier = input("Entrez le nom du fichier à créer : ")
    nom_fichier = Valide_extension(nom_fichier)
    # Vérifier si le fichier existe
    while os.path.isfile(nom_fichier):
        print("Un fichier du même nom existe déjà, voulez vous de remplacer ? : ")
        confirm = 'a'#initialisation different de o O n et N 1par defaut
        while(confirm not in ['o','O','n','N']):
            confirm = input("Tapper O (oui) ou N (non) : ")
            if(confirm == 'o' or confirm == 'O'):
                os.remove(nom_fichier)
                return nom_fichier
            elif(confirm == 'n' or confirm == 'N'):
                nom_fichier = input("Entrez un autre nom pour le fichier à créer : ")
                nom_fichier = Valide_extension(nom_fichier)
    return nom_fichier

def compare_strings(s1, s2):
    # Extraire les 10 premiers caractères des deux chaînes
    s1_prefix = s1[:10]
    s2_prefix = s2[:10]
    # Comparer les deux préfixes de chaîne
    if s1_prefix == s2_prefix:
        return True
    else:
        return False
    
def TraitementData(data, start_time):
    TensionmV,TempSC = data.strip().split(',')
    current_time = time.time() - start_time
    millisecondes = int(current_time * 1000)
    print(f'TensionmV: {TensionmV} mV, Temps: {millisecondes}')
    TensionmV = format(TensionmV).replace('.', ',')#remplacer les points par des vigules pour excel
    nombres = [str(millisecondes),str(TensionmV)]
    return nombres

"""Coefficient Tension -> Température
cV[0][0 à 9] : tensions allants de -5.891 à 0 mV (-200 à 0 °C)
cV[1][0 à 9] : tensions allants de 0 à 20.644 mV (0 à 500 °C)
cV[2][0 à 9] : tensions allants de 20.644 à 54.886 mV (500 à 1372 °C)"""

CoeffTension = [
    [0,
    2.5173462E+01,
    -1.1662878,
    -1.0833638,
    -8.9773540E-01,
    -3.7342377E-01,
    -8.6632643E-02,
    -1.0450598E-02,
    -5.1920577E-04,
    0],
    [0,
    2.508355E+01,
    7.860106E-02,
    -2.503131E-01,
    8.315270E-02,
    -1.228034E-02,
    9.804036E-04,
    -4.413030E-05,
    1.057734E-06,
    -1.052755E-08],
    [-1.318058E+02,
    4.830222E+01,
    -1.646031,
    5.464731E-02,
    -9.650715E-04,
    8.802193E-06,
    -3.110810E-08,
    0,
    0,
    0]
    ]

"""Coefficient Température -> Tension
cC[0][0 à 9] : températures allants -270 à 0 °C
cC[1][0 à 9] : températures allants 0 à 1372 °C"""

CoeffTemperature = [[0,
    0.394501280250E-1,
    0.236223735980E-4,
    -0.328589067840E-6,
    -0.499048287770E-8,
    -0.675090591730E-10,
    -0.574103274280E-12,
    -0.310888728940E-14,
    -0.104516093650E-16,
    -0.198892668780E-19,
    -0.163226974860E-22],
    [-0.176004136860E-1,
    0.389212049750E-1,
    0.185587700320E-4,
    -0.994575928740E-7,
    0.318409457190E-9,
    -0.560728448890E-12,
    0.560750590590E-15,
    -0.320207200030E-18,
    0.971511471520E-22,
    -0.121047212750E-25,
    0]
    ]

#coefficient d'exponentielle pour les températures supérieures à 0
a = [0.1185976 , -0.1183432E-3 , 0.1269686E+3]

#renvoie la tension en fonction de la température
def ConvertTemp_Tension(temp):
    result = 0
    i = 0
    if (temp <= 0):
        while(i < 11):
            result = result + CoeffTemperature[0][i]*pow(temp , i)
            i+=1

    else:
        while(i < 10):
            result = result + CoeffTemperature[1][i]*pow(temp , i)
            i+=1
        result = result + a[0] * math.exp(a[1] * pow((temp - a[2]) , 2))
        
    return(result)

#renvoie la température en fonction de la tension
def ConvertTension_Temp(Tension):
    result = 0
    i = 0
    if (Tension <= 0):
        while(i < 10):
            result = result + CoeffTension[0][i]*pow(Tension , i)
            i+=1
            
    elif (Tension <= 20.664):
        while(i < 10):
            result = result + CoeffTension[1][i]*pow(Tension , i)
            i+=1
    
    else:
        while(i < 10):
            result = result + CoeffTension[2][i]*pow(Tension , i)
            i+=1
            
    return(result)