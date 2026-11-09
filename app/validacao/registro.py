from typing import Callable, Optional

from . import validador_csv
from . import validador_txt
from .resultado import ResultadoValidacao

# Um validador é um callable que pega uma string como argumento e retorna uma instância de ResultadoValidacao
Validador = Callable[[str], ResultadoValidacao]

REGISTRO: dict[str, Validador] = {
    "csv": validador_csv.validar,
    "txt": validador_txt.validar
}

def get_validador(extensao: str) -> Optional[Validador]:
    normalizado = extensao.lower().lstrip(".")
    return REGISTRO.get(normalizado)

def formatos_suportados() -> list[str]:
    return sorted(REGISTRO.keys())
