from pathlib import Path

import webview

from validacao.registro import get_validador, formatos_suportados
from pipeline_stub import enviar_para_pipeline

class Api:
    def escolher_e_validar_arquivo(self):
        janela = webview.windows[0]
        selecao = janela.create_file_dialog(webview.FileDialog.OPEN)

        if not selecao:
            return None

        return self._validar_path(selecao[0])

    def _validar_path(self, raw_path: str) -> dict:
        path = Path(raw_path)
        extensao = path.suffix.lstrip(".").lower()
        validador = get_validador(extensao)

        if validador is None:
            formatos = ", ".join(f".{fmt}" for fmt in formatos_suportados())
            return {
                "nome_do_arquivo": path.name,
                "valido": False,
                "fase": "estrutural",
                "razao":    f"Tipo de arquivo nao suportado: .{extensao or '?'}. "
                            f"Formatos Suportados: {formatos}.",
            }

        resultado = validador(str(path))

        pipeline_rodou = False
        if resultado.valido:
            enviar_para_pipeline(str(path), extensao, resultado)
            pipeline_rodou = True

        resposta = resultado.to_dict()
        resposta["nome_do_arquivo"] = path.name
        resposta["pipeline_rodou"] = pipeline_rodou
        return resposta
