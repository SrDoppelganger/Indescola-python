import numpy as np
import pandas as pd
from girth import twopl_mml, ability_eap

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

#Substituir por np.loc()?
#Deixar mais genérico?
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

    df['recode_patio'] = np.where(
        (df['IN_PATIO_COBERTO'] == 1) | (df['IN_PATIO_DESCOBERTO'] == 1)
        ,1,0
    )
    

    df['recode_internet'] = np.where(
        (df['IN_INTERNET'] == 1) | (df['IN_INTERNET_ALUNOS'] == 1) | (df['IN_INTERNET_ADMINISTRATIVO'] == 1) | (df['IN_INTERNET_APRENDIZAGEM'] == 1) | (df['IN_INTERNET_COMUNIDADE'] == 1)
        ,1,0)

    remover_colunas(df)
    
#Talvez seja preferível MANTER as colunas, apenas ocultá-las
def remover_colunas(df: pd.DataFrame):
    #separa dados de contextualização com os dados binário para calcular
    df_contexto = df.loc[:,['NU_ANO_CENSO','TP_SITUACAO_FUNCIONAMENTO']]
    df_calc = df.loc[:,'IN_AGUA_POTAVEL':]


    df_calc = df_calc.drop(columns=['IN_AGUA_REDE_PUBLICA','IN_AGUA_POCO_ARTESIANO','IN_AGUA_CACIMBA','IN_AGUA_FONTE_RIO','IN_AGUA_CARRO_PIPA','IN_AGUA_INEXISTENTE',
                          'IN_ENERGIA_GERADOR_FOSSIL','IN_ENERGIA_RENOVAVEL','IN_ENERGIA_REDE_PUBLICA','IN_ENERGIA_INEXISTENTE','IN_ESGOTO_REDE_PUBLICA',
                          'IN_ESGOTO_FOSSA_SEPTICA','IN_ESGOTO_FOSSA_COMUM','IN_ESGOTO_FOSSA','IN_ESGOTO_INEXISTENTE','IN_TRATAMENTO_LIXO_SEPARACAO','IN_TRATAMENTO_LIXO_REUTILIZA',
                          'IN_TRATAMENTO_LIXO_RECICLAGEM','IN_TRATAMENTO_LIXO_INEXISTENTE','IN_INTERNET','IN_INTERNET_ALUNOS','IN_INTERNET_ADMINISTRATIVO','IN_INTERNET_APRENDIZAGEM',
                          'IN_INTERNET_COMUNIDADE','IN_PATIO_COBERTO','IN_PATIO_DESCOBERTO'])

    df_calc = df_calc.fillna(0).astype(int)
    calcular_parametros(df_calc)


def calcular_parametros(df:pd.DataFrame):
    #calcula os parametros de Dificuldade e Discriminação para cada questão
    print("Calculando parâmetros...")

    #verifica e remove colunas sem variancia nenhuma (quebra a lib)
    variancia = df.std(axis=0)
    validas = variancia[variancia > 0].index
    df = df[validas]

    respostas = df.values.T

    #Amostragem pra esse krl n crashar
    total_escolas = respostas.shape[1]
    tam_amostra = min(5000, total_escolas)
    

    np.random.seed(42)
    amostragem = np.random.choice(total_escolas, size=tam_amostra, replace=False)
    resp_amostra = respostas[:,amostragem]

    #PLACEHOLDER
    estimativas = twopl_mml(resp_amostra)

    disc = estimativas['Discrimination']
    dif = estimativas['Difficulty']

    df_params = pd.DataFrame({
        'Questao': validas,
        'Discriminação': disc,
        'Dificuldade': dif
    })

    print("Exportando parâmetros A e B por questão...")
    df_params.to_csv(f'{output_path}/parametros.csv',index=False)

    calcular_estimativas(df)

#Fica quabrando virando array 1D T .T
def calcular_estimativas(df:pd.DataFrame):
    print("Calculando estimativas para cada questão...")
     

    exportar_csv(df)

def exportar_csv(df:pd.DataFrame):
    print("Exportando...")
    df.to_csv(f'{output_path}/filtrado.csv',index=False)

selecionar_variaveis()
