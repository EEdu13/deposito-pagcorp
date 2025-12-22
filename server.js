const express = require('express');
const sql = require('mssql');
const path = require('path');

const app = express();
const port = 3002;

// Configuração da conexão com SQL Server
const config = {
    server: 'alrflorestal.database.windows.net',
    database: 'Tabela_teste',
    user: 'sqladmin',
    password: 'SenhaForte123!',
    options: {
        encrypt: true, // Para Azure SQL
        trustServerCertificate: false
    }
};

// Middleware para CORS
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
});

// Middleware para servir arquivos estáticos
app.use(express.static(path.join(__dirname)));

// Rota para servir o HTML
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// Rota para buscar dados da tabela PEDIDOS
app.get('/api/pedidos', async (req, res) => {
    console.log('🔍 Recebida requisição para /api/pedidos');
    
    try {
        console.log('🔌 Tentando conectar ao SQL Server...');
        console.log('📍 Servidor:', config.server);
        console.log('🗃️ Banco:', config.database);
        
        // Conectar ao banco
        await sql.connect(config);
        console.log('✅ Conectado ao banco com sucesso!');
        
        // Executar query
        console.log('📊 Executando query: SELECT * FROM PEDIDOS');
        const result = await sql.query('SELECT * FROM PEDIDOS');
        console.log('✅ Query executada com sucesso!');
        console.log('📈 Registros encontrados:', result.recordset.length);
        
        res.json({
            success: true,
            data: result.recordset,
            message: 'Dados carregados com sucesso!'
        });
        
    } catch (error) {
        console.error('❌ Erro ao buscar dados:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            message: 'Erro ao conectar com o banco de dados'
        });
    } finally {
        // Fechar conexão
        try {
            await sql.close();
            console.log('🔌 Conexão fechada');
        } catch (closeError) {
            console.error('Erro ao fechar conexão:', closeError);
        }
    }
});

// Iniciar servidor
app.listen(port, () => {
    console.log(`Servidor rodando em http://localhost:${port}`);
    console.log('Pressione Ctrl+C para parar o servidor');
});

// Tratamento de erros não capturados
process.on('uncaughtException', (err) => {
    console.error('Erro não capturado:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Promise rejeitada não tratada:', reason);
});
