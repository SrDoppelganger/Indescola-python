# Indescola

## Setup

Requer Python 3.9+.

```bash
cd indicescola
python3 -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt # para usar
## OU
pip install -r requirements-dev.txt # para devs, com testes usando pytest
```

No Linux talvez você também precise
de algumas instalações adicionais, por exemplo, no Debian/Ubuntu:

```bash
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1
```

(Nome de pacotes variam de acordo com distro/versão, se `pip install` funciona mas a janela não abre, cheque o que pode estar faltando.)

## Rodando

Verifique se o ambiente virtual python está rodando corretamente, caso contrário, rode `python3 -m venv .venv`

```bash
python3 main.py
```

## Testes

```bash
python3 -m pytest
```

## Limitações
O validador apenas checa o formato do arquivo por sua EXTENÇÃO(.csv), e não examinando o conteúdo do arquivo ou sua estrutura, isso significa que se alguém renomeia um .docx para .csv por exemplo, ele pode falhar quando faz a checagem. É recomendado que no futuro essa checagem seja capaz de checar o conteúdo em si, o que permitiria compreender erros melhor.
