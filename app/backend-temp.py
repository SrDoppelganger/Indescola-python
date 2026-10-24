#script para testar feature de agregação de variáveis

import pandas as pd
import numpy as np
import logging

var_path = 'app/dados_teste.csv'
bd_path = 'app/resposta_exemplo.csv'

#config de logs
logging.basicConfig(filename="logs/backendTestLog.log",filemode="w",format="%(asctime)s - %(levelname)s - %(message)s")

df_var = pd.read_csv(var_path, sep=";", encoding="utf-8-sig")
df = pd.read_csv(bd_path, sep=";", encoding="utf-8-sig")

var_agg: dict = {}

logging.warning("Testando Log = w=")
#percorre df_var
for index,row in df_var.iterrows():
    #checa se n tá vazio e se n tiver...
    if type(row.iloc[1]) == str:
        #cria array a partir da coluna 2 e associa valor da coluna 1
        if not row.iloc[1] in var_agg:
            var_agg[row.iloc[1]] = []
            var_agg[row.iloc[1]].append(row.iloc[0])
        #se o array já existir, só add o valor da coluna 1
        if row.iloc[1] in var_agg:
            var_agg[row.iloc[1]].append(row.iloc[0])


#checa se tem alguma variavel agregada no dicionário
if bool(var_agg):
    bd = df.copy()
    cols = list(var_agg.values())

    for key, value in var_agg.items():
        recode_values = []
        cols = bd[value]

        for index, row in cols.iterrows():
            print(row)
            #checar se linha tem o valor 1 em alguma coluna...se tiver append 1 para recode_values[]
        
        print(cols)
        bd[f"recode_{key}"] = [0,0,0,0] # <- colocar ngc np.where aq dps de processar tudo
        

    #greg = bd[cols[0]]
    #print(bd)

logger = logging.getLogger(__name__)
FileOutputHandler = logging.FileHandler('logs.log')

logger.addHandler(FileOutputHandler)
