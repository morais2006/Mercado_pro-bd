# Mercado Pro — Sistema de Vendas com PostgreSQL

## Identificação
- Nome: João Manoel de Sousa Morais
- Disciplina: Banco de Dados
- Professor: Anderson

## Sobre o projeto
Este projeto é um sistema web de vendas desenvolvido para demonstrar, na prática, como o PostgreSQL pode ir além do armazenamento de dados e executar processamento diretamente no banco.

A aplicação foi criada para resolver o fluxo cotidiano de um pequeno comércio, permitindo:
- cadastrar clientes;
- cadastrar produtos;
- registrar vendas com validação de estoque;
- calcular o valor final de cada venda automaticamente;
- consultar um relatório consolidado das vendas realizadas.

Para isso, o sistema utiliza:
- 1 view para gerar um relatório agregado;
- 1 function para calcular o total final de uma venda;
- 1 procedure para registrar uma venda em uma única transação, com validações e baixa de estoque.

O objetivo principal é tornar o processo de vendas mais seguro, organizado e eficiente, garantindo que as informações sejam tratadas com consistência no banco de dados.

## Tecnologias utilizadas
- Linguagem: Python 3.11+
- Framework web: Flask
- Templates: Jinja2
- Driver de banco: psycopg2-binary
- Variáveis de ambiente: python-dotenv
- Front-end: HTML + CSS próprio + ícones SVG inline
- Banco de dados: PostgreSQL

## Banco de dados

### SGBD
O projeto foi pensado para funcionar com PostgreSQL local, versão 13 ou superior. A aplicação se conecta ao banco por meio da variável `DATABASE_URL`.

### Principais tabelas
- `clientes` — id, nome, email, telefone, criado_em
- `produtos` — id, nome, preco, estoque
- `vendas` — id, id_cliente, data_venda, desconto_percentual
- `itens_venda` — id, id_venda, id_produto, quantidade, preco_unitario

Essas tabelas possuem chaves primárias, chaves estrangeiras e checks para garantir integridade, como:
- preço maior ou igual a zero;
- estoque maior ou igual a zero;
- quantidade maior que zero;
- desconto entre 0 e 100.

### Recursos criados no banco

| Recurso | Nome | Finalidade | Uso na aplicação |
|---|---|---|---|
| View | `vw_relatorio_vendas` | Junta informações de vendas, clientes e itens para gerar um resumo por venda | Relatório de vendas |
| Function | `fn_total_venda(p_id_venda)` | Soma os itens da venda e aplica o percentual de desconto, retornando o total final | Detalhe da venda |
| Procedure | `sp_realizar_venda(p_id_cliente, p_itens jsonb, p_desconto)` | Realiza a venda em uma única transação, validando cliente, estoque e itens antes da confirmação da operação | Cadastro de venda |

## Estrutura do repositório
```text
projeto-vendas-bd/
├── src/
│   ├── app.py
│   ├── db.py
│   ├── templates/
│   └── static/
├── database/
│   ├── 00_criar_banco.sql
│   ├── tables/
│   │   └── 01_criar_tabelas.sql
│   ├── views/
│   │   └── 02_vw_relatorio_vendas.sql
│   ├── functions/
│   │   └── 03_fn_total_venda.sql
│   ├── procedures/
│   │   └── 04_sp_realizar_venda.sql
│   └── inserts/
│       └── 05_dados_exemplo.sql
├── docs/
│   └── roteiro_video.md
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
└── .venv/
```

## Como executar o projeto

### 1. Instalar o PostgreSQL
- Windows: baixe o instalador em https://www.postgresql.org/download/windows/
- Linux (Debian/Ubuntu): `sudo apt install postgresql`
- macOS (Homebrew): `brew install postgresql && brew services start postgresql`

Depois, confirme que o serviço está funcionando:
```bash
psql -U postgres -c "SELECT version();"
```

### 2. Criar o banco `mercado_pro`
No terminal ou no pgAdmin, rode:
```bash
psql -U postgres -c "CREATE DATABASE mercado_pro;"
```

Se preferir, também é possível executar o script `database/00_criar_banco.sql` conectado como `postgres`.

### 3. Rodar os scripts SQL na ordem correta
Conecte-se ao banco recém-criado e execute os arquivos abaixo, na sequência:
```bash
psql -U postgres -d mercado_pro -f database/tables/01_criar_tabelas.sql
psql -U postgres -d mercado_pro -f database/views/02_vw_relatorio_vendas.sql
psql -U postgres -d mercado_pro -f database/functions/03_fn_total_venda.sql
psql -U postgres -d mercado_pro -f database/procedures/04_sp_realizar_venda.sql
psql -U postgres -d mercado_pro -f database/inserts/05_dados_exemplo.sql
```

Se achar mais prático, abra o pgAdmin, selecione o banco `mercado_pro`, use o Query Tool e execute os arquivos um por um, nessa mesma ordem.

### 4. Configurar o arquivo `.env`
Copie o arquivo `.env.example` para `.env` e edite a variável:
```env
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/mercado_pro
```

Substitua `SUA_SENHA` pela senha do usuário `postgres` definida durante a instalação.

### 5. Instalar dependências e iniciar a aplicação
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

# Opcional: testar a conexão com o banco e verificar os objetos criados
python src/testar_conexao.py

python src/app.py
```

Depois, abra no navegador:
```text
http://127.0.0.1:5000
```

## Dicas de solução de problemas
- `password authentication failed` — a senha do PostgreSQL no arquivo `.env` está incorreta.
- `could not connect to server` — o serviço do PostgreSQL não está ativo. No Windows, inicie o serviço pelo gerenciador de serviços.
- `database "mercado_pro" does not exist` — o banco ainda não foi criado ou você está acessando o banco errado.
- `relation "clientes" does not exist` — os scripts SQL não foram executados no banco correto.
- Caracteres estranhos, como `cafÃ©`, indicam problema de encoding. Nesse caso, recrie o banco com UTF-8:
```bash
CREATE DATABASE mercado_pro ENCODING 'UTF8' TEMPLATE template0;
```

## Vídeo
Link do vídeo: [https://youtu.be/ihbQ2Qbo51Y?feature=shared]

## Observação
Este projeto foi desenvolvido como parte de uma atividade acadêmica e tem como objetivo demonstrar, de forma prática, conceitos de modelagem de dados, SQL e integração entre um banco relacional e uma aplicação web.
