-- =====================================================
-- 04_sp_realizar_venda.sql
-- PROCEDURE usada na tela "Nova venda" (via CALL).
-- Em uma única transação:
--   1. Valida se o cliente existe
--   2. Valida se há estoque suficiente para cada item
--   3. Insere a venda
--   4. Insere cada item usando o preço atual do produto
--   5. Baixa o estoque
-- Em caso de erro (cliente inexistente, estoque insuficiente),
-- lança RAISE EXCEPTION com mensagem em português.
-- IMPORTANTE: NÃO usa COMMIT dentro da procedure. Quem controla
-- commit/rollback é a aplicação (psycopg2).
--
-- Parâmetro p_itens é um JSONB no formato:
-- [{"id_produto": 1, "quantidade": 2}, {"id_produto": 3, "quantidade": 1}]
-- =====================================================

CREATE OR REPLACE PROCEDURE sp_realizar_venda(
    p_id_cliente INTEGER,
    p_itens      JSONB,
    p_desconto   NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_venda       INTEGER;
    v_item           JSONB;
    v_id_produto     INTEGER;
    v_quantidade     INTEGER;
    v_preco_atual    NUMERIC(10,2);
    v_estoque_atual  INTEGER;
    v_nome_produto   VARCHAR(120);
BEGIN
    -- 1) Valida cliente
    IF NOT EXISTS (SELECT 1 FROM clientes WHERE id = p_id_cliente) THEN
        RAISE EXCEPTION 'Cliente de id % não encontrado.', p_id_cliente;
    END IF;

    -- Valida desconto
    IF p_desconto IS NULL OR p_desconto < 0 OR p_desconto > 100 THEN
        RAISE EXCEPTION 'Desconto inválido (%). Informe um valor entre 0 e 100.', p_desconto;
    END IF;

    -- Valida itens não vazios
    IF p_itens IS NULL OR jsonb_array_length(p_itens) = 0 THEN
        RAISE EXCEPTION 'Nenhum item informado para a venda.';
    END IF;

    -- 2) Valida estoque de cada item antes de qualquer alteração
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_itens)
    LOOP
        v_id_produto := (v_item->>'id_produto')::INTEGER;
        v_quantidade := (v_item->>'quantidade')::INTEGER;

        IF v_quantidade IS NULL OR v_quantidade <= 0 THEN
            RAISE EXCEPTION 'Quantidade inválida para o produto %.', v_id_produto;
        END IF;

        SELECT nome, estoque
        INTO v_nome_produto, v_estoque_atual
        FROM produtos
        WHERE id = v_id_produto;

        IF v_nome_produto IS NULL THEN
            RAISE EXCEPTION 'Produto de id % não encontrado.', v_id_produto;
        END IF;

        IF v_estoque_atual < v_quantidade THEN
            RAISE EXCEPTION 'Estoque insuficiente para o produto "%": disponível %, solicitado %.',
                v_nome_produto, v_estoque_atual, v_quantidade;
        END IF;
    END LOOP;

    -- 3) Insere a venda
    INSERT INTO vendas (id_cliente, desconto_percentual)
    VALUES (p_id_cliente, p_desconto)
    RETURNING id INTO v_id_venda;

    -- 4) Insere itens com o preço atual + 5) baixa o estoque
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_itens)
    LOOP
        v_id_produto := (v_item->>'id_produto')::INTEGER;
        v_quantidade := (v_item->>'quantidade')::INTEGER;

        SELECT preco INTO v_preco_atual
        FROM produtos
        WHERE id = v_id_produto;

        INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario)
        VALUES (v_id_venda, v_id_produto, v_quantidade, v_preco_atual);

        UPDATE produtos
            SET estoque = estoque - v_quantidade
        WHERE id = v_id_produto;
    END LOOP;
END;
$$;
