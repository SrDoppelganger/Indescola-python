import numpy as np
import pandas as pd
from girth import threepl_mml, ability_eap

censo_path = 'bases/censo.csv'
var_path = 'bases/variaveis_censo.txt'
mat_path = 'bases/matriculas_censo.csv'
output_path = 'resultados/'

def selecionar_variaveis():
    print("Selecionando variáveis...")
    with open(var_path, 'r') as file:
        var_list = [line.strip() for line in file]

    df = pd.read_csv(censo_path, sep=';',encoding="latin1", usecols=var_list)
    filtrar_escolas(df)


def filtrar_escolas(df:pd.DataFrame):
    print("Filtrando Escolas em atividade...")
    #remove escolas privadas
    df.drop(df[df['TP_DEPENDENCIA'] == 4].index, inplace=True)
    #mantém SOMENTE escolas em atividade
    df = df[df['TP_SITUACAO_FUNCIONAMENTO'] == 1]

    agregar_variaveis(df)

def agregar_variaveis(df:pd.DataFrame):
    print("Agregando Variáveis...")
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

    df['recode_internet'] = np.where(
        (df['IN_INTERNET'] == 1) | (df['IN_INTERNET_ALUNOS'] == 1) | (df['IN_INTERNET_ADMINISTRATIVO'] == 1) | (df['IN_INTERNET_APRENDIZAGEM'] == 1) | (df['IN_INTERNET_COMUNIDADE'] == 1)
        ,1,0)
    calcular_parametros(df)
    

def calcular_parametros(df: pd.DataFrame):
    print("Parametros :3 ")

    exportar_csv(df)

def exportar_csv(df:pd.DataFrame):
    print("Exportando...")
    df.to_csv(f'{output_path}/filtrado.csv',index=False)

selecionar_variaveis()
