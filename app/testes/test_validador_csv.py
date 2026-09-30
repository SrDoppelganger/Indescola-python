import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validacao import validador_csv

def write(tmp_path, nome, conteudo: bytes) -> str:
    path = tmp_path / nome
    path.write_bytes(conteudo)
    return str(path)

def test_csv_valido_passa(tmp_path):
    p = write(tmp_path, "ok.csv", b"a,b,c\n1,2,3\n4,5,6\n")
    resultado = validador_csv.validar(p)
    assert resultado.valido is True
    assert resultado.fase is None

def test_arquivo_zero_bytes_vazio(tmp_path):
    p = write(tmp_path, "zero_bytes.csv", b"")
    resultado = validador_csv.validar(p)
    assert resultado.valido is False
    assert resultado.fase == "vazio"
    assert "zero bytes" in resultado.razao

def test_arquivo_apenas_cabecalho_vazio(tmp_path):
    p = write(tmp_path, "apenas_cabecalho.csv", b"a,b,c\n")
    resultado = validador_csv.validar(p)
    assert resultado.valido is False
    assert resultado.fase == "vazio"
    assert "sem dados" in resultado.razao

def test_arquivo_com_apenas_espaco_em_branco_vazio(tmp_path):
    p = write(tmp_path, "branco.csv", b"\n\n   \n\n")
    resultado = validador_csv.validar(p)
    assert resultado.valido is False
    assert resultado.fase == "vazio"

def test_arquivo_binario_falha_estrutural(tmp_path):
    p = write(tmp_path, "falso.csv", b"\x89PNG\r\n\x1a\n\x00\x01\x02")
    resultado = validador_csv.validar(p)
    assert resultado.valido is False
    assert resultado.fase == "estrutural"

def test_arquivo_inexistente_falha_estrutural(tmp_path):
    p = str(tmp_path / "nao_exite.csv")
    resultado = validador_csv.validar(p)
    assert resultado.valido is False
    assert resultado.fase == "estrutural"

def test_arquivo_com_unterminated_quoted_field_falha_estrutural(tmp_path):
    p = write(tmp_path, "falso.csv", b'a,b,c\n"unterminated,2,3\n')
    resultado = validador_csv.validar(p)
    assert resultado.valido is False
    assert resultado.fase == "estrutural"
