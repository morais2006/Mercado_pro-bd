# Mercado Pro — Sistema de Vendas (Trabalho de Banco de Dados)

## Identificação
- **Nome: João Manoel de Sousa Morais
- **Disciplina: Banco de Dados
- **Professor: Anderson

## Sobre o projeto
Sistema web de vendas que demonstra, de forma prática, o uso de três
recursos do PostgreSQL que fazem o banco **processar dados** (e não apenas
armazená-los):

- 1 **View** para relatório agregado;
- 1 **Function** para cálculo do total final de uma venda;
- 1 **Procedure** para registrar uma venda em uma única transação, com
  validações e baixa de estoque.

O problema resolvido é o dia-a-dia de um pequeno comércio/mercado:
cadastrar clientes e produtos, registrar vendas (garantindo estoque e
preço corretos) e consultar um relatório consolidado.

## Tecnologias utilizadas
- **Linguagem:** Python 3.11+
- **Framework web:** Flask (Jinja2 para templates)
- **Driver de banco:** psycopg2-binary (acesso direto, sem ORM)
- **Variáveis de ambiente:** python-dotenv
- **Front-end:** HTML + CSS próprio (tema escuro) + ícones SVG inline
- **Banco de dados:** PostgreSQL (instalação local)

## Banco de dados

### SGBD
PostgreSQL local (versão 13 ou superior). A aplicação se conecta usando
a connection string definida em `DATABASE_URL`.

### Principais tabelas
- `clientes` (id, nome, email, telefone, criado_em)
- `produtos` (id, nome, preco, estoque)
- `vendas` (id, id_cliente, data_venda, desconto_percentual)
- `itens_venda` (id, id_venda, id_produto, quantidade, preco_unitario)

Todas com PKs, FKs e CHECKs (preço ≥ 0, estoque ≥ 0, quantidade > 0,
desconto entre 0 e 100).

### Recursos de banco criados

| Recurso | Nome | Finalidade | Usado na tela |
|---|---|---|---|
| View | `vw_relatorio_vendas` | Junta vendas + clientes + itens_venda e retorna por venda: id, data, cliente, qtd. de itens e subtotal. | **Relatório de vendas** |
| Function | `fn_total_venda(p_id_venda)` | Soma `quantidade * preco_unitario` dos itens e aplica o desconto da venda, retornando o total final. | **Detalhe da venda** |
| Procedure | `sp_realizar_venda(p_id_cliente, p_itens jsonb, p_desconto)` | Em uma única transação: valida cliente e estoque, insere a venda, insere os itens pelo preço atual do produto e baixa o estoque. Lança `RAISE EXCEPTION` em caso de erro. | **Nova venda** |

## Estrutura do repositório
```
projeto-vendas-bd/
├── src/
│   ├── app.py
│   ├── db.py
│   ├── templates/
│   └── static/
├── database/
│   ├── 00_criar_banco.sql   (opcional, cria o banco)
│   ├── tables/      01_criar_tabelas.sql
│   ├── views/       02_vw_relatorio_vendas.sql
│   ├── functions/   03_fn_total_venda.sql
│   ├── procedures/  04_sp_realizar_venda.sql
│   └── inserts/     05_dados_exemplo.sql
├── docs/roteiro_video.md
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Como executar

### 1. Instalar o PostgreSQL
- **Windows:** baixe o instalador em
  <https://www.postgresql.org/download/windows/>. Durante a instalação,
  defina uma senha para o usuário `postgres` e **anote-a**. Deixe a
  porta padrão `5432`.
- **Linux (Debian/Ubuntu):** `sudo apt install postgresql`
- **Mac (Homebrew):** `brew install postgresql && brew services start postgresql`

Verifique que o serviço está rodando:
```bash
psql -U postgres -c "SELECT version();"
```

### 2. Criar o banco `mercado_pro`
No terminal (ou pelo pgAdmin), rode:
```bash
psql -U postgres -c "CREATE DATABASE mercado_pro;"
```
Ou execute o script `database/00_criar_banco.sql` conectado como
`postgres`.

### 3. Rodar os scripts SQL (na ordem)
Conecte-se ao banco recém-criado e execute os cinco arquivos **na ordem**:
```bash
psql -U postgres -d mercado_pro -f database/tables/01_criar_tabelas.sql
psql -U postgres -d mercado_pro -f database/views/02_vw_relatorio_vendas.sql
psql -U postgres -d mercado_pro -f database/functions/03_fn_total_venda.sql
psql -U postgres -d mercado_pro -f database/procedures/04_sp_realizar_venda.sql
psql -U postgres -d mercado_pro -f database/inserts/05_dados_exemplo.sql
```

Alternativa visual: abra o **pgAdmin**, clique no banco `mercado_pro`,
abra o **Query Tool**, cole o conteúdo de cada arquivo (um por vez,
nessa ordem) e clique em **Executar** (F5).

### 4. Configurar o .env
Copie `.env.example` para `.env` e edite:
```
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/mercado_pro
```
Troque `SUA_SENHA` pela senha do usuário `postgres` definida na instalação.

### 5. Instalar dependências e rodar o Flask
```bash
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

# (Opcional) testar conexão e checar objetos do banco:
python src/testar_conexao.py

python src/app.py
```

Abra <http://127.0.0.1:5000> no navegador.

## Dicas de solução de problemas
- **`password authentication failed`** — a senha no `.env` está errada.
  Confira a senha definida na instalação do PostgreSQL.
- **`could not connect to server`** — o serviço do PostgreSQL não está
  rodando. No Windows, abra "Serviços" e inicie **postgresql-x64-xx**.
- **`database "mercado_pro" does not exist`** — você pulou o passo 2.
  Rode `CREATE DATABASE mercado_pro;` como `postgres`.
- **`relation "clientes" does not exist`** — você pulou o passo 3 ou
  rodou os scripts em outro banco. Confira com
  `psql -U postgres -d mercado_pro -c "\dt"`.
- **Caracteres estranhos (ex.: "cafÃ©")** — o banco não está em UTF-8.
  Recrie com `CREATE DATABASE mercado_pro ENCODING 'UTF8' TEMPLATE template0;`.

  link do meu vídeo [   ]
