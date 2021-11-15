import pandas as pd
import json


from Models.Wydobycie.raport_topiarza import Tabelka_z_Wydobyciem_po_baniakach
from Models.Wydobycie.wydobycie_brutto import Wydobycie_Brutto
from Models import scierzki_do_plikow

def Wydobycie_Zmianiowe():
    
    df = pd.read_excel(scierzki_do_plikow["Dane_Do_Wydobycia"])

    df.drop(["Unnamed: 8", "Unnamed: 9", "Unnamed: 10"], axis=1, inplace=True)
    
    print(df.tail(30))


def Dane_Do_wytopu(od:str, do:str):
    """
    Raport Wytopu na podstawie Raportu Topiarza i Raportera produkcji od 1 listopada 2021
    od,do : format daty RRRR.M.D
    """
    w_brutto = Wydobycie_Brutto(od, do)

    sbdw = w_brutto.Szklo_bezbarwne_do_wytopu 

    def Szklo_bezb_z_produkcji(Zmiana, Mnoznik_Korygujacy_Produkcje=1.2):
        _Zmiana = f"WG_{Zmiana}"
        szklo_bezb_z_produkcji = pd.DataFrame({"Data": pd.date_range(od,do)})
        szklo_bezb_z_produkcji = pd.merge(szklo_bezb_z_produkcji, sbdw.loc[sbdw["Zmiana"] == Zmiana][["Dzm", "Szklo WG"]], how="left", left_on="Data", right_on="Dzm")
        szklo_bezb_z_produkcji.drop("Dzm", axis=1, inplace=True)
        szklo_bezb_z_produkcji["Szklo WG"] = szklo_bezb_z_produkcji["Szklo WG"] * Mnoznik_Korygujacy_Produkcje
        szklo_bezb_z_produkcji.columns = ["Data",_Zmiana] #f"WG_{Zmiana}"]
        szklo_bezb_z_produkcji.fillna(0, inplace=True)
        return szklo_bezb_z_produkcji.groupby(["Data"]).sum()

    
    tabeleczka = pd.merge(Szklo_bezb_z_produkcji("R"), Szklo_bezb_z_produkcji("P"), how="inner", on="Data")
    tabeleczka = pd.merge(tabeleczka, Szklo_bezb_z_produkcji("N"), how="inner", on="Data")
   
    
    tabeleczka = pd.merge(tabeleczka, Tabelka_z_Wydobyciem_po_baniakach(od, do), how="inner", on="Data")
    tabeleczka = pd.merge(tabeleczka, Wylewanie(od,do), how="inner", on="Data")

    def Wydobycie_WE(n):
        if type(n["Wylewanie"]) == list and len(n["Wylewanie"]) == 6:
            w_we = 0 if n["Wylewanie"][3] == True else n["WE_1"]
            w_we += 0 if n["Wylewanie"][4] == True else n["WE_2"]
            w_we += 0 if n["Wylewanie"][5] == True else n["WE_3"]

            return w_we
        if type(n["Wylewanie"]) == list and len(n["Wylewanie"]) == 2:
            w_we = 0 if n["Wylewanie"][1] == True else n["WE_1"]
            w_we += 0 if n["Wylewanie"][1] == True else n["WE_2"]
            w_we += 0 if n["Wylewanie"][1] == True else n["WE_3"]

            return w_we
        else:
            return n["WE_1"] + n["WE_2"] + n["WE_3"]


    def Wydobycie_WG(n, Zmiana):

        zmiany = {"R": ["WG_R", "WE_1", 0],
                  "P": ["WG_P", "WE_2", 1],
                  "N": ["WG_N", "WE_3", 2]}

        war = zmiany[Zmiana]

        if type(n["Wylewanie"]) == list and len(n["Wylewanie"]) == 6:
                
            if n["Wylewanie"][war[2]] == True:
                return 0
            elif n["Wylewanie"][war[2]+3] == True:
                return n[war[0]]
            else:
                return n[war[0]] + n[war[1]] * 3 
        
        elif type(n["Wylewanie"]) == list and len(n["Wylewanie"]) == 2:
                
            if n["Wylewanie"][0] == False:
                return 0
            # elif n["Wylewanie"][war[2]+1] == True:
            #     return n[war[0]]
            else:
                return n[war[0]] + n[war[1]] * 3

        elif n["Wylewanie"]:
            return 0
        else:
            return n[war[0]] + n[war[1]] * 3 


    tabeleczka["Wydobycie_WE"] = tabeleczka.apply(lambda x: Wydobycie_WE(x), axis=1)
    tabeleczka["WG_1"] = tabeleczka.apply(lambda x: Wydobycie_WG(x, "R"), axis=1)
    tabeleczka["WG_2"] = tabeleczka.apply(lambda x: Wydobycie_WG(x, "P"), axis=1)
    tabeleczka["WG_3"] = tabeleczka.apply(lambda x: Wydobycie_WG(x, "N"), axis=1)
    tabeleczka["Wydobycie_WG"] = tabeleczka["WG_1"] + tabeleczka["WG_2"] + tabeleczka["WG_3"]
    
    kolumny = ["Data", "WG_1", "WG_2", "WG_3", "Wydobycie_WG", "WE_1", "WE_2", "WE_3", "Wydobycie_WE"]
    # return tabeleczka[kolumny]
    return tabeleczka


def Wylewanie(od,do):

    with open(scierzki_do_plikow["Wylewanie"]) as w:
        dane_Wylewanie = json.load(w)["Zmiany"]        

    wylewanie = pd.DataFrame(dane_Wylewanie)
    wylewanie["Data"] = pd.to_datetime(wylewanie["Data"])
    df = pd.DataFrame({"Data": pd.date_range(od, do)})

    df = pd.merge(df, wylewanie, how="left", on="Data")
    df["Wylewanie"].fillna(False, inplace=True)

    return df
