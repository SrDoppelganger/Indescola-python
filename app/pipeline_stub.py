"""
Placeholder para pipeline real de processamento em C/Python.
"""
import pipeline_dados
from validacao.resultado import ResultadoValidacao

#adicionar coiso de backend aq

def enviar_para_pipeline(file_path: str, formato_arquivo: str, resultado_validacao: ResultadoValidacao) -> None:
    pipeline_dados.processar(file_path)
