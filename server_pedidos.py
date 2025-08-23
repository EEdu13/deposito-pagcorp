#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string, request
import pymssql
import json
import decimal
from datetime import datetime

app = Flask(__name__)

# Função para serializar Decimal e datetime em JSON
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    return str(obj)

# Configuração do Azure SQL (suas credenciais)
AZURE_CONFIG = {
    'server': 'alrflorestal.database.windows.net',
    'database': 'Tabela_teste',
    'user': 'sqladmin',
    'password': 'SenhaForte123!'
}

def conectar_azure_sql():
    """Conecta ao Azure SQL Server"""
    try:
        conn = pymssql.connect(
            server=AZURE_CONFIG['server'],
            database=AZURE_CONFIG['database'],
            user=AZURE_CONFIG['user'],
            password=AZURE_CONFIG['password']
        )
        print(f"✅ Conectado ao Azure SQL: {AZURE_CONFIG['server']}")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar no Azure SQL: {e}")
        return None

@app.route('/')
def index():
    """Página principal com dashboard integrado"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/dashboard-pedidos-real.html')
def dashboard_real():
    """Dashboard com dados reais"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/pedidos')
def get_pedidos():
    """API para buscar dados da tabela PEDIDOS"""
    try:
        print("🔍 Recebida requisição para /api/pedidos")
        
        conn = conectar_azure_sql()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Não foi possível conectar ao banco de dados',
                'data': []
            }), 500
        
        cursor = conn.cursor()
        print("📊 Executando query: SELECT * FROM PEDIDOS")
        
        cursor.execute("SELECT * FROM PEDIDOS")
        
        # Obter nomes das colunas
        columns = [desc[0] for desc in cursor.description]
        print(f"📋 Colunas encontradas: {columns}")
        
        # Buscar todos os dados
        rows = cursor.fetchall()
        print(f"📈 Registros encontrados: {len(rows)}")
        
        # Converter para lista de dicionários
        data = []
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                row_dict[columns[i]] = value
            data.append(row_dict)
        
        cursor.close()
        conn.close()
        print("🔌 Conexão fechada")
        
        return jsonify({
            'success': True,
            'data': data,
            'message': f'Dados carregados com sucesso! {len(data)} registros encontrados.',
            'columns': columns
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

# Template HTML que funciona com dados reais
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard PEDIDOS - Dados REAIS</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .app-container {
            max-width: 100%;
            margin: 0 auto;
            background: #fff;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }

        .header {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .header-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: center;
        }

        .header-btn {
            padding: 0.5rem 0.75rem;
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            color: white;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .header-btn:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-1px);
        }

        .summary-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
            padding: 1rem;
            background: #f8fafc;
        }

        .stat-card {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .stat-value {
            font-size: 1.25rem;
            font-weight: 700;
            color: #1f2937;
        }

        .stat-label {
            font-size: 0.8rem;
            color: #6b7280;
            margin-top: 0.25rem;
        }

        .payments-container {
            padding: 1rem;
            max-height: 60vh;
            overflow-y: auto;
        }

        .payment-card {
            background: white;
            border-radius: 16px;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .payment-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .payment-header {
            padding: 1rem;
            cursor: pointer;
            position: relative;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .payment-main-content {
            flex: 1;
        }

        .payment-header::after {
            content: '▼';
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            transition: transform 0.3s ease;
            color: #6b7280;
            pointer-events: none;
            font-size: 12px;
        }

        .payment-card.expanded .payment-header::after {
            transform: translateY(-50%) rotate(180deg);
        }

        .payment-main-info {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 1rem;
            align-items: center;
        }

        .payment-title {
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 0.25rem;
        }

        .payment-subtitle {
            font-size: 0.85rem;
            color: #6b7280;
        }

        .payment-amount {
            text-align: right;
        }

        .amount-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: #059669;
        }

        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-top: 0.25rem;
            background: #d1fae5;
            color: #065f46;
        }

        .payment-details {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }

        .payment-card.expanded .payment-details {
            max-height: 500px;
        }

        .payment-details-content {
            padding: 0 1rem 1rem;
            border-top: 1px solid #f3f4f6;
            margin-top: 1rem;
            padding-top: 1rem;
        }

        .detail-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            padding: 0.5rem 0;
        }

        .detail-label {
            font-weight: 500;
            color: #6b7280;
        }

        .detail-value {
            font-weight: 600;
            color: #1f2937;
            text-align: right;
            flex: 1;
            margin-left: 1rem;
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: #6b7280;
        }

        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: #6b7280;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #2563eb;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Responsive adjustments */
        @media (min-width: 768px) {
            .app-container {
                max-width: 420px;
                margin: 0 auto;
                border-radius: 20px;
                overflow: hidden;
                margin-top: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <header class="header">
            <h1>📊 Dashboard PEDIDOS</h1>
            <div class="header-actions">
                <button class="header-btn" onclick="limparCache()">🔄 Limpar Cache</button>
                <button class="header-btn" onclick="atualizarDados()">📊 Carregar Dados Reais</button>
            </div>
        </header>

        <section class="summary-stats">
            <div class="stat-card">
                <div class="stat-value" id="totalCount">0</div>
                <div class="stat-label">Total de Pedidos</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalAmount">R$ 0,00</div>
                <div class="stat-label">Valor Total</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalColumns">0</div>
                <div class="stat-label">Total de Colunas</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="statusConnection">🔄</div>
                <div class="stat-label">Status Conexão</div>
            </div>
        </section>

        <section class="payments-container" id="paymentsContainer">
            <div class="loading">
                <div class="spinner"></div>
                <p>🔄 Clique em "Carregar Dados Reais" para ver seus pedidos...</p>
            </div>
        </section>
    </div>

    <script>
        let dadosReais = [];
        let colunas = [];

        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {
            mostrarMensagemInicial();
        });

        function mostrarMensagemInicial() {
            const container = document.getElementById('paymentsContainer');
            container.innerHTML = `
                <div class="loading">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🚀</div>
                    <h3>Dashboard PEDIDOS - Dados Reais</h3>
                    <p style="margin: 1rem 0;">Conectado ao Azure SQL Server</p>
                    <p style="color: #059669; font-weight: 600;">✅ Banco: Tabela_teste</p>
                    <p style="color: #059669; font-weight: 600;">✅ Tabela: PEDIDOS</p>
                    <br>
                    <p>👆 Clique em <strong>"📊 Carregar Dados Reais"</strong> para ver seus pedidos!</p>
                </div>
            `;
        }

        async function atualizarDados() {
            try {
                document.getElementById('statusConnection').textContent = '🔄';
                showNotification('🔄 Conectando ao Azure SQL Server...', 'info');
                
                const container = document.getElementById('paymentsContainer');
                container.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>🔌 Conectando ao banco de dados...</p>
                        <p style="color: #666; font-size: 0.9rem;">Server: alrflorestal.database.windows.net</p>
                        <p style="color: #666; font-size: 0.9rem;">Database: Tabela_teste</p>
                    </div>
                `;

                // Fazer requisição para a API Python
                const response = await fetch('/api/pedidos');
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const resultado = await response.json();
                console.log('📊 Dados recebidos:', resultado);

                if (resultado.success && resultado.data) {
                    dadosReais = resultado.data;
                    colunas = resultado.columns || (dadosReais.length > 0 ? Object.keys(dadosReais[0]) : []);
                    
                    renderizarPedidos();
                    atualizarEstatisticas();
                    
                    document.getElementById('statusConnection').textContent = '✅';
                    showNotification(`🎉 ${dadosReais.length} pedidos carregados com sucesso!`, 'success');
                    
                } else {
                    throw new Error(resultado.error || 'Erro desconhecido');
                }

            } catch (error) {
                console.error('❌ Erro:', error);
                document.getElementById('statusConnection').textContent = '❌';
                
                const container = document.getElementById('paymentsContainer');
                container.innerHTML = `
                    <div class="empty-state">
                        <div style="font-size: 3rem; margin-bottom: 1rem; color: #ef4444;">❌</div>
                        <h3>Erro de Conexão</h3>
                        <p>${error.message}</p>
                        <br>
                        <p style="color: #666; font-size: 0.9rem;">Verifique se o servidor Python está rodando!</p>
                    </div>
                `;
                
                showNotification(`❌ Erro: ${error.message}`, 'error');
            }
        }

        function renderizarPedidos() {
            const container = document.getElementById('paymentsContainer');
            
            if (!dadosReais || dadosReais.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <h3>Nenhum pedido encontrado</h3>
                        <p>A tabela PEDIDOS está vazia ou sem dados</p>
                    </div>
                `;
                return;
            }

            const html = dadosReais.map((pedido, index) => {
                // Tentar identificar campos principais
                const id = pedido.ID || pedido.id || pedido.Id || index + 1;
                const titulo = pedido.PROJETO || pedido.projeto || pedido.NOME || pedido.nome || `Pedido #${id}`;
                const subtitulo = pedido.FAZENDA || pedido.fazenda || pedido.CIDADE_PRESTACAO_DO_SERVICO || 'Sem descrição';
                
                // Tentar encontrar valor monetário
                let valor = 0;
                if (pedido.VALOR_PAGO) valor = parseFloat(pedido.VALOR_PAGO) || 0;
                else if (pedido.TOTAL_PAGAR) valor = parseFloat(pedido.TOTAL_PAGAR) || 0;
                else if (pedido.VALOR_DIARIA) valor = parseFloat(pedido.VALOR_DIARIA) || 0;

                return `
                    <div class="payment-card" data-id="${id}">
                        <div class="payment-header" onclick="togglePaymentDetails(${index})">
                            <div class="payment-main-content">
                                <div class="payment-main-info">
                                    <div>
                                        <div class="payment-title">${titulo}</div>
                                        <div class="payment-subtitle">${subtitulo}</div>
                                    </div>
                                    <div class="payment-amount">
                                        <div class="amount-value">${valor > 0 ? `R$ ${valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})}` : 'Sem valor'}</div>
                                        <div class="status-badge">PEDIDO</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="payment-details">
                            <div class="payment-details-content">
                                ${colunas.map(coluna => {
                                    let valorColuna = pedido[coluna];
                                    
                                    // Formatação de valores
                                    if (valorColuna === null || valorColuna === undefined) {
                                        valorColuna = '<em style="color: #999;">NULL</em>';
                                    } else if (typeof valorColuna === 'string' && valorColuna.includes('T')) {
                                        try {
                                            const data = new Date(valorColuna);
                                            if (!isNaN(data.getTime())) {
                                                valorColuna = data.toLocaleString('pt-BR');
                                            }
                                        } catch (e) {
                                            // Manter valor original
                                        }
                                    } else if (typeof valorColuna === 'number' && coluna.toLowerCase().includes('valor')) {
                                        valorColuna = `R$ ${valorColuna.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
                                    }
                                    
                                    return `
                                        <div class="detail-row">
                                            <span class="detail-label">${coluna}:</span>
                                            <span class="detail-value">${valorColuna}</span>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = html;
        }

        function togglePaymentDetails(index) {
            const cards = document.querySelectorAll('.payment-card');
            if (cards[index]) {
                cards[index].classList.toggle('expanded');
            }
        }

        function atualizarEstatisticas() {
            const totalCount = dadosReais.length;
            const totalColumns = colunas.length;
            
            // Calcular valor total
            let totalAmount = 0;
            dadosReais.forEach(pedido => {
                if (pedido.VALOR_PAGO) totalAmount += parseFloat(pedido.VALOR_PAGO) || 0;
                else if (pedido.TOTAL_PAGAR) totalAmount += parseFloat(pedido.TOTAL_PAGAR) || 0;
                else if (pedido.VALOR_DIARIA) totalAmount += parseFloat(pedido.VALOR_DIARIA) || 0;
            });

            document.getElementById('totalCount').textContent = totalCount;
            document.getElementById('totalColumns').textContent = totalColumns;
            document.getElementById('totalAmount').textContent = `R$ ${totalAmount.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
        }

        function limparCache() {
            dadosReais = [];
            colunas = [];
            document.getElementById('statusConnection').textContent = '🔄';
            mostrarMensagemInicial();
            
            // Reset estatísticas
            document.getElementById('totalCount').textContent = '0';
            document.getElementById('totalColumns').textContent = '0';
            document.getElementById('totalAmount').textContent = 'R$ 0,00';
            
            showNotification('🗑️ Cache limpo!', 'success');
        }

        // Função para mostrar notificações
        function showNotification(message, type = 'info') {
            // Remover notificação anterior se existir
            const existingNotification = document.querySelector('.notification');
            if (existingNotification) {
                existingNotification.remove();
            }

            // Criar nova notificação
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.innerHTML = message;
            
            // Estilos da notificação
            Object.assign(notification.style, {
                position: 'fixed',
                top: '20px',
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6',
                color: 'white',
                padding: '1rem 1.5rem',
                borderRadius: '12px',
                boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
                zIndex: '9999',
                fontSize: '0.9rem',
                fontWeight: '500',
                maxWidth: '90vw',
                textAlign: 'center',
                animation: 'slideDown 0.3s ease-out'
            });

            document.body.appendChild(notification);

            // Remover após 4 segundos
            setTimeout(() => {
                notification.style.animation = 'slideUp 0.3s ease-out';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }, 4000);
        }

        // Animações para notificações
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideDown {
                from {
                    transform: translateX(-50%) translateY(-100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(-50%) translateY(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideUp {
                from {
                    transform: translateX(-50%) translateY(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(-50%) translateY(-100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard PEDIDOS - Python Flask</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .controls {
            padding: 30px;
            text-align: center;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        
        .btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            margin: 0 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            background: #cccccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: #f8f9fa;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin: 10px;
            flex: 1;
            min-width: 200px;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #666;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .content {
            padding: 30px;
        }
        
        .message {
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-weight: bold;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.3em;
            color: #666;
        }
        
        .table-container {
            overflow-x: auto;
            max-height: 600px;
            overflow-y: auto;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        
        th {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 10;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }
        
        tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        tr:hover {
            background: #e8f5e8;
            transition: background 0.3s ease;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Dashboard PEDIDOS</h1>
            <p>Sistema de Visualização de Dados - Python Flask + Azure SQL</p>
        </div>
        
        <div class="controls">
            <button class="btn" id="loadBtn" onclick="carregarDados()">
                📊 CARREGAR DADOS REAIS
            </button>
            <button class="btn" id="refreshBtn" onclick="atualizarDados()">
                🔄 ATUALIZAR
            </button>
        </div>
        
        <div id="statsContainer"></div>
        <div class="content">
            <div id="messageArea"></div>
            <div id="tableContainer"></div>
        </div>
        
        <div class="footer">
            <p>🎯 Sistema desenvolvido com Python Flask + Azure SQL Server</p>
        </div>
    </div>

    <script>
        let dadosAtuais = [];

        function mostrarMensagem(mensagem, tipo = 'success') {
            const messageArea = document.getElementById('messageArea');
            messageArea.innerHTML = `<div class="message ${tipo}">${mensagem}</div>`;
        }

        function mostrarCarregando() {
            const tableContainer = document.getElementById('tableContainer');
            tableContainer.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>🔄 Carregando dados REAIS da tabela PEDIDOS...</p>
                </div>
            `;
        }

        function criarEstatisticas(dados) {
            if (!dados || dados.length === 0) {
                document.getElementById('statsContainer').innerHTML = '';
                return;
            }

            const totalRegistros = dados.length;
            const colunas = Object.keys(dados[0]);
            
            const statsHTML = `
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">${totalRegistros}</div>
                        <div class="stat-label">Total de Registros</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${colunas.length}</div>
                        <div class="stat-label">Total de Colunas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">✅</div>
                        <div class="stat-label">Status: Online</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">🐍</div>
                        <div class="stat-label">Python Flask</div>
                    </div>
                </div>
            `;
            
            document.getElementById('statsContainer').innerHTML = statsHTML;
        }

        async function carregarDados() {
            console.log('🚀 Iniciando carregamento de dados REAIS...');
            
            const loadBtn = document.getElementById('loadBtn');
            const refreshBtn = document.getElementById('refreshBtn');
            
            loadBtn.disabled = true;
            refreshBtn.disabled = true;
            loadBtn.textContent = '⏳ Carregando...';
            
            mostrarCarregando();
            mostrarMensagem('🔌 Conectando ao Azure SQL Server...', 'success');

            try {
                console.log('📡 Fazendo requisição para /api/pedidos');
                
                const response = await fetch('/api/pedidos');
                console.log('📡 Resposta recebida:', response);
                
                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status} - ${response.statusText}`);
                }
                
                const dados = await response.json();
                console.log('✅ Dados recebidos:', dados);

                if (dados.success && dados.data) {
                    dadosAtuais = dados.data;
                    console.log(`📊 Total de registros: ${dadosAtuais.length}`);
                    
                    criarTabela(dadosAtuais);
                    criarEstatisticas(dadosAtuais);
                    mostrarMensagem(`🎉 SUCESSO! ${dadosAtuais.length} registros REAIS carregados da tabela PEDIDOS!`, 'success');
                } else {
                    throw new Error(dados.error || 'Erro desconhecido');
                }

            } catch (error) {
                console.error('❌ Erro:', error);
                mostrarMensagem(`❌ ERRO: ${error.message}`, 'error');
                document.getElementById('tableContainer').innerHTML = '';
                document.getElementById('statsContainer').innerHTML = '';
            } finally {
                loadBtn.disabled = false;
                refreshBtn.disabled = false;
                loadBtn.textContent = '📊 CARREGAR DADOS REAIS';
            }
        }

        function atualizarDados() {
            carregarDados();
        }

        function criarTabela(dados) {
            if (!dados || dados.length === 0) {
                document.getElementById('tableContainer').innerHTML = '<div class="loading">❌ Nenhum dado encontrado</div>';
                return;
            }

            const colunas = Object.keys(dados[0]);
            let tabelaHTML = '<div class="table-container"><table><thead><tr>';
            
            colunas.forEach(coluna => {
                tabelaHTML += `<th>${coluna}</th>`;
            });
            
            tabelaHTML += '</tr></thead><tbody>';

            dados.forEach((linha, index) => {
                tabelaHTML += '<tr>';
                colunas.forEach(coluna => {
                    let valor = linha[coluna];
                    
                    if (valor === null || valor === undefined) {
                        valor = '<em style="color: #999;">NULL</em>';
                    } else if (typeof valor === 'string' && valor.includes('T') && valor.includes(':')) {
                        try {
                            const data = new Date(valor);
                            if (!isNaN(data.getTime())) {
                                valor = data.toLocaleString('pt-BR');
                            }
                        } catch (e) {
                            // Manter valor original
                        }
                    } else if (typeof valor === 'number' && coluna.toLowerCase().includes('valor')) {
                        valor = `R$ ${valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
                    }
                    
                    tabelaHTML += `<td>${valor}</td>`;
                });
                tabelaHTML += '</tr>';
            });

            tabelaHTML += '</tbody></table></div>';
            
            document.getElementById('tableContainer').innerHTML = tabelaHTML;
        }

        // Carregar dados automaticamente ao abrir a página
        window.addEventListener('load', function() {
            mostrarMensagem('🎯 Dashboard carregado! Clique em "CARREGAR DADOS REAIS" para ver sua tabela PEDIDOS.', 'success');
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🐍 Iniciando servidor Python Flask...")
    print("🌐 Acesse: http://localhost:5000")
    print("📊 API: http://localhost:5000/api/pedidos")
    app.run(debug=True, host='0.0.0.0', port=5000)
