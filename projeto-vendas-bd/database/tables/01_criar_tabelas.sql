-- =====================================================
-- 01_criar_tabelas.sql
-- Cria as tabelas principais do sistema de vendas.
-- Idempotente: pode ser executado várias vezes sem erro.
-- =====================================================

CREATE TABLE IF NOT EXISTS clientes (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(120) NOT NULL,
    email       VARCHAR(120) NOT NULL UNIQUE,
    telefone    VARCHAR(30),
    criado_em   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS produtos (
    id       SERIAL PRIMARY KEY,
    nome     VARCHAR(120) NOT NULL,
    preco    NUMERIC(10,2) NOT NULL CHECK (preco >= 0),
    estoque  INTEGER NOT NULL CHECK (estoque >= 0)
);

CREATE TABLE IF NOT EXISTS vendas (
    id                   SERIAL PRIMARY KEY,
    id_cliente           INTEGER NOT NULL REFERENCES clientes(id),
    data_venda           TIMESTAMP NOT NULL DEFAULT NOW(),
    desconto_percentual  NUMERIC(5,2) NOT NULL DEFAULT 0
        CHECK (desconto_percentual >= 0 AND desconto_percentual <= 100)
);

CREATE TABLE IF NOT EXISTS itens_venda (
    id              SERIAL PRIMARY KEY,
    id_venda        INTEGER NOT NULL REFERENCES vendas(id) ON DELETE CASCADE,
    id_produto      INTEGER NOT NULL REFERENCES produtos(id),
    quantidade      INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario  NUMERIC(10,2) NOT NULL CHECK (preco_unitario >= 0)
);
