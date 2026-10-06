"""
Placeholder para pipeline real de processamento em C/Python.
"""
from typing import List, TypedDict

import pipeline_dados
from validacao.resultado import ResultadoValidacao

class ArquivosPipeline(TypedDict):
    path: str
    formato: str
    resultado_validacao: ResultadoValidacao

#TODO substituir por input do usuário
var_path = 'bases/variaveis.txt'
mat_path = 'bases/matriculas_censo.csv'
output_path = 'resultados/'

#adicionar coiso de backend aq

def enviar_para_pipeline(file_path: str, formato_arquivo: str, resultado_validacao: ResultadoValidacao) -> None:
    pipeline_dados.processar(file_path, var_path)

def novo_enviar_para_pipeline(arquivos: List[ArquivosPipeline], pasta_saida: str) -> None:
    pass
