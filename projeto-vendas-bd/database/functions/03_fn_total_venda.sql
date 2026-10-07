-- =====================================================
-- 03_fn_total_venda.sql
-- FUNCTION usada na tela "Detalhe da venda".
-- Recebe o id da venda, soma (quantidade * preco_unitario) dos itens
-- e aplica o desconto percentual da venda, retornando o total final.
-- =====================================================

CREATE OR REPLACE FUNCTION fn_total_venda(p_id_venda INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    v_subtotal  NUMERIC(12,2);
    v_desconto  NUMERIC(5,2);
BEGIN
    SELECT COALESCE(SUM(i.quantidade * i.preco_unitario), 0)
    INTO v_subtotal
    FROM itens_venda i
    WHERE i.id_venda = p_id_venda;

    SELECT COALESCE(desconto_percentual, 0)
    INTO v_desconto
    FROM vendas
    WHERE id = p_id_venda;

    RETURN ROUND(v_subtotal * (1 - v_desconto / 100.0), 2);
END;
$$ LANGUAGE plpgsql;
