"""
Código de utilidade para decodificação de texto.
"""

from typing import Tuple

FORMATOS_SUPORTADOS: Tuple[str, ...] = (
    "utf-8-sig",
    "utf-8",
    "cp1252",
    "latin-1",
)

def decodificar_texto(raw: bytes) -> Tuple[str, str]:
    """
    Tenta decodificar, em ordem, de acordo com FORMATOS_SUPORTADOS.
    Retorna (texto, formato) na primeira decodificação bem sucedida.
    Leva a UnicodeDecodeError se não conseguir decodificar em nenhum formato.
    """
    ultimo_erro: UnicodeDecodeError = None
    for formato in FORMATOS_SUPORTADOS:
        try:
            return raw.decode(formato), formato
        except UnicodeDecodeError as exc:
            ultimo_erro = exc
            continue
    raise ultimo_erro
