import csv
import io
from pathlib import Path

from .resultado import ResultadoValidacao, ok, falha

def validar(file_path: str) -> ResultadoValidacao:
    path = Path(file_path)

    try:
        raw = path.read_bytes()
    except OSError as exc:
        return falha("estrutural", f"Arquivo nao pode ser lido: ${exc}")

    if len(raw) == 0:
        return falha("vazio", "Arquivo vazio(zero bytes).")

    try:
        texto = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return falha("estrutural", "Arquivo invalido como texto e nao pode ser lido como CSV.")

    try:
        linhas = list(csv.reader(io.StringIO(texto), strict=True))
    except csv.Error as exc:
        return falha("estrutural", f"Arquivo não pode ser lido como CSV: ${exc}")

    linhas_nao_vazias = [linha for linha in linhas if any(cell.strip() for cell in linha)]

    if len(linhas_nao_vazias) == 0:
        return falha("vazio", "Arquivo vazio")

    if len(linhas_nao_vazias) == 1:
        return falha("vazio", "Arquivo contém apenas cabecalho, sem dados.")

    return ok()


    
