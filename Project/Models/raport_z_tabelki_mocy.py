from os import path, listdir
from pandas import DataFrame
import numpy as np
import datetime
from datetime import datetime, date, timedelta


def OpenTxt(FilePath):
        rows = list()

        columns = ['T1A', 'T1V', 'T1kW', 'T2A', 'T2V', 'T2kW', 'T3A', 'T3V', 'T3kW',
                   'T4A', 'T4V', 'T4kW', 'Tem Top', 'T5A', 'T5V', 'T5kW', 'Tem mas', 'Tem gas']

        file = open(FilePath, 'r')

        fileName = file.name.replace('.txt', '')
        # fileName = fileName[10:]

        for r in file:

            newRow = r.replace('\x05', '')
            newRow = newRow.split(' ')
            rows.append(newRow)

        file.close()

        for r in rows:

            for i in r:

                if (i == ''):
                    r.remove('')

        dates = list()

        Table = DataFrame(np.zeros((24, 18), float))

      

        start_date = datetime(int(fileName[0:2])+2000, int(fileName[2:4]), int(fileName[4:]), 6)
        for h in range(24):
            dates.append(start_date + timedelta(hours=h))

        i = 0
        for r in rows:         

            for j in range(18):

                Table[j][i] = r[j+1]

            i = i + 1

        Table.columns = columns

        Table['DataGodzina'] = dates
        Table['MocCalkowita'] = Table['T1kW'] + Table['T2kW'] + \
            Table['T3kW'] + Table['T4kW'] + Table['T5kW']

        return Table


tabelka_1_2 = OpenTxt("210917.txt")[['DataGodzina', 'T1A', 'T1V','T2A', 'T2V', 'Tem Top']]
tabelka_1_2 = tabelka_1_2.append([{'DataGodzina':None, 'T1A':None, 'T1V':None,'T2A':None, 'T2V':None, 'Tem Top':None}], ignore_index=True)



