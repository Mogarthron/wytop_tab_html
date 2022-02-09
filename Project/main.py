from businnes_logic import *
import sys
from datetime import datetime as dt

from Models.Wydobycie.wydobycie_zmianowe import Dane_Do_wytopu, Wylewanie,  Raport_Wydobycia_Zmianowego, Drukuj_Raport_Do_Excella
from Models.Wydobycie.wydobycie_brutto import Wydobycie_Brutto
from Models.Wydobycie.raport_topiarza import Tabelka_z_Wydobyciem_po_baniakach, Wydobycie_Zmianowe, Raport_Topiarza



def main():    

    # bl = BusinessLogic()
    # bl.PoliczWydobycieNaDzien()

    

    Drukuj_Raport_Do_Excella("2022.2.1", "2022.2.7").Drukuj_Sformatowny_Raport_Wytopu("Wytop luty 2022")
    print(Dane_Do_wytopu("2022.2.1", "2022.2.7")[["Data", "Wydobycie_WG", "WE_1", "WE_2", "WE_3", "Wydobycie_WE", "Wydobycie_Calkowite", "Wydobycie_Brutto_Calkowite"]])
    # print(Tabelka_z_Wydobyciem_po_baniakach("2022.1.21", "2022.2.2"))
    # rtw = Raport_Topiarza("2022").Raport_Topiarza_Wanna("Elektrodowa")
    # print(rtw.loc[rtw["Czas Wpisu"] > dt(2022,2,2)])

    # wz = Wydobycie_Zmianowe(Raport_Topiarza(), dt(2022,2,2))    
    # for b in wz.Lista_Baniakow:
    #     print(b)
    # print(Wydobycie_Brutto("2022.1.1", "2022.1.12").Wydobycie_Brutto_Podsumowanie)
    # rwz = Raport_Wydobycia_Zmianowego()
    # print(rwz.rap_2017.info())
    # print(rwz.rap_2018_2021.info())
    # print(Wylewanie("2021.11.1", "2021.11.14").to_string(index=False))


if __name__ == "__main__":
    main()

