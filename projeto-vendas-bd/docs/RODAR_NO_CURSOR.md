# Passo a passo — rodar o projeto e validar o banco de dados

Guia direto para o **Cursor** (ou qualquer IDE) executar o projeto do zero
em uma máquina nova e confirmar que o PostgreSQL está respondendo.

> **Pré-requisito único:** ter o **PostgreSQL** instalado localmente.
> Durante a instalação, foi definida uma senha para o usuário `postgres` —
> você vai precisar dela.

---

## 1. Abrir o projeto no Cursor

```powershell
cd C:\Users\Ryan\projeto-vendas-bd
cursor .
```

Confirme que a estrutura está assim na barra lateral:

```
projeto-vendas-bd/
├── src/
│   ├── app.py
│   ├── db.py
│   ├── testar_conexao.py
│   ├── templates/
│   └── static/
├── database/
│   ├── 00_criar_banco.sql
│   ├── tables/   01_criar_tabelas.sql
│   ├── views/    02_vw_relatorio_vendas.sql
│   ├── functions/03_fn_total_venda.sql
│   ├── procedures/04_sp_realizar_venda.sql
│   └── inserts/  05_dados_exemplo.sql
├── requirements.txt
├── .env.example
└── README.md
```

---

## 2. Verificar se o PostgreSQL está rodando

No **terminal do Cursor** (`Ctrl + ' `), rode:

```powershell
psql -U postgres -c "SELECT version();"
```

- Vai pedir a senha do usuário `postgres`.
- Se aparecer algo como `PostgreSQL 16.x on x86_64-windows ...`, **está OK**.
- Se der erro `psql: command not found`, o PostgreSQL não está no PATH —
  procure por `psql.exe` em `C:\Program Files\PostgreSQL\<versao>\bin` e
  rode usando o caminho completo.
- Se der `could not connect to server`, abra o app **Serviços** do Windows,
  procure `postgresql-x64-XX` e clique em **Iniciar**.

---

## 3. Criar o banco `mercado_pro`

```powershell
psql -U postgres -c "CREATE DATABASE mercado_pro;"
```

Se já existir, aparece `ERROR: database "mercado_pro" already exists` —
pode ignorar.

Confirme que foi criado:

```powershell
psql -U postgres -c "\l" | findstr mercado_pro
```

Tem que aparecer uma linha com `mercado_pro`.

---

## 4. Rodar os scripts SQL na ordem

**Importante: tem que ser nessa ordem**, porque uma coisa depende da outra.

```powershell
psql -U postgres -d mercado_pro -f database\tables\01_criar_tabelas.sql
psql -U postgres -d mercado_pro -f database\views\02_vw_relatorio_vendas.sql
psql -U postgres -d mercado_pro -f database\functions\03_fn_total_venda.sql
psql -U postgres -d mercado_pro -f database\procedures\04_sp_realizar_venda.sql
psql -U postgres -d mercado_pro -f database\inserts\05_dados_exemplo.sql
```

Cada comando deve terminar sem `ERROR`. Mensagens tipo
`CREATE TABLE`, `CREATE VIEW`, `CREATE FUNCTION`, `CREATE PROCEDURE`,
`INSERT 0 N` são **normais** — significa que funcionou.

---

## 5. Validar os objetos criados no banco

Essa é a conferência que importa — garante que **tabelas, view, function e
procedure existem**.

```powershell
psql -U postgres -d mercado_pro -c "\dt"
```

Esperado:

```
            List of relations
 Schema |    Name     | Type  |  Owner
--------+-------------+-------+----------
 public | clientes    | table | postgres
 public | itens_venda | table | postgres
 public | produtos    | table | postgres
 public | vendas      | table | postgres
```

```powershell
psql -U postgres -d mercado_pro -c "\dv"
```

Esperado: `vw_relatorio_vendas`.

```powershell
psql -U postgres -d mercado_pro -c "\df fn_total_venda"
```

Esperado: linha com `fn_total_venda | numeric | ...`.

```powershell
psql -U postgres -d mercado_pro -c "\df sp_realizar_venda"
```

Esperado: linha com `sp_realizar_venda | | ... | proc`.

E para confirmar que os dados de exemplo entraram:

```powershell
psql -U postgres -d mercado_pro -c "SELECT COUNT(*) AS clientes FROM clientes; SELECT COUNT(*) AS produtos FROM produtos; SELECT COUNT(*) AS vendas FROM vendas;"
```

Esperado: 5 clientes, 10 produtos, 3 vendas.

---

## 6. Configurar o arquivo `.env`

```powershell
copy .env.example .env
notepad .env
```

No `.env`, edite a linha:

```
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/mercado_pro
```

