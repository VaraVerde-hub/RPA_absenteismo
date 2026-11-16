# RPA de Absenteísmo

Rotina Python para ler marcações no SQL Server, classificar faltas/atrasos e gerar relatórios CSV.
**Por padrão não envia e-mails**. A branch de melhorias não foi testada contra sistemas reais.

## Segurança (ação urgente)

Credenciais de banco e SMTP foram publicadas em versões anteriores do config.py.
**Revogue/troque imediatamente essas senhas**. A remoção do arquivo atual **não remove**
os segredos do histórico Git, de forks ou de caches. Avalie reescrever o histórico com
ferramentas apropriadas depois da rotação, coordenando com colaboradores.
Use uma conta SQL Server somente de leitura e limite acesso aos relatórios de RH.

## Preparação

1. Python 3.11+ e Microsoft ODBC Driver 18 instalado no Windows.
2. python -m pip install -r requirements.txt
3. Copie .env.example para .env (fora do Git) e configure usuário somente leitura.
4. Testes locais: python -m pytest -q
5. Execução local: python main.py --days 7 --output output
6. Envio REAL (somente quando aprovado e configurado): python main.py --send

O comando padrão grava CSVs e output/runs.jsonl; nunca envia e-mail.
A saída contém dados pessoais de RH: restrinja permissões e configure retenção.

## Regras e limitações

- Inclui funcionários sem registro pela combinação de funcionários cadastrados e dias
  úteis configurados, ao invés de depender de um INNER JOIN com ponto.
- DIAS_TRABALHO (0=segunda, 6=domingo) e FERIADOS (datas ISO) são políticas globais.
  **Não usar para decisões trabalhistas antes de integrar escala individual, férias,
  afastamentos, folgas e feriados regionais.** Sem justificativas o rótulo de falta
  é provisório.
- Assumem-se uma linha de ponto por funcionário/dia, com entrada e saída em colunas.
  Duplicidades provocam erro explícito; caso o banco use batidas isoladas, adapte a
  consulta e normalize marcações/turnos antes do cálculo.
- Turnos atravessando a meia-noite são tratados com base no horário esperado, mas
  batidas complexas e horas extras precisam de regras específicas.
- Agrupamento usa funcionario_id + nome, evitando juntar homônimos.
- Relatório cobre datas desde hoje - days até ontem (limite superior exclusivo).
- A conexão usa TLS com validação de certificado; configure certificado confiável.

## Arquitetura

main.py: CLI e orquestração; config.py: configuração segura; db.py: acesso SQL;
absenteismo.py: regras puras; reports.py: CSV e histórico; email_sender.py: SMTP.
tests/: testes sem SQL Server nem envio de e-mail.

## Plano de migração estrutural

A separação por responsabilidades acima é preservada para compatibilidade com o
agendador existente. Em próximo PR, converter para pacote src/ após testes de
integração e configuração de paths de execução em produção.
