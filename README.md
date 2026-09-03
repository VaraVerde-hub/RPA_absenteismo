# Automação de Absenteísmo

Projeto em Python que busca registros de ponto (entrada/saída) em um
banco de dados SQL, calcula atrasos e saídas antecipadas por
funcionário e envia um relatório resumido por email — pensado para
rodar diariamente de forma automática.

## Estrutura

```
absenteismo_automation/
├── config.py         # todas as configurações (banco, email, regras)
├── db.py              # consulta ao banco de dados
├── absenteismo.py     # cálculo de atrasos / saídas antecipadas
├── email_sender.py    # montagem e envio do email
├── main.py             # script principal (rode este)
└── requirements.txt
```

## 1. Ajuste o `config.py` para a sua base real

O código assume duas tabelas: uma de funcionários e uma de registros
de ponto. **Troque os nomes de tabela/coluna em `config.py`** para
bater com sua base de dados real:

```python
TABELA_FUNCIONARIOS = "funcionarios"
COL_FUNC_ID = "id"
COL_FUNC_NOME = "nome"
COL_FUNC_EMAIL = "email"
COL_FUNC_HORARIO_ENTRADA_ESPERADO = "horario_entrada_esperado"
COL_FUNC_HORARIO_SAIDA_ESPERADO = "horario_saida_esperado"

TABELA_REGISTROS = "registros_ponto"
COL_REG_FUNCIONARIO_ID = "funcionario_id"
COL_REG_DATA = "data"
COL_REG_HORA_ENTRADA = "hora_entrada"
COL_REG_HORA_SAIDA = "hora_saida"
```

Se a sua base tiver uma estrutura bem diferente (por exemplo, um
único registro por "batida" em vez de entrada/saída no mesmo dia),
me avise e eu adapto a query em `db.py`.

## 2. Instale as dependências

```bash
pip install -r requirements.txt
# e o driver do seu banco, por exemplo:
pip install psycopg2-binary   # PostgreSQL
```

## 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na pasta do projeto (não versione este
arquivo — coloque-o no `.gitignore`):

```
DB_CONNECTION_STRING=postgresql+psycopg2://usuario:senha@host:5432/banco
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seuemail@empresa.com
SMTP_PASSWORD=sua_senha_de_app
EMAIL_DESTINATARIOS=gestor1@empresa.com,gestor2@empresa.com
```

E no início do `main.py`, adicione (se optar por usar `.env`):

```python
from dotenv import load_dotenv
load_dotenv()
```

> **Gmail**: se usar Gmail, gere uma "Senha de App" nas configurações
> de segurança da conta — a senha normal não funciona com SMTP.

## 4. Teste manualmente

```bash
python main.py
```

Se der erro de conexão com o banco ou de login SMTP, a mensagem vai
indicar exatamente qual variável revisar.

## 5. Agende para rodar todo dia

### Linux/Mac (cron)

```bash
crontab -e
```

Adicione a linha (roda todo dia às 7h da manhã):

```
0 7 * * * cd /caminho/para/absenteismo_automation && /usr/bin/python3 main.py >> log_absenteismo.log 2>&1
```

### Windows (Agendador de Tarefas)

1. Abra o "Agendador de Tarefas" → "Criar Tarefa Básica"
2. Defina o gatilho como "Diariamente" no horário desejado
3. Ação: "Iniciar um programa"
   - Programa: caminho do `python.exe`
   - Argumentos: `main.py`
   - Iniciar em: caminho da pasta do projeto

## Regras de cálculo (ajustáveis em `config.py`)

- `TOLERANCIA_ATRASO_MINUTOS` (padrão 10 min): atrasos menores que
  isso não contam como ocorrência.
- `TOLERANCIA_SAIDA_ANTECIPADA_MINUTOS` (padrão 10 min): idem para
  saída antecipada.
- `PERIODO_RELATORIO_DIAS` (padrão 1): quantos dias olhar para trás
  a cada execução. Como a automação roda diariamente, o padrão
  cobre o dia anterior.

## Próximos passos possíveis

- Anexar o relatório detalhado (dia a dia) como planilha Excel no
  email, além do resumo.
- Gerar um dashboard (ex: com Streamlit) para visualizar tendências
  de absenteísmo ao longo do tempo.
- Adicionar alertas quando um funcionário ultrapassar um limite de
  ocorrências no mês.
