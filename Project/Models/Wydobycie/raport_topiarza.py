from pandas import read_excel, Series, DataFrame, to_datetime, to_timedelta, merge
import pandas as pd
from numpy import float64, zeros, array, datetime64, NaN
from datetime import datetime, timedelta
import calendar

from Models.Zasypnik.zasypnik import PracaZasypnika as pz
from Models.Receptura.receptura import Zestaw
from Models.Receptura.sklady_receptur import wg, we
from Models.baniaki import Wydobycie_z_baniaka, Baniak
from .wydobycie_brutto import Wydobycie_Brutto


class Raport_Topiarza:
    
    bazowa_gestosc_szkla_opalowego = 2.33 #g/cm3
    bazowa_powierzchnia_wyrobowki_WE = 5000 #cm3

    def __init__(self, rok_raportu:str):
        """
        Clasa wyświetlająca raport toparza z pliku .xlsx

        rok_raportu: nawa arkusza z raportem bez rozszeżenia np.: 2021, 2022 
        """
        from Models import scierzki_do_plikow
        self.__rap_top = read_excel(scierzki_do_plikow["Raport_Topiarza"][rok_raportu])          

        self.__rap_top["Baniak_WG"] = self.__rap_top["Baniak_WG"].astype(float64)
        self.__rap_top["Czas Wpisu"] = self.__rap_top.apply(lambda x: Czas_wpisu(x["Data"], x["Godzina"]), axis=1)

        czas_wpisu_nowy = [self.__rap_top["Czas Wpisu"][0] + timedelta(hours=x) for x in self.__rap_top["Czas Wpisu"].index]

        self.__rap_top["Czas Wpisu"] = Series(data=czas_wpisu_nowy)
        self.__rap_top["Zmiana"] = self.__rap_top["Czas Wpisu"].apply(Zmiana)
        self.__rap_top["Data Zmiany"] = self.__rap_top["Czas Wpisu"].apply(Data_zmiany)   

        self.__rap_top.drop(["Data", "Godzina", "Uwagi", "odciąg L/P"], axis=1, inplace=True)      

        self.__rap_top["Postawienie Baniaka WE"] = self.__rap_top["Czas Wpisu"] + to_timedelta(self.__rap_top["Baniak_WE"], unit="m")

        self.__rap_top["Przerwa Pracy Zasypnika WE"] = 90

        self.__rap_top["Ruznica poziomu"] = -self.__rap_top["Poziom WE"].diff()
        self.__rap_top["Naplyw szkla"] = self.__rap_top["Ruznica poziomu"].apply(lambda x: 
                        Naplyw_szkla(x, self.bazowa_powierzchnia_wyrobowki_WE, self.bazowa_gestosc_szkla_opalowego))

    def Raport_Topiarza_Wanna(self, wanna:str, **kwargs):

        _kolumny = ["Czas Wpisu","Data Zmiany", "Zmiana"]

        if wanna == "Elektrodowa":
           _kolumny += ["Zasyp WE", "Przerwa Pracy Zasypnika WE", "Poziom WE", 
                        "Ruznica poziomu", "Naplyw szkla", 
                        "Postawienie Baniaka WE", "Moc"]
        elif wanna == "Gazowa":
           _kolumny += ["Zasyp WG", "Poziom WG", "Baniak_WG", "Gaz [Nm3/h]"]
        else:
            return "Zła nazwa wanny"

        return self.__rap_top[_kolumny]


