#Pipeline de processamento backends
def processar(censo_path: str, var_path: str):
    selecionar_variaveis(censo_path, var_path)
    #implementar funções de calcular.py aq

import numpy as np
import pandas as pd 
from girth import twopl_mml, ability_eap


def selecionar_variaveis(censo_path:str, var_path: str):
    print("Selecionando variáveis...")
    with open(var_path, 'r') as file:
        var_list = [line.strip() for line in file]

    df = pd.read_csv(censo_path, sep=';',encoding="latin1", usecols=var_list)
    filtrar_escolas(df)


def filtrar_escolas(df:pd.DataFrame):
    print("Filtrando Escolas em atividade...")
    #remove escolas privadas
    df = df[df['TP_DEPENDENCIA'] != 4].copy() #tira o SettingWithCopy Warning ;3
    #mantém SOMENTE escolas em atividade
    df = df[df['TP_SITUACAO_FUNCIONAMENTO'] == 1].copy()

    agregar_variaveis(df)

#Substituir por np.loc()?
#Deixar mais genérico?
def agregar_variaveis(df:pd.DataFrame):
    print("Agregando Variáveis...")

    df = df.copy()

    df['recode_abastecimento_agua'] = np.where(
            ((df['IN_AGUA_REDE_PUBLICA'] == 1) | (df['IN_AGUA_POCO_ARTESIANO'] == 1) | (df['IN_AGUA_CACIMBA'] == 1) | (df['IN_AGUA_FONTE_RIO'] == 1) | (df['IN_AGUA_CARRO_PIPA'] == 1)) & (df['IN_AGUA_INEXISTENTE'] == 0)
            ,1,0)


    df['recode_energia'] = np.where(
        ((df['IN_ENERGIA_GERADOR_FOSSIL'] == 1) | (df['IN_ENERGIA_RENOVAVEL'] == 1) | (df['IN_ENERGIA_REDE_PUBLICA'] == 1)) & (df['IN_ENERGIA_INEXISTENTE'] == 0)
        ,1,0)

    df['recode_esgoto'] = np.where(
        ((df['IN_ESGOTO_REDE_PUBLICA'] == 1) | (df['IN_ESGOTO_FOSSA_SEPTICA'] == 1) | (df['IN_ESGOTO_FOSSA_COMUM'] == 1) | (df['IN_ESGOTO_FOSSA'] == 1)) & (df['IN_ESGOTO_INEXISTENTE'] == 0)
        ,1,0
    )

    df['recode_destinacao_lixo'] = np.where(
        (df['IN_LIXO_SERVICO_COLETA'] == 1) | (df['IN_LIXO_QUEIMA'] == 1) | (df['IN_LIXO_ENTERRA'] == 1) | (df['IN_LIXO_DESTINO_FINAL_PUBLICO'] == 1)
        ,1,0
    )
    
    df['recode_tratamento_lixo'] = np.where(
            ((df['IN_TRATAMENTO_LIXO_SEPARACAO'] == 1) | (df['IN_TRATAMENTO_LIXO_REUTILIZA'] == 1) | (df['IN_TRATAMENTO_LIXO_RECICLAGEM'] == 1)) & (df['IN_TRATAMENTO_LIXO_INEXISTENTE']==0)
            ,1,0
        )

    df['recode_patio'] = np.where(
        (df['IN_PATIO_COBERTO'] == 1) | (df['IN_PATIO_DESCOBERTO'] == 1)
        ,1,0
    )
    
    df['recode_internet'] = np.where(
        (df['IN_INTERNET'] == 1) | (df['IN_INTERNET_ALUNOS'] == 1) | (df['IN_INTERNET_ADMINISTRATIVO'] == 1) | (df['IN_INTERNET_APRENDIZAGEM'] == 1) | (df['IN_INTERNET_COMUNIDADE'] == 1)
        ,1,0)

    drop_cols = ['IN_AGUA_REDE_PUBLICA','IN_AGUA_POCO_ARTESIANO','IN_AGUA_CACIMBA','IN_AGUA_FONTE_RIO','IN_AGUA_CARRO_PIPA','IN_AGUA_INEXISTENTE',
                'IN_ENERGIA_GERADOR_FOSSIL','IN_ENERGIA_RENOVAVEL','IN_ENERGIA_REDE_PUBLICA','IN_ENERGIA_INEXISTENTE','IN_ESGOTO_REDE_PUBLICA',
                'IN_ESGOTO_FOSSA_SEPTICA','IN_ESGOTO_FOSSA_COMUM','IN_ESGOTO_FOSSA','IN_ESGOTO_INEXISTENTE','IN_TRATAMENTO_LIXO_SEPARACAO','IN_TRATAMENTO_LIXO_REUTILIZA',
                'IN_TRATAMENTO_LIXO_RECICLAGEM','IN_TRATAMENTO_LIXO_INEXISTENTE','IN_INTERNET','IN_INTERNET_ALUNOS','IN_INTERNET_ADMINISTRATIVO','IN_INTERNET_APRENDIZAGEM',
                'IN_INTERNET_COMUNIDADE','IN_PATIO_COBERTO','IN_PATIO_DESCOBERTO']

    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    calcular_parametros(df)
    

def calcular_parametros(df:pd.DataFrame):
    #garante que vai pegar somente as colunas dicotomizadas
    cols_itens = [c for c in df.columns if c.startswith('IN_') or c.startswith('recode_')]
    df_calc = df[cols_itens].fillna(0).astype(int)

    #TODO adicionar moto calculo

    calcular_estimativas(df)

#Fica quabrando virando array 1D T .T
def calcular_estimativas(df:pd.DataFrame):
    print("Calculando estimativas para cada questão...")
     

    exportar_csv(df)

def exportar_csv(df:pd.DataFrame):
    print("Exportando...")
    df.to_csv(f'resultados/filtrado.csv',index=False)


