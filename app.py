#!/usr/bin/env python3

import os
print("🔄 Iniciando imports...")

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import pymssql
from datetime import datetime

print("✅ Imports OK")

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configurações do banco Azure SQL - usando variáveis de ambiente
SQL_SERVER = os.getenv('SQL_SERVER', 'localhost')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'database')
SQL_USERNAME = os.getenv('SQL_USERNAME', 'user')
SQL_PASSWORD = os.getenv('SQL_PASSWORD', 'password')

print("✅ Configurações carregadas")

def conectar_azure_sql():
    """Conecta ao Azure SQL Server"""
    try:
        print(f"🔌 Conectando ao {SQL_SERVER}...")
        connection = pymssql.connect(
            server=SQL_SERVER,
            user=SQL_USERNAME,
            password=SQL_PASSWORD,
            database=SQL_DATABASE,
            timeout=30,
            login_timeout=30
        )
        print("✅ Conexão estabelecida!")
        return connection
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

@app.route('/favicon.ico')
def favicon():
    """Retorna um favicon vazio para evitar erro 404"""
    return '', 204

@app.route('/health')
def health_check():
    """Health check para Railway"""
    return jsonify({'status': 'healthy', 'service': 'deposito-pagcorp'}), 200

@app.route('/')
def dashboard():
    """Serve o dashboard HTML"""
    print("📄 Servindo dashboard-pedidos-real.html")
    return send_file('dashboard-pedidos-real.html')

@app.route('/api/pedidos')
def get_pedidos():
    """API para buscar dados da tabela PEDIDOS"""
    print("🔍 Buscando dados da tabela PEDIDOS...")
    
    try:
        # Conectar ao banco
        connection = conectar_azure_sql()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Erro de conexão com o banco de dados'
            }), 500

        # Executar query
        cursor = connection.cursor(as_dict=True)
        cursor.execute("SELECT * FROM PEDIDOS")
        
        # Buscar todos os resultados
        dados = cursor.fetchall()
        
        # Processar dados para JSON
        dados_processados = []
        colunas = []
        
        if dados:
            # Pegar nomes das colunas
            colunas = list(dados[0].keys())
            
            # Processar cada linha
            for linha in dados:
                linha_processada = {}
                for coluna, valor in linha.items():
                    # Converter datetime para string
                    if isinstance(valor, datetime):
                        linha_processada[coluna] = valor.isoformat()
                    else:
                        linha_processada[coluna] = valor
                dados_processados.append(linha_processada)
        
        # Fechar conexão
        cursor.close()
        connection.close()
        
        print(f"✅ Consulta executada: {len(dados_processados)} registros")
        
        return jsonify({
            'success': True,
            'data': dados_processados,
            'columns': colunas,
            'count': len(dados_processados)
        })
        
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pedidos/depositar', methods=['POST'])
def depositar_pedidos():
    """API para atualizar status de depositado"""
    print("💰 Processando depósito de pedidos...")
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Extrair informações dos pedidos
        pedidos_para_depositar = data.get('pedidos', [])
        
        if not pedidos_para_depositar:
            return jsonify({
                'success': False,
                'error': 'Nenhum pedido especificado'
            }), 400
        
        print(f"📋 Processando {len(pedidos_para_depositar)} pedidos...")
        
        # Conectar ao banco
        connection = conectar_azure_sql()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Erro de conexão com o banco de dados'
            }), 500
        
        cursor = connection.cursor()
        
        # Atualizar cada pedido baseado em critérios únicos
        pedidos_atualizados = 0
        
        for pedido in pedidos_para_depositar:
            try:
                # Usar critérios únicos mais simples para identificar o pedido
                responsavel = pedido.get('RESPONSAVEL_PELO_CARTAO')
                pagcorp = pedido.get('PAGCORP')
                total_pagar = pedido.get('TOTAL_PAGAR')
                
                # Query de atualização mais simples
                query = """
                UPDATE PEDIDOS 
                SET DEPOSITADO = 'DEPOSITADO' 
                WHERE RESPONSAVEL_PELO_CARTAO = %s 
                AND PAGCORP = %s
                AND TOTAL_PAGAR = %s
                AND (DEPOSITADO IS NULL OR DEPOSITADO != 'DEPOSITADO')
                """
                
                cursor.execute(query, (responsavel, pagcorp, total_pagar))
                
                if cursor.rowcount > 0:
                    pedidos_atualizados += cursor.rowcount
                    print(f"✅ Pedido atualizado: {responsavel} - {pagcorp}")
                else:
                    print(f"⚠️ Pedido não encontrado ou já depositado: {responsavel} - {pagcorp}")
                    
            except Exception as e:
                print(f"❌ Erro ao atualizar pedido {responsavel}: {e}")
                continue
        
        # Confirmar as mudanças
        connection.commit()
        
        # Fechar conexão
        cursor.close()
        connection.close()
        
        print(f"✅ {pedidos_atualizados} pedidos atualizados com sucesso!")
        
        return jsonify({
            'success': True,
            'message': f'{pedidos_atualizados} pedidos marcados como depositados',
            'pedidos_atualizados': pedidos_atualizados
        })
        
    except Exception as e:
        print(f"❌ Erro na API de depósito: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pedidos/depositar-por-id', methods=['POST'])
def depositar_pedidos_por_id():
    """API alternativa para atualizar por IDs (se a tabela tiver campo ID)"""
    print("💰 Processando depósito por IDs...")
    
    try:
        data = request.get_json()
        pedidos_ids = data.get('ids', [])
        
        if not pedidos_ids:
            return jsonify({
                'success': False,
                'error': 'Nenhum ID especificado'
            }), 400
        
        # Conectar ao banco
        connection = conectar_azure_sql()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Erro de conexão'
            }), 500
        
        cursor = connection.cursor()
        
        # Criar placeholders para os IDs
        placeholders = ','.join(['?' for _ in pedidos_ids])
        query = f"UPDATE PEDIDOS SET DEPOSITADO = 'DEPOSITADO' WHERE ID IN ({placeholders})"
        
        cursor.execute(query, pedidos_ids)
        pedidos_atualizados = cursor.rowcount
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"✅ {pedidos_atualizados} pedidos atualizados por ID!")
        
        return jsonify({
            'success': True,
            'message': f'{pedidos_atualizados} pedidos atualizados',
            'pedidos_atualizados': pedidos_atualizados
        })
        
    except Exception as e:
        print(f"❌ Erro na API de depósito por ID: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Endpoint de saúde"""
    return jsonify({
        'status': 'ok',
        'server': 'Python Flask',
        'database': 'Azure SQL Server',
        'endpoints': [
            'GET /api/pedidos - Buscar pedidos',
            'POST /api/pedidos/depositar - Atualizar status',
            'POST /api/pedidos/depositar-por-id - Atualizar por IDs'
        ]
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔌 APIs disponíveis:")
    print("   GET  /api/pedidos - Buscar dados")
    print("   POST /api/pedidos/depositar - Marcar como depositado")
    print("   POST /api/pedidos/depositar-por-id - Marcar por IDs")
    print("🔧 Configurações:")
    print(f"   Server: {SQL_SERVER}")
    print(f"   Database: {SQL_DATABASE}")
    print(f"   User: {SQL_USERNAME}")
    print("✅ Iniciando servidor...")
    
    # Usar porta do Railway se disponível, senão usar 5000
    import os
    port = int(os.environ.get('PORT', 5000))
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()