from datetime import datetime
from numpy import array, float32
import json
import os 

class Zestaw:

    def __init__(self, sklad_surowcowy=None, sklad_tlenkowy=None,  **stluczka):
              

        with open("E:/Biaglass/Wytop/Wydobycie zmianowe/wytop_tab_html/Project/Data/Surowce.json", "r") as f:
            dane = json.load(f)
        
        self.__sposob_inicjalizacji = None

        self.tlenki = dane["Tlenki"]
        self.surowce = dane["Sklady_surowcow"]
        if sklad_surowcowy != None:
            self.__sposob_inicjalizacji = "surowce"
            self.Waga_skladnikow = array(list(sklad_surowcowy.values()), float32).sum()            
            self.Skladniki_receptury = sklad_surowcowy
        
        elif sklad_tlenkowy != None:
            self.__sposob_inicjalizacji = "tlenki"
            self.Waga_skladnikow = array(list(sklad_tlenkowy.values()), float32).sum()            
            self.Skladniki_receptury = sklad_tlenkowy
           

    @property
    def Ilosc_tlenkow_w_nastawie(self):
        
        skladTlenkowy = dict()

        if self.__sposob_inicjalizacji == "surowce":
            for surowiec in self.Skladniki_receptury:            
                for tlenek in self.surowce[surowiec]:

                    if tlenek in skladTlenkowy:
                        skladTlenkowy[tlenek] += self.Skladniki_receptury[surowiec]*self.surowce[surowiec][tlenek]
                    else:
                        skladTlenkowy[tlenek] = self.Skladniki_receptury[surowiec]*self.surowce[surowiec][tlenek]
            return skladTlenkowy

        else: 

            return self.Skladniki_receptury 

    @property
    def Ilosc_tlenkow_w_szkle(self):

        skladTelnkowySzkla = dict()
        for tlenek in self.Ilosc_tlenkow_w_nastawie:
            stan_w_szkle = self.tlenki.get(tlenek)["stan_w_szkle"]
            zawartosc_w_szkle = (1 - self.tlenki.get(tlenek)["lotnosc"]) * self.Ilosc_tlenkow_w_nastawie[tlenek]
            if stan_w_szkle != "gazowy":                
                skladTelnkowySzkla[tlenek] = zawartosc_w_szkle
        
        return skladTelnkowySzkla

    @property
    def Ilosc_szkla_z_jednego_zestawu(self):
        return array(list(self.Ilosc_tlenkow_w_szkle.values()), float32).sum()

    def __mul__(self, other):
        
        pomnorzony_sklad = {k: self.Ilosc_tlenkow_w_szkle.get(k, 0) * other for k in set(self.Ilosc_tlenkow_w_szkle)}

        return pomnorzony_sklad

    def __add__(self, other):
        if type(other) == Zestaw:
            return {k: self.Ilosc_tlenkow_w_szkle.get(k, 0) + other.Ilosc_tlenkow_w_szkle.get(k, 0) for k in set(self.Ilosc_tlenkow_w_szkle) | set(other.Ilosc_tlenkow_w_szkle)}
        elif type(other) == dict:
                return {k: self.Ilosc_tlenkow_w_szkle.get(k, 0) + other.get(k, 0) for k in set(self.Ilosc_tlenkow_w_szkle) | set(other)}
        
    def __str__(self):
        return f"{self.Skladniki_receptury}"


class Stluczka:
    def __init__(self, *sklad, jeden_skladnik=None):

        if type(jeden_skladnik) == Zestaw:     
            self.Sklad_stluczki = jeden_skladnik.Ilosc_tlenkow_w_szkle
            
        else:
           
            for s in range(len(sklad[0])-1):
                self.Sklad_stluczki =  sklad[0][s] + sklad[0][s+1]
            
        
        waga_skladnikow = array(list(self.Sklad_stluczki.values()), float32).sum()

        for tlenek in self.Sklad_stluczki:
            self.Sklad_stluczki[tlenek] = self.Sklad_stluczki[tlenek]/waga_skladnikow
        
    def __mul__(self, other):
        return {k: self.Sklad_stluczki.get(k, 0) * other for k in set(self.Sklad_stluczki)}
    
    def __str__(self):
        return f"{self.Sklad_stluczki}"


class Nastawa_surowcowa:

    def __init__(self, receptura, dataprzygotowania=None, numer=None):
        
        self.Data_przygotowania = dataprzygotowania
        self.Numer_nastawy = numer
        self.Receprura = receptura
        self.Surowce = dict()
        self.Stluczka = dict()

    def Dodaj_surowiec(self, *surowiec):
        if len(surowiec) == 0: 
            for s in self.Receprura:
                print(s)
                waga_nastawy = input("Waga nastawy: ")
                waga_nastawy = waga_nastawy.replace(",", ".")
                self.Surowce[s] = float(waga_nastawy)
        else:
            self.Surowce[surowiec[0][0]] = float(surowiec[0][1])
        


    def __add__(self, other):
        return {k: self.Surowce.get(k, 0) + other.Surowce.get(k, 0) for k in set(self.Surowce) | set(other.Surowce)}
      



