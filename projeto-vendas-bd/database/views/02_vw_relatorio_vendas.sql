-- =====================================================
-- 02_vw_relatorio_vendas.sql
-- VIEW usada na tela "Relatório de vendas".
-- Junta vendas + clientes + itens_venda e retorna, por venda:
-- id, data, nome do cliente, quantidade de itens e subtotal (sem desconto).
-- =====================================================

CREATE OR REPLACE VIEW vw_relatorio_vendas AS
SELECT
    v.id                                 AS id_venda,
    v.data_venda                         AS data_venda,
    c.nome                               AS nome_cliente,
    COALESCE(SUM(i.quantidade), 0)       AS quantidade_itens,
    COALESCE(SUM(i.quantidade * i.preco_unitario), 0) AS subtotal
FROM vendas v
JOIN clientes c         ON c.id = v.id_cliente
LEFT JOIN itens_venda i ON i.id_venda = v.id
GROUP BY v.id, v.data_venda, c.nome
ORDER BY v.data_venda DESC;
