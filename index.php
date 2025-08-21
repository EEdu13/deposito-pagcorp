<?php
// Configurações de conexão
$serverName = "alrflorestal.database.windows.net";
$connectionOptions = array(
    "Database" => "Tabela_teste",
    "Uid" => "sqladmin",
    "PWD" => "SenhaForte123!",
    "CharacterSet" => "UTF-8"
);

try {
    
    // Conectar ao SQL Server
    $conn = sqlsrv_connect($serverName, $connectionOptions);
    
    if ($conn === false) {
        throw new Exception("Erro na conexão: " . print_r(sqlsrv_errors(), true));
    }
    
    // Query para buscar todos os dados da tabela PEDIDOS
    $sql = "SELECT * FROM PEDIDOS";
    $stmt = sqlsrv_query($conn, $sql);
    
    if ($stmt === false) {
        throw new Exception("Erro na consulta: " . print_r(sqlsrv_errors(), true));
    }
    
} catch (Exception $e) {
    $error = $e->getMessage();
}
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dados da Tabela PEDIDOS</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        
        tr:hover {
            background-color: #e8f5e8;
        }
        
        .error {
            color: #d32f2f;
            background-color: #ffebee;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #d32f2f;
            margin-bottom: 20px;
        }
        
        .info {
            color: #1976d2;
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #1976d2;
            margin-bottom: 20px;
        }
        
        .no-data {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Dados da Tabela PEDIDOS</h1>
        
        <?php if (isset($error)): ?>
            <div class="error">
                <strong>Erro:</strong> <?php echo htmlspecialchars($error); ?>
            </div>
        <?php else: ?>
            
            <?php if (isset($stmt) && $stmt): ?>
                <div class="info">
                    <strong>Conexão estabelecida com sucesso!</strong> Exibindo dados da tabela PEDIDOS.
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <?php
                            // Obter nomes das colunas
                            $fieldNames = array();
                            foreach (sqlsrv_field_metadata($stmt) as $fieldMetadata) {
                                $fieldNames[] = $fieldMetadata['Name'];
                                echo "<th>" . htmlspecialchars($fieldMetadata['Name']) . "</th>";
                            }
                            ?>
                        </tr>
                    </thead>
                    <tbody>
                        <?php
                        $hasData = false;
                        while ($row = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC)) {
                            $hasData = true;
                            echo "<tr>";
                            foreach ($fieldNames as $fieldName) {
                                $value = $row[$fieldName];
                                
                                // Formatação especial para diferentes tipos de dados
                                if ($value instanceof DateTime) {
                                    $value = $value->format('d/m/Y H:i:s');
                                } elseif (is_null($value)) {
                                    $value = '<em>NULL</em>';
                                }
                                
                                echo "<td>" . htmlspecialchars($value) . "</td>";
                            }
                            echo "</tr>";
                        }
                        
                        if (!$hasData) {
                            echo "<tr><td colspan='" . count($fieldNames) . "' class='no-data'>Nenhum dado encontrado na tabela PEDIDOS</td></tr>";
                        }
                        ?>
                    </tbody>
                </table>
                
                <?php
                // Fechar conexão
                sqlsrv_free_stmt($stmt);
                sqlsrv_close($conn);
                ?>
                
            <?php endif; ?>
        <?php endif; ?>
    </div>
</body>
</html>
