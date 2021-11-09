import numpy as np
from numpy import int16, float32
import pandas as pd
from datetime import datetime


class PostawionyBaniakWE:
    
    def __init__(self, numerBaniaka=None, receptura=0, czasZsypywania=0, zmI=0, zmII=0, zmIII=0):              
        """
       
        """
        self.NumerBaniaka = numerBaniaka
        self.Receptura = receptura
        self.WydobycieZmianowe = np.zeros(3, dtype=float32)


        self.WydobycieZmianowe[0] = zmI/czasZsypywania*self.Receptura
        self.WydobycieZmianowe[1] = zmII/czasZsypywania*self.Receptura
        self.WydobycieZmianowe[2] = zmIII/czasZsypywania*self.Receptura
        

class WydobycieNaDzien:

    ilosc_szkla_WG = int16(471)
    # ilosc_szkla_WE = float32(420)

    def __init__(self, daneDoWydobycia=None, obliczDzienneWydobycie=None):
        """
        daneDoWydobycia: wiersz z pliku Wydobycie_Zmianowe.json

        obliczDzienneWydobycie: słownik = {"DataZmiany", "IloscBaniakowWG", "WydobycieWE", "Wylewanie"}
        DataZmiany: string np: '2021.9.1'
        WydobycieWE: lista float'ów z warością wydobycia na poszczególnych zmianach
        Wylewanie: lista True False dla karzedj zmiany WG i WE np.: [False, False, False, False, False, True]
        """
       
        self.__wydobycie_WE = np.zeros(3, dtype=float32)   
        self.__we_wylewanie = np.zeros(3, dtype=float32)     
        self.DataWpisu = None
        self.WierszTabelki = dict()    
    
        if daneDoWydobycia:
            self.__DaneDOWydobycia(daneDoWydobycia)     

        if obliczDzienneWydobycie:
            self.__ObliczDzienneWydobycie(obliczDzienneWydobycie)
            
    def __ObliczDzienneWydobycie(self, obliczDzienneWydobycie):        
        
        ilosc_baniakow_WG=obliczDzienneWydobycie["Baniaki_WG"]       

        self.Wylewanie_WG = obliczDzienneWydobycie["Wylewanie"][:3]
        self.Wylewanie_WE = obliczDzienneWydobycie["Wylewanie"][3:] 

        self.__wydobycie_WE[0] = obliczDzienneWydobycie["Wydobycie_WE"][0]
        self.__wydobycie_WE[1] = obliczDzienneWydobycie["Wydobycie_WE"][1]
        self.__wydobycie_WE[2] = obliczDzienneWydobycie["Wydobycie_WE"][2] 

        self.__we_wylewanie[0] = self.__wydobycie_WE[0] if self.Wylewanie_WE[0] == False else 0
        self.__we_wylewanie[1] = self.__wydobycie_WE[1] if self.Wylewanie_WE[1] == False else 0
        self.__we_wylewanie[2] = self.__wydobycie_WE[2] if self.Wylewanie_WE[2] == False else 0

        self.Wydobycie_WG = ilosc_baniakow_WG * self.ilosc_szkla_WG  

        self.WG_1 = int16((self.__wydobycie_WE[0] / self.__we_wylewanie.sum()) * self.Wydobycie_WG) if self.Wylewanie_WE[0] == False else 0
        self.WG_2 = int16((self.__wydobycie_WE[1] / self.__we_wylewanie.sum()) * self.Wydobycie_WG) if self.Wylewanie_WE[1] == False else 0
        self.WG_3 = int16((self.__wydobycie_WE[2] / self.__we_wylewanie.sum()) * self.Wydobycie_WG) if self.Wylewanie_WE[2] == False else 0         

        self.Wydobycie_WE = self.__we_wylewanie.sum()
        
        self.WierszTabelki = {"Data": obliczDzienneWydobycie["Data"], "WG_1": self.WG_1, "WG_2": self.WG_2, "WG_3": self.WG_3, "Suma_WG": self.Wydobycie_WG, "WE_1": self.__wydobycie_WE[0], "WE_2": self.__wydobycie_WE[1], "WE_3": self.__wydobycie_WE[2], "Suma_WE": self.Wydobycie_WE}
        
    def __DaneDOWydobycia(self, daneDoWydobycia):

        if type(daneDoWydobycia["Data"]) == list:
            self.DataWpisu = datetime(daneDoWydobycia["Data"][0], daneDoWydobycia["Data"][1],daneDoWydobycia["Data"][2])
        else:
            self.DataWpisu = datetime.strptime(daneDoWydobycia["Data"], "%Y.%m.%d")

        self.Wylewanie_WG = daneDoWydobycia["Wylewanie"][:3]
        self.Wylewanie_WE = daneDoWydobycia["Wylewanie"][3:] 

        self.__wydobycie_WE[0] = daneDoWydobycia["Wydobycie_WE"][0]
        self.__wydobycie_WE[1] = daneDoWydobycia["Wydobycie_WE"][1]
        self.__wydobycie_WE[2] = daneDoWydobycia["Wydobycie_WE"][2] 

        self.__we_wylewanie[0] = self.__wydobycie_WE[0] if self.Wylewanie_WE[0] == False else 0
        self.__we_wylewanie[1] = self.__wydobycie_WE[1] if self.Wylewanie_WE[1] == False else 0
        self.__we_wylewanie[2] = self.__wydobycie_WE[2] if self.Wylewanie_WE[2] == False else 0

        if len(daneDoWydobycia["Wydobycie_WG"]) != 0:
            self.WG_1 = daneDoWydobycia["Wydobycie_WG"][0]
            self.WG_2 = daneDoWydobycia["Wydobycie_WG"][1]
            self.WG_3 = daneDoWydobycia["Wydobycie_WG"][2]

            self.Wydobycie_WG = self.WG_1 + self.WG_2 + self.WG_3
  
        else:
            ilosc_baniakow_WG=daneDoWydobycia["Baniaki_WG"]                       

            self.Wydobycie_WG = ilosc_baniakow_WG * self.ilosc_szkla_WG  

            self.WG_1 = int16((self.__wydobycie_WE[0] / self.__we_wylewanie.sum()) * self.Wydobycie_WG) if self.Wylewanie_WE[0] == False else 0
            self.WG_2 = int16((self.__wydobycie_WE[1] / self.__we_wylewanie.sum()) * self.Wydobycie_WG) if self.Wylewanie_WE[1] == False else 0
            self.WG_3 = int16((self.__wydobycie_WE[2] / self.__we_wylewanie.sum()) * self.Wydobycie_WG) if self.Wylewanie_WE[2] == False else 0 

        self.Wydobycie_WE = self.__we_wylewanie.sum()
        
        self.WE_1 =  self.__wydobycie_WE[0]
        self.WE_2 =  self.__wydobycie_WE[1]
        self.WE_3 =  self.__wydobycie_WE[2]     

        self.WierszTabelki = {"Data": self.DataWpisu.strftime("%Y.%m.%d"), "WG_1": self.WG_1, "WG_2": self.WG_2, "WG_3": self.WG_3, "Suma_WG": self.Wydobycie_WG, "WE_1": self.WE_1, "WE_2": self.WE_2, "WE_3": self.WE_3, "Suma_WE": self.Wydobycie_WE}
  
    
