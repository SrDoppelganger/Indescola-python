import numpy as np
import pandas as pd
from girth import threepl_mml, ability_eap

censo_path = 'bases/censo.csv'
var_path = 'bases/variaveis_censo.txt'
mat_path = 'bases/matriculas_censo.csv'
output_path = 'resultados/'

def selecionar_variaveis():
    with open(var_path, 'r') as file:
        var_list = [line.strip() for line in file]

    df = pd.read_csv(censo_path, sep=';',encoding="latin1", usecols=var_list)
    filtrar_escolas(df)


def filtrar_escolas(df:pd.DataFrame):
    #remove escolas privadas
    df.drop(df[df['TP_DEPENDENCIA'] == 4].index, inplace=True)
    #mantém SOMENTE escolas em atividade
    df = df[df['TP_SITUACAO_FUNCIONAMENTO'] == 1]

    df.to_csv(f'{output_path}/filtrado.csv',index=False)
    agregar_variaveis(df)

def agregar_variaveis(df:pd.DataFrame):
    print(df)

selecionar_variaveis()
