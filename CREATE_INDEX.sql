-- ========================================================
-- SCRIPT DE OTIMIZAÇÃO DE ÍNDICES - DEPOSITO PAGCORP
-- ========================================================
-- Execute este script no banco de dados para criar índices
-- que melhoram a performance das queries
-- ========================================================

-- Índice principal para filtro de data + status depositado
CREATE NONCLUSTERED INDEX IX_PEDIDOS_DATA_DEPOSITADO 
ON PEDIDOS(DATA_ENVIO1 DESC, DEPOSITADO)
INCLUDE (
    RESPONSAVEL_PELO_CARTAO,
    PAGCORP,
    TOTAL_PAGAR,
    FECHAMENTO,
    APROVADO_POR,
    PROJETO,
    OBSERVACOES
);

-- Índice para UPDATE otimizado (busca por chaves compostas)
CREATE NONCLUSTERED INDEX IX_PEDIDOS_DEPOSITAR
ON PEDIDOS(RESPONSAVEL_PELO_CARTAO, PAGCORP, TOTAL_PAGAR)
INCLUDE (DEPOSITADO);

-- Verificar índices criados
SELECT 
    i.name AS IndexName,
    OBJECT_NAME(i.object_id) AS TableName,
    i.type_desc AS IndexType,
    COL_NAME(ic.object_id, ic.column_id) AS ColumnName
FROM sys.indexes i
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
WHERE OBJECT_NAME(i.object_id) = 'PEDIDOS'
AND i.name LIKE 'IX_PEDIDOS_%'
ORDER BY i.name, ic.key_ordinal;

-- ========================================================
-- IMPORTANTE: Após criar os índices, execute:
-- ========================================================
-- UPDATE STATISTICS PEDIDOS WITH FULLSCAN;
-- ========================================================
