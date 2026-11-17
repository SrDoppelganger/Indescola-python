# Indescola

Uma aplicação que calcula o índice de infraestrutura por escola a partir do Censo Escolar do INEP.

## Integrantes
- Arthur Albuquerque Pereira - 01603940
- Davi Fontes Barbosa - 01589639
- Fábio Coutinho Aroucha - 01597225
- Lucas Henrique Lins da Silva - 01613905
- Miguel Luna Giovannetti de Arruda Amorim - 01590491

## Objetivo da Solução

Calcular, para cada escola pública em atividade presente no censo, um índice de infraestrutura, e disponibilizar parâmetros estimados para cada item. O índice bem de um modelo de Teoria de Resposta ao Item (2PL), aplicado a indicadores de presença/ausência de itens de infraestrutura como água, energia, esgoto, etc.

## Tecnologias Utilizadas

| Tecnologia | Descrição |
| --- | --- |
| Python 3.9+ | Linguagem do backend (validação, ponte com a interface e cálculo). |
| pywebview | Janela desktop que hospeda o frontend. |
| HTML, CSS, Javascript | Interface |
| pandas | Leitura do censo, filtros, agregações e escrita dos CSV. |
| numpy | Recodificação de variáveis e amostragem aleatória |
| girth | Ajuste do modelo 2PL |
| pytest | Testes automatizados dos validadores (em desenvolvimento) |

Formatos de dados: CSV e TXT.

## Requisitos Necessários para execução

- Python 3.9 ou superior
- pip + venv
- Pacotes Python: pywebview, pandas, numpy, girth, pytest.
- Arquivos de entrada: CSV do censo, CSV de matrículas e TXT de variáveis.

## Instruções de instalação e configuração

1. Obter o projeto e entrar na pasta raiz

```
cd <pasta-do-projeto>
```

2. Criar e ativar o ambiente virtual
```
python3 -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
```

3. Instalar as dependências
```
pip install -r requirements.txt
```
ou
```
pip install -r requirements-dev.txt
```

A diferença entre os dois é o acesso a testes automatizados, onde requirements-dev permite testes automatizados com pytest.

4. **Apenas para Linux, se a janela não abrir.** Instalar o backend gráfico

(Debian/Ubuntu):
```
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1
```

## Execução

### Iniciando a aplicação
```
cd app
python3 main.py
```

### Usando a interface
1. Em **Censo**, **Matrícula** e **Variáveis (.txt)**, clique em *Escolher...* eselecione o arquivo apropriado.
2. Em **Pasta de saída**, clique em *Escolher...* e selecione uma pasta.
3. Quando os três arquivos forem validados e a pasta escolhida, o botão **Calcular** é habilitado; clique nele.
4. Aguarde a mensagem "Enviado. A saída vai para: ..."; os arquivos que resultam do cálculo estarão na pasta de saída.

### Executar testes
Requer pytest
```
python3 -m pytest
```

## Estrutura do projeto
+ Indescola-python
  + README.md
  + requirements.txt
  + requirements-dev.txt
  + app/
    + main.py               
    + api.py                
    + pipeline_stub.py      
    + pipeline_dados.py     
    + validacao/            
      + registro.py      
      + resultado.py      
      + utils_encoding.py 
      + validador_csv.py  
      + validador_txt.py  
    + frontend/
      + index.html
      + app.js
      + style.css
    + testes/
      + test_validador_csv.py
      + test_validador_txt.py
      + arquivos/         
      + casos/            