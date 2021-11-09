from pandas import DataFrame, Series, read_sql, merge
from numpy import float64
import numpy as np
import fdb
from datetime import datetime

from pandas.core.tools.datetimes import to_datetime


path = "E:\Biaglass\Wytop\Wydobycie zmianowe\wytop_tab_html\Project\Data\ConnectionFDB.txt"
with open(path, "r") as c:
    con = c.read()

con = con.split(",")



dolki = """
SELECT 
    --r.ID, 
    r.FORMA, r.HUTNIK, r.DOLEK_BRYGADZISTY, r.DOLEK_OPALOWEGO,
    r.PISZCZEL, r.STEMPEL
FROM DOLKI r
"""


# DOLKI = read_sql(dolki, fdb.connect(
#         dsn=con[0], user=con[1], password=con[2]), params=[])

# DOLKI["HUTNIK"] = DOLKI["HUTNIK"].apply(Napraw_Hutnika)
# DOLKI["DOLEK_BRYGADZISTY"] = DOLKI["DOLEK_BRYGADZISTY"].apply(Popraw_Wartosci_Dolkow)
# DOLKI["DOLEK_OPALOWEGO"] = DOLKI["DOLEK_OPALOWEGO"].apply(Popraw_Wartosci_Dolkow)



def Kategoria(n):
    if "0" in n:
        return "Bezbarwne"
    else:
        return "Opalowe"

def Zmiana(n):

    h = n.hour

    if h >= 6 and h < 14:
        return "R"
    elif h >= 14 and h < 22:
        return "P"
    else: return "N"

def Napraw_Hutnika(hutnik:str):

    p_hutnik = hutnik.replace(hutnik[0:], hutnik[0:].lower())
    p_hutnik = p_hutnik.replace(p_hutnik[0], p_hutnik[0].upper())

    return p_hutnik

def Popraw_Wartosci_Dolkow(wartosc_dolka:str):
    try:
        n = wartosc_dolka.replace(",", ".")
        return float64(n)
    except:
        return 0


class Wydobycie_Brutto:
    query = """
        select 	
            a."Dzm", 
            --a."Zmiana" as "Brygada",	
            a."Warsztat", 
            c."Mistrz. zesp. form",	
            c."K", 	
            c."Forma",
            --b."Netto",
            b."Brutto",
            c."WAGA_BRUTTO", 
            a."Stempel czasu"            
            
        from "Formowanie" a	
        inner join "Sortownia" b on a."Nr karty formowania" = b."Nr karty formowania"	
        inner join "Stany" c on a."Nr karty formowania" = c."Nr karty formowania"	
        where a."Dzm" between ? and ? and b."Braki masy ml" is not null	
        order by a."Dzm", a."Zmiana", a."Warsztat"	
        """
    
    def __init__(self, od, do):
        """
        od, do: datetime lub str
        """

        od = od if (type(od) == datetime) else datetime.strptime(od, "%Y.%m.%d")
        do = do if (type(do) == datetime) else datetime.strptime(do, "%Y.%m.%d")
        
        WYDOBYCIE_BRUTTO = read_sql(self.query, fdb.connect(
                                    dsn=con[0], user=con[1], password=con[2]), params=[od, do])
        WYDOBYCIE_BRUTTO["Dzm"] = to_datetime(WYDOBYCIE_BRUTTO["Dzm"])
        WYDOBYCIE_BRUTTO["Kategoria"] = WYDOBYCIE_BRUTTO["K"].apply(Kategoria)
        WYDOBYCIE_BRUTTO["Zmiana"] = WYDOBYCIE_BRUTTO["Stempel czasu"].apply(Zmiana)
        WYDOBYCIE_BRUTTO["Wydobycie Brutto"] = WYDOBYCIE_BRUTTO["Brutto"] * WYDOBYCIE_BRUTTO["WAGA_BRUTTO"] / 1000

        warunek_Opal = (WYDOBYCIE_BRUTTO["Kategoria"] == "Opalowe")

        WYDOBYCIE_BRUTTO["Szklo WG"] = (WYDOBYCIE_BRUTTO["Wydobycie Brutto"]*0.75).where(warunek_Opal, WYDOBYCIE_BRUTTO["Wydobycie Brutto"])
        WYDOBYCIE_BRUTTO["Szklo WE"] = (WYDOBYCIE_BRUTTO["Wydobycie Brutto"]*0.25).where(warunek_Opal, 0)

        self.Wydobycie_Brutto = WYDOBYCIE_BRUTTO

        podsumowanie = self.Wydobycie_Brutto.pivot_table(
                            index=["Dzm"], columns=["Zmiana"], values=["Wydobycie Brutto"], aggfunc=np.sum, fill_value=0)
    
        nowe_kolumny = {x[1]: Series(data=podsumowanie[x], index=podsumowanie.index) for x in podsumowanie.columns}
    
        self.Wydobycie_Brutto_Podsumowanie = DataFrame(nowe_kolumny)    

        self.Wydobycie_Brutto_Podsumowanie.reset_index(inplace=True)

        self.Szklo_bezbarwne_do_wytopu = self.Wydobycie_Brutto.loc[self.Wydobycie_Brutto["Kategoria"] == "Bezbarwne"][["Dzm", "Zmiana", "Szklo WG"]]



   

# if __name__ == "__main__":
#     not_main()