from businnes_logic import *
from Models.Wydobycie.wydobycie_zmianowe import Dane_Do_wytopu, Wylewanie, Wydobycie_Zmianiowe
from Models.Wydobycie.wydobycie_brutto import Wydobycie_Brutto
from Models.Wydobycie.raport_topiarza import Tabelka_z_Wydobyciem_po_baniakach


def main():    

    # bl = BusinessLogic()
    # bl.PoliczWydobycieNaDzien()


    # Wydobycie_Zmianiowe()
    print(Dane_Do_wytopu("2021.11.1", "2021.11.13").to_string(index=False))
    # print(Wylewanie("2021.11.1", "2021.11.14").to_string(index=False))
    # print(Wydobycie_Brutto("2021.11.9", "2021.11.10").Wydobycie_Brutto.to_string(index=False))
    # print(Tabelka_z_Wydobyciem_po_baniakach("2021.11.9", "2021.11.9"))
  


    



if __name__ == "__main__":
    main()

