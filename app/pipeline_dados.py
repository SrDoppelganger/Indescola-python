import numpy as np
import pandas as pd 
from girth import twopl_mml, ability_eap
import logging

#configuração de logs
logging.basicConfig(filename="logs/SysLog.log",filemode="w",format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)

logger = logging.getLogger(__name__)
FileOutputHandler = logging.FileHandler('logs.log')

logger.addHandler(FileOutputHandler)

#TEMPORÁRIO, IMPLEMENTAR JEITO MAIS SOFISTICADO DPS
#Listas de variáveis específicas

#Talvez seja mais fácil só remover as específicas e deixar o resto das variáveis como gerais
#base_geral = ['recode_abastecimento_agua','recode_energia','recode_esgoto','recode_destinacao_lixo','recode_tratamento_lixo','recode_patio']

base_tech = ['recode_internet','IN_COMPUTADOR','IN_EQUIP_COPIADORA','IN_EQUIP_IMPRESSORA','IN_EQUIP_IMPRESSORA_MULT',
             'IN_EQUIP_SCANNER','IN_EQUIP_NENHUM','IN_EQUIP_DVD','IN_DESKTOP_ALUNO','IN_COMP_PORTATIL_ALUNO',
             'IN_TABLET_ALUNO','IN_ACESSO_INTERNET_COMPUTADOR','IN_ACES_INTERNET_DISP_PESSOAIS','TP_REDE_LOCAL','IN_BANDA_LARGA']

base_infantil = ['IN_BANHEIRO_EI','IN_PARQUE_INFANTIL']

#Pipeline de processamento backend
def processar(censo_path: str, var_path: str, mat_path: str, output_path: str):
        
    df_esc, df_mat = selecionar_variaveis(censo_path, var_path, mat_path)
    df_esc = filtrar_escolas(df_esc)
    df_esc = agregar_variaveis(df_esc)
    df_mat = separar_etapas(df_mat)
    df_calc, df_score, df_params = calcular_parametros(df_esc)
    df_resultado = associar_matriculas(df_score,df_mat)
    exportar_csv(df_calc,df_resultado,df_params,output_path)



def selecionar_variaveis(censo_path:str, var_path: str, mat_path):
    print("Selecionando variáveis...")
    

    #TEMP -> colocar como input do usuário dps
    mat_cols = ['CO_ENTIDADE','QT_MAT_INF_CRE','QT_MAT_INF_PRE','QT_MAT_FUND_AI','QT_MAT_FUND_AF','QT_MAT_MED']

    
    with open(var_path, 'r', encoding="utf-8-sig") as file:
        var_list = [line.strip() for line in file]

    df = pd.read_csv(censo_path, sep=';',encoding="latin1", usecols=var_list)
    df_mat = pd.read_csv(mat_path, sep=';', encoding="latin1", usecols=mat_cols)

    logging.info("Variáveis selecionadas com sucesso")
    return df, df_mat


def filtrar_escolas(df:pd.DataFrame):
    print("Filtrando Escolas em atividade...")
    #remove escolas privadas
    df = df[df['TP_DEPENDENCIA'] != 4].copy() #tira o SettingWithCopy Warning ;3
    #mantém SOMENTE escolas em atividade
    df = df[df['TP_SITUACAO_FUNCIONAMENTO'] == 1].copy()

    logging.info("Escolas válidas filtradas com sucesso")
    return df

#Substituir por np.loc()?
#Deixar mais genérico? sim.
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


    #TODO implementar separação por etapa de ensino
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    logging.info("Escolas válidas filtradas com sucesso")
    return df