class Wydobycie_Zmianowe:    

    dodatek_stluczki_do_baniaka_WG = 270 #kg

    def __init__(self, raport_topiarza:Raport_Topiarza, data_zmiany):
        """
        data_zmiany: datetime 
        """
        
        self.Data_Raportu = data_zmiany

        rte = raport_topiarza.Raport_Topiarza_Wanna("Elektrodowa")  

        zakres_raportu = (rte["Data Zmiany"] >= (data_zmiany - timedelta(days=1))) & \
                            (rte["Data Zmiany"] <= (data_zmiany + timedelta(days=1)))

        raport_topiarza_wanna_El = rte.loc[zakres_raportu]

        zakres_postawienia_baniakow_we = raport_topiarza_wanna_El.resample('D', on='Data Zmiany')['Postawienie Baniaka WE'].agg(['first','last'])
        self.Zakres_postawienia_baniakow_we = zakres_postawienia_baniakow_we

        baniak_poczatkowy = to_datetime(zakres_postawienia_baniakow_we[zakres_postawienia_baniakow_we.index == (data_zmiany - timedelta(days=1))]["last"].values[0])
        baniak_koncowy = to_datetime(zakres_postawienia_baniakow_we[zakres_postawienia_baniakow_we.index == (data_zmiany + timedelta(days=1))]["first"].values[0])

        warunek_baniaki_we = ((rte["Postawienie Baniaka WE"] >= baniak_poczatkowy) & 
                                (rte["Postawienie Baniaka WE"] <= baniak_koncowy))
   

        lista_indeksow = [i for i in rte.loc[warunek_baniaki_we]["Postawienie Baniaka WE"].index]

        lista_Baniakow = list()
        p=0

        while p < len(lista_indeksow)-1:
            
            lista_Baniakow.append(
                Wydobycie_z_baniaka(data_zmiany, 
                                    to_datetime(raport_topiarza_wanna_El.loc[raport_topiarza_wanna_El.index == lista_indeksow[p]]["Postawienie Baniaka WE"].values[0]),  
                                    to_datetime(raport_topiarza_wanna_El.loc[raport_topiarza_wanna_El.index == lista_indeksow[p+1]]["Postawienie Baniaka WE"].values[0]), 
                                    Baniak(numer="1", data_przygotowania="2021.10.5", nastawa=Zestaw(sklad_surowcowy=we)*2)))
            p += 1

        self.Lista_Baniakow = lista_Baniakow
        self.Wydobycie_WE = sum([x.WydobycieNaZmiane for x in lista_Baniakow])  
        
        warunek_baniaki_WG = raport_topiarza.Raport_Topiarza_Wanna("Gazowa")["Data Zmiany"] == self.Data_Raportu

        self.Baniaki_WG = raport_topiarza.Raport_Topiarza_Wanna("Gazowa").loc[warunek_baniaki_WG].groupby(["Data Zmiany"]).sum()["Baniak_WG"].values[0]


    @property
    def Wiersz_Do_Raportu(self):

        wiersz = {
            "Data": datetime.strftime(self.Data_Raportu, '%Y.%m.%d'),
            "WE_1": self.Wydobycie_WE[0],
            "WE_2": self.Wydobycie_WE[1],
            "WE_3": self.Wydobycie_WE[2],
            # "Wydobycie_WG": self.Wydobycie_WG,
            "Baniaki_WG": self.Baniaki_WG
        }

        return wiersz

    def __str__(self) -> str:
        
        return f"{datetime.strftime(self.Data_Raportu, '%Y.%m.%d')}, wydobycie WE: {self.Wydobycie_WE}, Wydobycie WG: {self.Baniaki_WG*471}"

    
def Czas_wpisu(d,g):

    return d + timedelta(hours=g)

def Zmiana(n):

    h = n.hour

    if h >= 6 and h < 14:
        return "R"
    elif h >= 14 and h < 22:
        return "P"
    else: return "N"

def Data_zmiany(d):
    
    d1 = datetime(d.year, d.month, d.day, hour=6)
    
    try:
        d2 = datetime(d.year, d.month, d.day + 1, hour=6)
    except:
        d2 = datetime(d.year, d.month + 1, 1, hour=6)


    if d >= d1 and d < d2:
        return datetime(d.year, d.month, d.day)
    
    if d.day <= 1:
        return datetime(d.year, d.month-1, calendar.monthrange(d.year, d.month-1)[1])
    else: 
        return datetime(d.year, d.month, d.day - 1)

def Czas_postawienia_Baniaka_WE(d,m):
    
    return datetime(d.year, d.month, d.day, d.hour) + timedelta(minutes=m)

def Naplyw_szkla(n, powierzchnia_wyrobowki, gestosc_szkla):
    if n != NaN:
        return n * powierzchnia_wyrobowki * gestosc_szkla /1000
    return 0.0

def Czas_sypania_w_ciagu_godziny(z, p):
    czas = pz(p, z)
    return czas.Czas_sypania_w_ciagu_godziny




def Tabelka_z_Wydobyciem_po_baniakach(od:str, do:str, rok_raportu:str):
    od = datetime.strptime(od, "%Y.%m.%d")
    do = datetime.strptime(do, "%Y.%m.%d")

    rt = Raport_Topiarza(rok_raportu)

    zakres_dat = [od + timedelta(days=x) for x in range(0, (do-od).days+1)]

    wydobycie = [Wydobycie_Zmianowe(rt, d).Wiersz_Do_Raportu for d in zakres_dat]                

    df = DataFrame(wydobycie)
    # df = DataFrame([Wydobycie_Zmianowe(rt, d).Wiersz_Do_Raportu for d in [od + timedelta(days=x) for x in range(0, (do-od).days+1)]])
    df["Data"] = to_datetime(df["Data"])
    
    return df
