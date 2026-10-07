# Roteiro do vídeo (8 a 10 minutos)

> Objetivo: mostrar que o banco **processa dados**, usando de verdade
> 1 View, 1 Function e 1 Procedure, cada uma com finalidade diferente.

---

## 1. Apresentação do sistema (~1 min)
- Nome, disciplina, professor.
- Tema: sistema de vendas simples (clientes, produtos, vendas).
- Stack: Python + Flask + PostgreSQL (local) + psycopg2 (sem ORM).
- Mostrar a estrutura do repositório rapidamente.

## 2. Demonstração das telas (~1 min 30 s)
- Abrir a aplicação no navegador.
- Passar por: **Clientes**, **Produtos**, **Nova venda**,
  **Relatório de vendas**, **Detalhe da venda**.
- Explicar que três dessas telas usam diretamente um recurso do banco
  (há um aviso no rodapé de cada uma).

## 3. VIEW `vw_relatorio_vendas` (~1 min 30 s)
- Abrir `database/views/02_vw_relatorio_vendas.sql` e mostrar o código.
- Explicar:
  - **Motivo:** evitar escrever o mesmo JOIN e agregação em vários lugares;
    o banco já entrega o relatório pronto.
  - **Tabelas envolvidas:** `vendas`, `clientes`, `itens_venda`.
  - **Retorno:** id, data, nome do cliente, qtd. de itens, subtotal.
- Mostrar a tela **Relatório de vendas** consumindo a view (um
  `SELECT * FROM vw_relatorio_vendas`).

## 4. FUNCTION `fn_total_venda(p_id_venda)` (~1 min 30 s)
- Abrir `database/functions/03_fn_total_venda.sql`.
- Explicar:
  - **O que faz:** soma `quantidade * preco_unitario` dos itens e aplica
    o desconto percentual da venda.
  - **Parâmetro:** `p_id_venda INTEGER`.
  - **Retorno:** `NUMERIC` (total final com desconto).
  - **Onde é usada:** tela **Detalhe da venda** — a aplicação executa
    `SELECT fn_total_venda(%s)`.
- Mostrar o detalhe de uma venda e indicar o campo "Total final".

## 5. PROCEDURE `sp_realizar_venda` (~2 min)
- Abrir `database/procedures/04_sp_realizar_venda.sql`.
- Explicar:
  - **O que faz:** registra uma venda em **uma única transação** —
    valida cliente, valida estoque, insere `vendas`, insere `itens_venda`
    com o preço atual do produto e baixa o estoque.
  - **Parâmetros:** id do cliente, itens em `JSONB`, desconto.
  - **Erros:** `RAISE EXCEPTION` com mensagem em português quando o
    cliente não existe ou falta estoque. O commit/rollback é feito pela
    aplicação (psycopg2).
  - **Tela que chama:** **Nova venda**, com `CALL sp_realizar_venda(...)`.
- Fazer uma venda válida ao vivo e, em seguida, **provocar um erro**
  (quantidade acima do estoque) para mostrar a mensagem amigável e o
  rollback.

## 6. Fluxo integrado (~1 min)
- Resumir o caminho de ponta a ponta:
  1. **Tela** envia dados do formulário.
  2. Aplicação chama a **View/Function/Procedure** no banco.
  3. O **banco processa** (agrega, calcula ou executa a transação).
  4. O **resultado volta** e é exibido na tela.
- Conclusão: o banco não é só armazenamento — ele participa ativamente
  da lógica do sistema.
