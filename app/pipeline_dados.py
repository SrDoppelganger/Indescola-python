import numpy as np
import pandas as pd 
from girth import twopl_mml, ability_eap
import logging

#configuração de logs
logging.basicConfig(filename="logs/SysLog.log",filemode="w",format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)

logger = logging.getLogger(__name__)
FileOutputHandler = logging.FileHandler('logs.log')

logger.addHandler(FileOutputHandler)

#Pipeline de processamento backend
def processar(censo_path: str, var_path: str, mat_path: str, output_path: str):
        
    df_esc, df_mat = selecionar_variaveis(censo_path, var_path, mat_path)
    df_esc = filtrar_escolas(df_esc)
    df_esc = agregar_variaveis(df_esc)
    df_mat = separar_etapas(df_mat)
    df_calc, df_score, df_params = calcular_parametros(df_esc, df_mat)
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

    for index, row in df_mat.iterrows():
        row_flags = []
        sep = ";"
    
        if row['QT_MAT_INF_CRE'] > 0:
            row_flags.append("Creche")
        if row['QT_MAT_INF_PRE'] > 0:
            row_flags.append("Infantil - Pré-escola")
        if row['QT_MAT_FUND_AI'] > 0:
            row_flags.append("Fundamental - Anos Inicias")
        if row['QT_MAT_FUND_AF'] > 0:
            row_flags.append("Fundamental - Anos Finais")
        if row['QT_MAT_MED'] > 0:
            row_flags.append("Ensino Médio")

        #checa se a escola n pegou nenhuma flag ;3
        if not row_flags:
            row_flags.append("Sem Matrículas")

        flag_col.append(sep.join(row_flags))

    df_mat['Etapas'] = flag_col  
    
    return df_mat

