-- =====================================================
-- 05_dados_exemplo.sql
-- Popula o banco com dados de exemplo:
--   - 5 clientes
--   - 10 produtos
--   - 3 vendas criadas pela PROCEDURE sp_realizar_venda
-- =====================================================

-- Clientes
INSERT INTO clientes (nome, email, telefone) VALUES
    ('Ana Souza',       'ana.souza@email.com',       '11988880001'),
    ('Bruno Lima',      'bruno.lima@email.com',      '11988880002'),
    ('Carla Mendes',    'carla.mendes@email.com',    '11988880003'),
    ('Diego Rocha',     'diego.rocha@email.com',     '11988880004'),
    ('Eduarda Alves',   'eduarda.alves@email.com',   '11988880005')
ON CONFLICT (email) DO NOTHING;

-- Produtos
INSERT INTO produtos (nome, preco, estoque) VALUES
    ('Caneta Azul',           3.50,  100),
    ('Caderno 100 folhas',   18.90,   50),
    ('Mochila Escolar',     129.90,   20),
    ('Lápis HB',              1.20,  200),
    ('Borracha Branca',       2.00,  150),
    ('Estojo Simples',       25.00,   40),
    ('Régua 30cm',            6.75,   80),
    ('Marcador de Texto',     8.50,   60),
    ('Agenda 2026',          34.90,   30),
    ('Cola Bastão',           5.40,   90);

-- Vendas criadas via PROCEDURE (demonstra o uso real da procedure)
DO $$
BEGIN
    -- Venda 1: Ana compra 2 canetas e 1 caderno, 5% de desconto
    CALL sp_realizar_venda(
        1,
        '[{"id_produto": 1, "quantidade": 2}, {"id_produto": 2, "quantidade": 1}]'::jsonb,
        5
    );

    -- Venda 2: Bruno compra 1 mochila e 1 estojo, 10% de desconto
    CALL sp_realizar_venda(
        2,
        '[{"id_produto": 3, "quantidade": 1}, {"id_produto": 6, "quantidade": 1}]'::jsonb,
        10
    );

    -- Venda 3: Carla compra 3 lápis, 2 borrachas e 1 agenda, sem desconto
    CALL sp_realizar_venda(
        3,
        '[{"id_produto": 4, "quantidade": 3}, {"id_produto": 5, "quantidade": 2}, {"id_produto": 9, "quantidade": 1}]'::jsonb,
        0
    );
END $$;
