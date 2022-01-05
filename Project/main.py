from businnes_logic import *

from Models.Wydobycie.wydobycie_zmianowe import Dane_Do_wytopu, Wylewanie, Wydobycie_Zmianiowe, Raport_Wydobycia_Zmianowego, Drukuj_Raport_Do_Excella
from Models.Wydobycie.wydobycie_brutto import Wydobycie_Brutto
from Models.Wydobycie.raport_topiarza import Tabelka_z_Wydobyciem_po_baniakach



def main():    

    # bl = BusinessLogic()
    # bl.PoliczWydobycieNaDzien()

    

    # Drukuj_Raport_Do_Excella("2021.12.1", "2021.12.17").Drukuj_Sformatowny_Raport_Wytopu("Wytop grudzień 2021")
    # print(Dane_Do_wytopu("2021.12.1", "2021.12.17")[["Data", "Wydobycie_WG", "WE_1", "WE_2", "WE_3", "Wydobycie_WE", "Wydobycie_Calkowite", "Wydobycie_Brutto_Calkowite"]])
    # print(Tabelka_z_Wydobyciem_po_baniakach("2021.11.15", "2021.11.23"))
    print(Wydobycie_Brutto("2021.12.16", "2021.12.19").Wydobycie_Brutto_Podsumowanie)
    # rwz = Raport_Wydobycia_Zmianowego()
    # print(rwz.rap_2017.info())
    # print(rwz.rap_2018_2021.info())
    # print(Wylewanie("2021.11.1", "2021.11.14").to_string(index=False))


if __name__ == "__main__":
    main()

