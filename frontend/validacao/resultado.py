from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class ResultadoValidacao:
    valido: bool
    # retorna: "estrutural" ou "vazio" em caso de erro. None em caso de validação completa.
    fase: Optional[str]
    razao: str

    def to_dict(self) -> dict:
        # Para formatar para JSON.
        return asdict(self)

# construtor para caso de arquivo válido
def ok(razao: str = "Arquivo passou na checagem.") -> ResultadoValidacao:
    return ResultadoValidacao(valido=True, fase=None, razao=razao)

# construtor para caso de arquivo inválido
def falha(fase: str, razao: str) -> ResultadoValidacao:
    return ResultadoValidacao(valido=False, fase=fase, razao=razao)
