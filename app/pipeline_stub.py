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


#adicionar coiso de backend aq

def enviar_para_pipeline(file_path: str, formato_arquivo: str, resultado_validacao: ResultadoValidacao) -> None:
    pass

def novo_enviar_para_pipeline(arquivos: List[ArquivosPipeline], pasta_saida: str) -> None:
    censo_path: str = arquivos[0].get('path')
    mat_path: str = arquivos[1].get('path')
    var_path: str = arquivos[2].get('path')

    pipeline_dados.processar(censo_path, var_path, mat_path, pasta_saida)
