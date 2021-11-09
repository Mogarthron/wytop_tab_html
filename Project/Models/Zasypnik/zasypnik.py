from numpy import float32

class PracaZasypnika:
    def __init__(self, czas, czas_pracy, tryb=1):

        if tryb == 1:
            self.Cykl = float32(czas + czas_pracy)
            self.Czas_Przerwy = float32(czas)
            self.Czas_Pracy = float32(czas_pracy)
        elif tryb == 2:
            self.Cykl = float32(czas)
            self.Czas_Przerwy = float32(czas - czas_pracy)
            self.Czas_Pracy = float32(czas_pracy)

        self.Czas_sypania_w_ciagu_godziny = float32(3600/self.Cykl*self.Czas_Pracy)