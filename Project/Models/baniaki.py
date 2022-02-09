from .Receptura.receptura import Zestaw
from datetime import datetime, time, timedelta
from numpy import float32, zeros, full, array, ndarray


class Baniak:
    
    def __init__(self, nastawa, stluczka=0, numer=None, data_przygotowania=None ):
        
        self.Numer_baniaka = numer if numer != None else "XX"
        self.Data_przygotowania = data_przygotowania if data_przygotowania != None else "XXXX"

        if type(stluczka) == int or type(stluczka) == float:
            self.Dodatek_stluczki = stluczka
        elif type(stluczka) == dict:
            self.Dodatek_stluczki = array(list(stluczka.values()),float32).sum()

        if type(nastawa) == Zestaw: 
            self.Ilosc_szkla_z_baniaka = nastawa.Ilosc_szkla_z_jednego_zestawu + self.Dodatek_stluczki
        else:
            self.Ilosc_szkla_z_baniaka = array(list(nastawa.values()), float32).sum() + self.Dodatek_stluczki

    def __str__(self):
        return f"numer: {self.Numer_baniaka}, data przygotowania: {self.Data_przygotowania}, ilosc szkła: {self.Ilosc_szkla_z_baniaka:.2f} kg"


class Wydobycie_z_baniaka:
    
    PIERWSZA_ZMIANA = [6, 13]
    DRUGA_ZMIANA = [14, 21]
    TRZECIA_ZMIANA = [22, 6]       
    
    def __init__(self, dataZmiany=None, czasPostawienia=None, czasZdjecia=None, iloscSzklaZBaniaka=None, **kwargs):
        """
        dataZmiany: str lub datetime
        czasPostawienia, czasZdjecia: str lub datetime 
        iloscSzklaZBaniaka: int, float, Baniak
        """
        if dataZmiany != None and czasPostawienia != None and czasZdjecia != None and iloscSzklaZBaniaka != None:
            
            self.DataZmiany = datetime.strptime(dataZmiany, "%Y.%m.%d") if type(dataZmiany) == str else dataZmiany
            self.CzasPostawienia = datetime.strptime(czasPostawienia, "%Y.%m.%d %H:%M") if type(czasPostawienia) == str else czasPostawienia
            self.CzasZdjecia = datetime.strptime(czasZdjecia, "%Y.%m.%d %H:%M") if type(czasZdjecia) == str else czasZdjecia

            czasZasypuZestawu = self.CzasZdjecia - self.CzasPostawienia        
            self.CzasZasypuZestawu = float32(czasZasypuZestawu.seconds/3600)
            if type(iloscSzklaZBaniaka) == int or type(iloscSzklaZBaniaka) == float:
                stalaDoObliczeniaIlosciSzkla = iloscSzklaZBaniaka / (self.CzasZasypuZestawu)
            elif type(iloscSzklaZBaniaka) == Baniak:
                stalaDoObliczeniaIlosciSzkla = iloscSzklaZBaniaka.Ilosc_szkla_z_baniaka / (self.CzasZasypuZestawu)



        self.czasZasypuNaZmianie = zeros(3, float32)   

        poczatekPierwszejZmiany = datetime.combine(self.DataZmiany, time(self.PIERWSZA_ZMIANA[0],0,0))
        koniecPierwszejZmiany = datetime.combine(self.DataZmiany, time(self.PIERWSZA_ZMIANA[1],0,0))
        poczatekDrugiejZmiany = datetime.combine(self.DataZmiany, time(self.DRUGA_ZMIANA[0],0,0))
        koniecDrugiejZmiany = datetime.combine(self.DataZmiany, time(self.DRUGA_ZMIANA[1],0,0))
        poczatekTrzeciejZmiany = datetime.combine(self.DataZmiany, time(self.TRZECIA_ZMIANA[0],0,0))
        koniecTrzeciejZmiany = datetime.combine(self.DataZmiany + timedelta(days=1), time(self.TRZECIA_ZMIANA[1],0,0))
        
        
        self.WydobycieNaZmiane = full(3, stalaDoObliczeniaIlosciSzkla)

        for m in range(int(czasZasypuZestawu.seconds/60)):
            #Baniak Początkowy
            # if (self.CzasPostawienia+timedelta(minutes=m)) <= poczatekPierwszejZmiany and (self.CzasPostawienia+timedelta(minutes=m)) <= koniecPierwszejZmiany:
            #     pass
            if (self.CzasPostawienia+timedelta(minutes=m)) >= poczatekPierwszejZmiany and (self.CzasPostawienia+timedelta(minutes=m)) < poczatekDrugiejZmiany:
                self.czasZasypuNaZmianie[0] += 1
            elif (self.CzasPostawienia+timedelta(minutes=m)) >= poczatekDrugiejZmiany and (self.CzasPostawienia+timedelta(minutes=m)) < poczatekTrzeciejZmiany:
                self.czasZasypuNaZmianie[1] += 1
            elif (self.CzasPostawienia+timedelta(minutes=m)) >= poczatekTrzeciejZmiany and (self.CzasPostawienia+timedelta(minutes=m)) < koniecTrzeciejZmiany:
                self.czasZasypuNaZmianie[2] += 1


        self.WydobycieNaZmiane *= (self.czasZasypuNaZmianie/60)

        self.CzasZasypuNaZmianie = [self.CzasZasypuZestawu, self.czasZasypuNaZmianie[0]/60,self.czasZasypuNaZmianie[1]/60,self.czasZasypuNaZmianie[2]/60]

    def __str__(self):
        return f"Czas postawienie: {self.CzasPostawienia}, Czas zasypu: {self.CzasZasypuZestawu:.2f}, Wydobycie na zmianach: {self.WydobycieNaZmiane}"


                         


