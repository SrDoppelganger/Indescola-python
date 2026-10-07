from pathlib import Path
from typing import Optional

import webview

from validacao.registro import get_validador, formatos_suportados
from pipeline_stub import enviar_para_pipeline, novo_enviar_para_pipeline

ARQUIVOS = {
    "censo_csv": {"rotulo": "Censo", "tipos": ("Arquivo CSV (*.csv)",)},
    "matriculas_csv": {"rotulo": "Matriculas", "tipos": ("Arquivo CSV (*.csv)",)},
    "variaveis_txt": {"rotulo": "Variaveis", "tipos": ("Arquivo de texto (*.txt)",)}
}

class Api:
    def __init__(self):
        self.selecionados: dict[str, Optional[dict]] = {arquivo: None for arquivo in ARQUIVOS}
        self.pasta_saida: Optional[str] = None


    def escolher_arquivo(self, arquivo: str):
        if arquivo not in ARQUIVOS:
            raise ValueError(f"Arquivo Desconhecido: {arquivo}")
        janela = webview.windows[0]
        selecao = janela.create_file_dialog(webview.FileDialog.OPEN, file_types=ARQUIVOS[arquivo]["tipos"])

        if not selecao:
            return None
        
        resultado = self._validar_path(selecao[0])
        self.selecionados[arquivo] = resultado

        return resultado

    def escolher_pasta_saida(self):
        window = webview.windows[0]
        selecao = window.create_file_dialog(webview.FileDialog.FOLDER)
        if not selecao:
            return None
        self.pasta_saida = selecao[0]
        return self.pasta_saida

    def get_arquivos_status(self) -> dict:
        return {
            "selecionados": self.selecionados,
            "pasta_saida": self.pasta_saida,
            "pronto": self._pronto()
        }

    def submeter_arquivos(self) -> dict:
        if not self._pronto():
            return {"enviado": False, "motivo": self._nao_pronto_motivo()}
        arquivos = [
            {"path": selecionado["path"], "formato": selecionado["formato"], "resultado_validacao": selecionado}
            for selecionado in self.selecionados.values()
        ]
        novo_enviar_para_pipeline(arquivos, self.pasta_saida)
        return {"enviado": True, "pasta_saida": self.pasta_saida}

    def _pronto(self) -> bool:
        if self.pasta_saida is None:
            return False
        return all(selecionado is not None and selecionado["valido"] for selecionado in self.selecionados.values())

    def _nao_pronto_motivo(self) -> str:
        faltando = [ARQUIVOS[arquivo]["rotulo"] for arquivo, sel in self.selecionados.items() if sel is None]
        invalidos = [ARQUIVOS[arquivo]["rotulo"] for arquivo, sel in self.selecionados.items() if sel and not sel["valido"]]
        partes = []
        if faltando: partes.append(f"arquivos faltando: {', '.join(faltando)}")
        if invalidos: partes.append(f"invalidos: {', '.join(invalidos)}")
        if self.pasta_saida is None: partes.append("nenhuma pasta de saida selecionada")
        return "; ".join(partes) or "invalido"

    def _validar_path(self, raw_path: str) -> dict:
        path = Path(raw_path)
        extensao = path.suffix.lstrip(".").lower()
        validador = get_validador(extensao)

        if validador is None:
            formatos = ", ".join(f".{fmt}" for fmt in formatos_suportados())
            return {
                "path": str(path), 
                "nome_arquivo": path.name, 
                "formato": extensao,
                "valido": False,
                "fase": "estrutural",
                "razao":    f"Tipo de arquivo nao suportado: .{extensao or '?'}. "
                            f"Formatos Suportados: {formatos}.",
            }

        resultado = validador(str(path))

        resposta = resultado.to_dict()
        resposta.update({"path": str(path), "nome_arquivo": path.name, "formato": extensao})
        return resposta
