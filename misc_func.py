import pandas as pd
import bisect
from datetime import date

def localiza_data_proxima(df:pd.DataFrame, data:date):
    lista_datas:list[date] = df.index.to_list()
    lista_datas = sorted(lista_datas)
    i = bisect.bisect_left(lista_datas,data)#identifica o indice do valor mais próximo
    return(lista_datas[i - 1])