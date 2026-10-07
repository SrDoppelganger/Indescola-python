from pathlib import Path
from .resultado import ResultadoValidacao, ok, falha
from .utils_encoding import decodificar_texto

def validar(file_path: str) -> ResultadoValidacao:
    path = Path(file_path)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return falha("estrutural", f"Arquivo não pode ser lido: {exc}")

    if len(raw) == 0:
        return falha("vazio", "Arquivo vazio(zero bytes).")

    try:
        texto, formato = decodificar_texto(raw)
    except UnicodeDecodeError:
        return falha("estrutural", "Arquivo inválido nos formatos suportados.")

    if not texto.strip():
        return falha("vazio", "Arquivo sem conteúdo usável(vazio ou apenas espaços em branco).")

    return ok(f"Arquivo .txt válido não vazio(formato: {formato}).")
