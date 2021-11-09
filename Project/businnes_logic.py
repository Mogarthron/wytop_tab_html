import json
import pandas as pd
import numpy as np
from datetime import datetime 

from Models.policz_wydobycie import WydobycieNaDzien, PostawionyBaniakWE
from Models.Receptura.receptura import Zestaw
from Models.Receptura.sklady_receptur import we
from Models.baniaki import Wydobycie_z_baniaka, Baniak


class BusinessLogic:

    def __init__(self):
        # self.__path = "Wydobycie_Zmianowe.json"
        # self.__path = "wydobycie_zmianowe_1.json"

        # with open(self.__path, "r") as file:
        #     self.__dic = json.load(file) 

        self.WydobycieWE = np.zeros(3, np.float32)
        self.BaniakiWG = None
        self.DataZmiany = None

    def __DodajDaneDoRaportu(self, wierszTableki):

        with open(self.__path,'r+') as f:
        
            daneZPliku = json.load(f)
            daneZPliku["daneDoWydobycia"].append(wierszTableki)
            f.seek(0)
            json.dump(daneZPliku, f, indent = 3)

    def __DodajBaniakiDoWydobycia(self, receptura = 0):
    
        numerBaniaka= input("Numer Baniaka: ")

        if receptura == 0:
            receptura = input("Receptura (ile szkła): ")

        _czasZsypywania = input("Czas zsypywania zestawu w godzinach: ")
        listaCzasuZasypu = _czasZsypywania.split(",")

        czasZsypywania = listaCzasuZasypu[0]

        if len(listaCzasuZasypu) > 1:
            zmI = int(listaCzasuZasypu[1])
            zmII = int(listaCzasuZasypu[2])
            zmIII = int(listaCzasuZasypu[3])
        else:
            _zmI = input("ile godzin na pierwszej zmianie: ")
            zmI = 0 if _zmI == "" else int(_zmI)

            _zmII = input("ile godzin na drugiej zmianie: ")
            zmII = 0 if _zmII == "" else int(_zmII)

            _zmIII = input("ile godzin na trzeciej zmianie: ")
            zmIII = 0 if _zmIII == "" else int(_zmIII)

        baniak= {"numerBaniaka": numerBaniaka, "receptura": np.float32(receptura), "czasZsypywania": int(czasZsypywania), "zmI": zmI, "zmII": zmII, "zmIII": zmIII}
        dodacNastepnyBaniak = True if input("Czy dodać nastepny baniak (T/t - Tak):").upper() == "T" else False 
        
        return [baniak, dodacNastepnyBaniak]

    def PoliczWydobycieNaDzien(self):
        DataRaportu = input("Data raportu (yyyy.mm.dd): ")

        self.DataZmiany = DataRaportu

        IloscBaniakowWG = int(input("Ile baniaków WG: "))
        self.BaniakiWG = IloscBaniakowWG

        _wylewanieNaZmianach = input("Wylewanie na zmianach t/f dla karzedej zmiany: ")
        _wylewanieNaZmianach = _wylewanieNaZmianach.split(",")
        WylewanieNaZmianach = list()
        if len(_wylewanieNaZmianach) != 1:
            for w in _wylewanieNaZmianach:
                wylewanie = False if w == "f" else True
                WylewanieNaZmianach.append(wylewanie)
        elif len(_wylewanieNaZmianach) == 1:
            # print("drugi if")
            # if _wylewanieNaZmianach == "ft":
            #     WylewanieNaZmianach = [False, False, False, True, True, True]
            if _wylewanieNaZmianach[0] != "t" or _wylewanieNaZmianach[0] == "":
                WylewanieNaZmianach = [False, False, False, False, False, False]            
            else: 
                WylewanieNaZmianach = [True, True, True, True, True, True]
        
        # print(WylewanieNaZmianach)
        self.PoliczWydobycieWE()
        obliczDzienneWydobycie = {"Data": DataRaportu, "Baniaki_WG": IloscBaniakowWG, "Wydobycie_WE": self.WydobycieWE, "Wylewanie": WylewanieNaZmianach}

        wnd = WydobycieNaDzien(obliczDzienneWydobycie=obliczDzienneWydobycie)
        print(wnd.WierszTabelki)

        nowyWierszTabelki = wnd.WierszTabelki
        nowyWierszTabelki["Wylewanie"] = WylewanieNaZmianach
     

    def PoliczWydobycieWE(self):   
        print("Reczne wpisywanie baniaków: wpisujesz ile godzin dany baniaka schodził a nastepnie dopisujesz ile schodził na poszczegóncyh zmianach")
        wpisywacBaniakiRecznie = input("Czy wpisywac baniaki recznie? (t/n): ")

        if wpisywacBaniakiRecznie.upper() == "T":

            baniaki = list()
            wydobycieZmianowe = np.zeros(3, dtype=np.float32)

            _iloscSzklaZBaniaka = input("Ile szkła z baniaka (Globalnie): ")
            iloscSzklaZBaniaka = 0 if _iloscSzklaZBaniaka == "" else int(_iloscSzklaZBaniaka)
    
            dodacNastepnyBaniak = True
            while dodacNastepnyBaniak:
                b =  self.__DodajBaniakiDoWydobycia(receptura=iloscSzklaZBaniaka)
                baniaki.append(PostawionyBaniakWE(b[0]["numerBaniaka"], b[0]["receptura"], b[0]["czasZsypywania"], b[0]["zmI"], b[0]["zmII"], b[0]["zmIII"]))
                dodacNastepnyBaniak = b[1]       
            
            for b in baniaki:
                print(b.NumerBaniaka, b.WydobycieZmianowe)
                wydobycieZmianowe += b.WydobycieZmianowe            

            print(f"Wydobycie Zmianowe: zmI: {wydobycieZmianowe[0]}, zmII: {wydobycieZmianowe[1]}, zmIII: {wydobycieZmianowe[2]}.\nWydobycie całkowite: {wydobycieZmianowe.sum()}")
            self.WydobycieWE = wydobycieZmianowe
        else:

            szklo_z_baniaka_we = Baniak(numer="1", data_przygotowania="2021.10.5", nastawa=Zestaw(sklad_surowcowy=we)*2)
            baniaki = list()
            wydobycie_z_baniaka = list()

            print(f"Wpisac czas postawiania baniaków dla dnia {self.DataZmiany}")
            print("Format daty: yyyy.m.d h:m")
          
            i = 1
            while True:
                czasPostawienia = input(f"czas postawiania baniaka nr {i}: ")
                baniaki.append(czasPostawienia)
                i += 1
                dodacBaniak = input("Czy dodać baniak?? t/n: ")
                if dodacBaniak.upper() == "N":
                    break

            b=0
            while b < len(baniaki)-1:

                wydobycie_z_baniaka.append(Wydobycie_z_baniaka(dataZmiany=self.DataZmiany, czasPostawienia=baniaki[b], czasZdjecia=baniaki[b+1], iloscSzklaZBaniaka=szklo_z_baniaka_we).WydobycieNaZmiane)
                b += 1


            self.WydobycieWE = sum(wydobycie_z_baniaka)
            print(baniaki)
            print(self.WydobycieWE, self.WydobycieWE.sum())

    # def TabelkaZWydobyciem(self, html=False):

    #     rows = list()

    #     for i in self.__dic["daneDoWydobycia"]:
    #         wnd = WydobycieNaDzien(daneDoWydobycia=i)
            
    #         rows.append(wnd.WierszTabelki)

    #     df = pd.DataFrame(rows)
        
    #     df["Data"] = pd.to_datetime(df["Data"])

    #     sumaWydobyciaWG = df["WG_1"].sum()+df["WG_2"].sum()+df["WG_3"].sum()
    #     sumaWydobyciaWE = df["Suma_WE"].sum()
    #     sum_WG = f"Suma_WG {sumaWydobyciaWG}kg"
    #     sum_WE = f"Suma_WE {sumaWydobyciaWE:.0f}kg"

    #     columns = ["Data","WG_1", "WG_2", "WG_3", sum_WG, "WE_1", "WE_2", "WE_3", sum_WE]
    #     columns_html = ["Data","WG_1", "WG_2", "WG_3", "Suma_WG", "WE_1", "WE_2", "WE_3", "Suma_WE"]

    #     pd.options.display.float_format = '{:.0f}'.format

    #     if html:
    #         df.columns = columns_html
    #         return df
    #     else:
    #         df.columns = columns
    #         return df
    
    # def TabelkaZWyleaniem(self):     

    #     wylewanie = list()
    #     for i in self.__dic["daneDoWydobycia"]:
    #         wylewanie.append([i["Data"], 
    #                             i["Wylewanie"][0], 
    #                             i["Wylewanie"][1], 
    #                             i["Wylewanie"][2], 
    #                             i["Wylewanie"][3], 
    #                             i["Wylewanie"][4], 
    #                             i["Wylewanie"][5]])

    #     df = pd.DataFrame(wylewanie)
    #     df.columns= ["Data", "WG_1", "WG_2", "WG_3", "WE_1", "WE_2", "WE_3"]
    #     return df