Troque `SUA_SENHA` pela senha do usuário `postgres` que você definiu na
instalação. **Salve e feche o notepad.**

> Se a sua senha tem caractere especial (`@`, `#`, `/`, `:`, `?`), é mais
> fácil trocar para uma senha simples só com letras e números no pgAdmin
> antes de preencher aqui.

---

## 7. Criar o ambiente virtual e instalar dependências

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Depois do `activate`, o terminal mostra `(venv)` no começo da linha.

---

## 8. Rodar o teste de conexão (etapa de verificação final)

Esse script já conecta no banco, lista o que achou e avisa o que falta:

```powershell
python src\testar_conexao.py
```

Saída esperada (resumida):

```
Conexão OK em postgresql://postgres:***@localhost:5432/mercado_pro
Tabela clientes ..... OK
Tabela produtos ..... OK
Tabela vendas ....... OK
Tabela itens_venda .. OK
View vw_relatorio_vendas .. OK
Function fn_total_venda ... OK
Procedure sp_realizar_venda OK

Tudo pronto. Pode rodar: python src/app.py
```

Se aparecer qualquer `FAIL`, veja a **seção de problemas** abaixo.

---

## 9. Subir a aplicação Flask

```powershell
python src\app.py
```

Deve mostrar algo como:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Abra <http://127.0.0.1:5000> no navegador.

---

## 10. Testar as 3 telas que usam recursos do banco

Com o app rodando, confira cada tela — essas são as 3 que o professor
precisa ver no vídeo:

| Tela | URL | O que precisa aparecer |
|---|---|---|
| **Relatório de vendas** (VIEW) | <http://127.0.0.1:5000/vendas> | 3 vendas listadas, com cliente, data, qtd. de itens e subtotal. |
| **Detalhe de uma venda** (FUNCTION) | <http://127.0.0.1:5000/vendas/1> | Itens da venda e o **Total final (com desconto)** calculado pela função. |
| **Nova venda** (PROCEDURE) | <http://127.0.0.1:5000/vendas/nova> | Formulário com cliente, itens e desconto. Clicar em **Confirmar** registra a venda e redireciona para o relatório. |

Também valide:

- `/clientes` lista os 5 clientes de exemplo.
- `/produtos` lista os 10 produtos de exemplo.
- Botão **Excluir** pede confirmação antes de apagar.
- Em **Nova venda**, o campo "Total estimado" atualiza enquanto você muda produto/quantidade/desconto.

---

## Problemas comuns e como resolver

### `password authentication failed for user "postgres"`
A senha no `.env` está errada. Reabra `.env` e corrija.

### `database "mercado_pro" does not exist`
Pulou o passo 3. Rode:
`psql -U postgres -c "CREATE DATABASE mercado_pro;"`

### `relation "clientes" does not exist`
Pulou o passo 4 (ou rodou os scripts no banco errado). Confirme com
`psql -U postgres -d mercado_pro -c "\dt"` e, se vier vazio, rode os
5 scripts novamente.

### `could not connect to server: Connection refused`
O serviço do PostgreSQL não está no ar. Abra **Serviços** do Windows e
inicie `postgresql-x64-XX`.

### `psql: command not found`
Adicione `C:\Program Files\PostgreSQL\<versao>\bin` ao `PATH` do Windows,
ou chame com caminho completo:
`"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres ...`

### A página inicial abre, mas as outras dão `UndefinedTable`
Tabelas não foram criadas no banco que o `.env` aponta. Verifique:
1. O nome do banco no `.env` bate com o que recebeu os scripts (`mercado_pro`).
2. Executou os 5 scripts com `-d mercado_pro` (passo 4).

### Caracteres acentuados aparecem como `cafÃ©` ou `ü` virou lixo
O banco foi criado com encoding diferente de UTF-8. Recrie:
```powershell
psql -U postgres -c "DROP DATABASE mercado_pro;"
psql -U postgres -c "CREATE DATABASE mercado_pro ENCODING 'UTF8' TEMPLATE template0;"
```
E rode de novo os scripts do passo 4.

---

## Resumo (checklist para marcar antes de gravar o vídeo)

- [ ] `psql -U postgres -c "SELECT version();"` responde.
- [ ] `psql -U postgres -d mercado_pro -c "\dt"` mostra 4 tabelas.
- [ ] `psql -U postgres -d mercado_pro -c "\dv"` mostra `vw_relatorio_vendas`.
- [ ] `python src\testar_conexao.py` termina com "Tudo pronto".
- [ ] `python src\app.py` sobe sem erro em `http://127.0.0.1:5000`.
- [ ] As 6 páginas (Home, Clientes, Produtos, Nova venda, Relatório, Detalhe) abrem sem exceção.
- [ ] Consegui cadastrar um cliente, um produto e registrar uma venda.