def separar_etapas(df_mat: pd.DataFrame):
    flag_col = [] #<- adicionar como coluna em df_mat
    #row_flags = ['creche','infantil - pré-escola','fundamental - anos iniciais','fundamental - anos finais','ensino medio']
    #mats = ['QT_MAT_INF_CRE','QT_MAT_INF_PRE','QT_MAT_FUND_AI','QT_MAT_FUND_AF','QT_MAT_MED']

    #for index,value in enumerate(mats):

    for index, row in df_mat.iterrows():
        row_flags = []
        sep = ";"
        if row['QT_MAT_INF_CRE'] > 0:
            row_flags.append("creche")
        if row['QT_MAT_INF_PRE'] > 0:
            row_flags.append("infantil - pré-escola")
        if row['QT_MAT_FUND_AI'] > 0:
            row_flags.append("fundamental - anos inicias")
        if row['QT_MAT_FUND_AF'] > 0:
            row_flags.append("fundamental - anos finais")
        if row['QT_MAT_MED'] > 0:
            row_flags.append("ensino médio")


        flag_col.append(sep.join(row_flags))

    df_mat['temp_etapas'] = flag_col  
    
    return df_mat

def calcular_parametros(df:pd.DataFrame):
    print("calculando parametros...")
    #garante que vai pegar somente as colunas dicotomizadas
    cols_itens = [c for c in df.columns if c.startswith('IN_') or c.startswith('recode_')]
    df_calc = df[cols_itens].fillna(0).astype(int)

    #Pega uma amostra generosa ao inves de processar todas as escolas de uma vez
    escolas_total = len(df_calc)
    tam_amostra = min(5000, escolas_total)
    np.random.seed(42)
    amostragem_idx = np.random.choice(escolas_total, size=tam_amostra, replace=False)

    df_amostra = df_calc.iloc[amostragem_idx]

    #remove colunas sem variância
    var_amostra = df_amostra.std(axis=0)
    itens_validos = var_amostra[(var_amostra >= 0.01) & (var_amostra <= 0.99)].index.tolist()

    df_amostra = df_amostra[itens_validos]
    df_calc = df_calc[itens_validos]


    #transposição da matriz para ficar no formato da biblioteca (resp x item)
    respostas = df_amostra.values.T

    estimativas = twopl_mml(respostas)
    disc = estimativas['Discrimination'].ravel()
    diff = estimativas['Difficulty'].ravel()

    df_params = pd.DataFrame({
        'Questao': itens_validos,
        'Discriminação': disc,
        'Dificuldade': diff
    })

    respostas_total = df_calc.values.T
    
    theta = ability_eap(respostas_total, diff, disc).ravel()
    

    #TODO ponderar por matrícula
    escore_infra = (theta * 10) + 50

    #escore_ponderado = escore_etapa * mat_etapa /soma_das_matriculas

    if 'CO_ENTIDADE' in df.columns:
        co_entidade = df['CO_ENTIDADE'].values.ravel()
    else:
        co_entidade = np.arange(escolas_total)


    df_resultado = pd.DataFrame({
        'CO_ENTIDADE':co_entidade,
        'NO_ENTIDADE':df['NO_ENTIDADE'].values.ravel(),
        'NO_MUNICIPIO':df['NO_MUNICIPIO'].values.ravel(),
        'SG_UF':df['SG_UF'].values.ravel(),
        'theta_bruto':theta,
        'indice_infraestrutura':escore_infra
    })


    logging.info("Calculo TRI realizado com sucesso")
    return df_calc,df_resultado,df_params

def associar_matriculas(df_escolas: pd.DataFrame, df_matriculas: pd.DataFrame):
    print("Associando Matriculas...")

    df = pd.merge(df_escolas, df_matriculas, on='CO_ENTIDADE', how='inner')
    df['Total Matrículas'] = df['QT_MAT_INF_CRE'] + df['QT_MAT_INF_PRE'] + df['QT_MAT_FUND_AI'] + df['QT_MAT_FUND_AF'] + df['QT_MAT_MED']

    logging.info("Matriculas associadas foram associadas as escolas com sucesso")
    return df

def exportar_csv(df_calc:pd.DataFrame, df_resultado:pd.DataFrame, df_parametros:pd.DataFrame, output: str):
    print("Exportando...")
    df_calc.to_csv(f'{output}/respostas.csv',index=False)
    df_resultado.to_csv(f'{output}/resultado.csv',index=False)
    df_parametros.to_csv(f'{output}/parametros.csv',index=False)
    logging.info("Processamento completo concluido com sucesso")