def calcular_parametros(df:pd.DataFrame, df_mat:pd.DataFrame):
    print("calculando parametros...")

    #Listas de variáveis específicas
    #reverificar se tech é exclusiva para alunos ou para adm (adm tem que ser geral msm)
    vars_tech = ['recode_internet','IN_COMPUTADOR','IN_EQUIP_COPIADORA','IN_EQUIP_IMPRESSORA','IN_EQUIP_IMPRESSORA_MULT',
                'IN_EQUIP_SCANNER','IN_EQUIP_NENHUM','IN_EQUIP_DVD','IN_DESKTOP_ALUNO','IN_COMP_PORTATIL_ALUNO',
                'IN_TABLET_ALUNO','IN_ACESSO_INTERNET_COMPUTADOR','IN_ACES_INTERNET_DISP_PESSOAIS','TP_REDE_LOCAL','IN_BANDA_LARGA']

    vars_infantil = ['IN_BANHEIRO_EI','IN_PARQUE_INFANTIL']
    mat_cols = ['CO_ENTIDADE','QT_MAT_INF_CRE','QT_MAT_INF_PRE','QT_MAT_FUND_AI','QT_MAT_FUND_AF','QT_MAT_MED','Etapas']
    #=====================================================================================================================================


    #adiciona as etapas às escolas
    df = df.merge(df_mat[mat_cols], on='CO_ENTIDADE',how='left').copy()
    print(df)

    #garante que vai pegar somente as colunas dicotomizadas
    cols_itens = [c for c in df.columns if c.startswith('IN_') or c.startswith('recode_')]
    
    total_vars = list(dict.fromkeys(cols_itens))

    base_tech = [c for c in vars_tech if c in total_vars]
    base_inf = [c for c in vars_infantil if c in total_vars]
    base_geral = [c for c in total_vars if c not in base_tech and c not in base_inf]

    df_calc = df[total_vars].fillna(0).astype(int) #<- df usado na lib em si

    etapas_config = {
        'creche':{
            'col_mat': 'QT_MAT_INF_CRE',
            'vars': base_geral + base_inf
        },
        'pre_escola':{
            'col_mat': 'QT_MAT_INF_PRE',
            'vars': base_geral + base_inf
        },
        'fundamentai_ai':{
            'col_mat': 'QT_MAT_FUND_AI',
            'vars': base_geral + base_tech
        },
        'fundamental_af':{
            'col_mat': 'QT_MAT_FUND_AF',
            'vars': base_geral + base_tech
        },
        'ensino_medio':{
            'col_mat': 'QT_MAT_MED',
            'vars': base_geral + base_tech
        },
    }

    #Pega uma amostra generosa ao inves de processar todas as escolas de uma vez
    escolas_total = len(df_calc)
    co_entidade = df['CO_ENTIDADE'].values.ravel() if 'CO_ENTIDADE' in df.columns else np.arrange(escolas_total)

    df_resultado = pd.DataFrame({
        'CO_ENTIDADE': co_entidade,
        'NO_ENTIDADE': df['CO_ENTIDADE'].values.ravel(),
        'NO_MUNICIPIO': df['CO_MUNICIPIO'].values.ravel(),
        'SG_UF': df['SG_UF'].values.ravel(),
    })

    params_list = []
    rng = np.random.default_rng(42)

    #calcula 2PL POR ETAPA
    for etapa, cfg in etapas_config.items():
        col_mat = cfg['col_mat'] #<- pega cada etapa da escola
        vars_etapa = list(dict.fromkeys(cfg['vars'])) #<- utiliza somente as variáveis da etapa

        mask_etapa = df[col_mat] > 0
        qtd_escolas_etapa = int(mask_etapa.sum())

        df_resultado[f"theta_{etapa}"] = np.nan
        df_resultado[f"theta_{etapa}"] = np.nan

        if qtd_escolas_etapa < 30:
            logging.warning(f"Etapa {etapa} ignorada na calibração: apenas {qtd_escolas_etapa} escolas com matrícula")
            continue

    
        df_etapa = df_calc.loc[mask_etapa, vars_etapa]

        #Amostragem
        tam_amostra = min(5000, qtd_escolas_etapa)
        amostragem_idx = rng.choice(qtd_escolas_etapa, size=tam_amostra, replace=False)
        df_amostra = df_etapa[amostragem_idx]

        #remove itens sem variância
        var_amostra = df_amostra.std(axis=0)
        itens_validos = var_amostra[var_amostra >= 0.01].index.tolist()

        if len(itens_validos) < 2:
            logging.warning(f"Etapa {etapa} sem itens válidos o suficiente após filtragem")

        respostas_amostra = df_amostra[itens_validos].values.T
        estimativas = twopl_mml(respostas_amostra)
        disc = estimativas['Discrimination'].ravel()
        diff = estimativas['Difficulty'].ravel()

        params_list.append(pd.DataFrame({
            'Etapa':etapa,
            'Questao': itens_validos,
            'Discriminacao': disc,
            'Dificuldade': diff
        }))

        respostas_etapa = df_etapa[itens_validos].values.T
        theta_etapa = ability_eap(respostas_etapa, diff, disc).ravel()
        escore_etapa = (theta_etapa * 10) + 50

        df_resultado.loc[mask_etapa, f"theta_{etapa}"] = theta_etapa
        df_resultado.loc[mask_etapa, f"theta_{etapa}"] = escore_etapa

        logging.info(f"TRI concluida para {etapa} ({qtd_escolas_etapa} escolas, {len(itens_validos)} itens).")

    soma_indice_pond = np.zeros(escolas_total, dtype=float)
    soma_theta_pond = np.zeros(escolas_total, dtype=float)
    soma_mats_pond = np.zeros(escolas_total, dtype=float)

    #cálculo ponderado
    for etapa, cfg in etapas_config.items():
        col_indice = f'indice_{etapa}'
        col_theta = f'theta_{etapa}'
        col_mat = cfg['col_mat']

        valida = df_resultado[col_indice].notna().values
        mats = np.where(valida, df[col_mat].values, 0.0)

        soma_indice_pond += df_resultado[col_indice].fillna(0).value * mats
        soma_theta_pond += df_resultado[col_indice].fillna(0).value * mats
        soma_mats_validas += mats

    df_resultado['Theta_bruto'] = np.where(
        soma_mats_validas > 0,
        soma_theta_pond / soma_mats_validas,
        np.nan
    )
    df_resultado['Indice_infraestrutura'] = np.where(
        soma_mats_validas > 0,
        soma_indice_pond / soma_mats_validas,
        np.nan
    )

    df_params = pd.concat(params_list, ignore_index=True) if params_list else pd.DataFrame(
        columns=['Etapa','Questao','Discriminação','Dificuldade']
    )
    
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





