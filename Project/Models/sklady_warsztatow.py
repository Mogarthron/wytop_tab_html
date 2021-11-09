from pandas import DataFrame, read_sql, merge
from numpy import float64, pi
import math
import fdb
from datetime import datetime


path = "ConnectionFDB.txt"
with open(path, "r") as c:
    con = c.read()

con = con.split(",")


_sklady_warsztatow = """
SELECT r."Nr karty formowania", r."Nazwisko", r."Imie",
    r."Stempel czasu", r."Dzm", r."Zmiana", r."Dzial", r."Akord", r."Stanowisko",
    r."Przestoj", r."Czas pracy"
FROM "Pracownicy" r
where "Dzial" = 'Formowanie' and "Stempel czasu" > '1.10.2021' and "Nr karty formowania" is not null
"""


df = read_sql(_sklady_warsztatow, fdb.connect(
                                    dsn=con[0], user=con[1], password=con[2]))


print(df)