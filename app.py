#!/usr/bin/env python3

import os
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import pymssql
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ========== CONFIGURAÇÕES CENTRALIZADAS ==========
SQL_SERVER = os.getenv('SQL_SERVER', 'localhost')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'database')
SQL_USERNAME = os.getenv('SQL_USERNAME', 'user')
SQL_PASSWORD = os.getenv('SQL_PASSWORD', 'password')

# ========== FUNÇÕES AUXILIARES ==========
def conectar_azure_sql():
    """Conecta ao Azure SQL Server com retry"""
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

def processar_dados_query(dados):
    """Processa resultados da query para JSON"""
    dados_processados = []
    colunas = []
    
    if dados:
        colunas = list(dados[0].keys())
        
        for linha in dados:
            linha_processada = {}
            for coluna, valor in linha.items():
                if isinstance(valor, datetime):
                    linha_processada[coluna] = valor.isoformat()
                else:
                    linha_processada[coluna] = valor
            dados_processados.append(linha_processada)
    
    return dados_processados, colunas

# ========== ROTAS ==========
@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'deposito-pagcorp',
        'database': SQL_DATABASE,
        'server': SQL_SERVER
    }), 200

@app.route('/')
def dashboard():
    print("📄 Servindo dashboard")
    return send_file('dashboard-pedidos-real.html')

@app.route('/sw.js')
def service_worker():
    return send_file('sw.js')

@app.route('/manifest.json')
def manifest():
    return send_file('manifest.json')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve arquivos estáticos (imagens, etc)"""
    try:
        return send_file(filename)
    except:
        return '', 404

@app.route('/api/pedidos')
def get_pedidos():
    """Busca todos os pedidos"""
    print("🔍 GET /api/pedidos")
    
    try:
        connection = conectar_azure_sql()
        if not connection:
            return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

        cursor = connection.cursor(as_dict=True)
        cursor.execute("SELECT * FROM PEDIDOS")
        dados = cursor.fetchall()
        
        dados_processados, colunas = processar_dados_query(dados)
        
        cursor.close()
        connection.close()
        
        print(f"✅ {len(dados_processados)} registros retornados")
        
        return jsonify({
            'success': True,
            'data': dados_processados,
            'columns': colunas,
            'count': len(dados_processados)
        })
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pedidos/depositar', methods=['POST'])
def depositar_pedidos():
    """Atualiza status de depositado - OTIMIZADO COM BATCH UPDATE"""
    print("💰 POST /api/pedidos/depositar")
    
    try:
        data = request.get_json()
        print(f"📦 Dados recebidos: {data}")
        pedidos = data.get('pedidos', [])
        
        if not pedidos:
            print("⚠️ Nenhum pedido encontrado no request")
            return jsonify({'success': False, 'error': 'Nenhum pedido'}), 400
        
        print(f"📋 Processando {len(pedidos)} pedidos...")
        print(f"📋 Primeiro pedido: {pedidos[0] if pedidos else 'N/A'}")
        
        connection = conectar_azure_sql()
        if not connection:
            return jsonify({'success': False, 'error': 'Erro de conexão'}), 500
        
        cursor = connection.cursor()
        
        # 🚀 OTIMIZAÇÃO: Batch update com IN clause
        # Criar lista de tuplas (responsavel, pagcorp, total)
        valores = [(p.get('RESPONSAVEL_PELO_CARTAO'), p.get('PAGCORP'), p.get('TOTAL_PAGAR')) 
                   for p in pedidos]
        
        # Construir query com múltiplas condições
        condicoes = []
        parametros = []
        
        for responsavel, pagcorp, total in valores:
            condicoes.append("(RESPONSAVEL_PELO_CARTAO = %s AND PAGCORP = %s AND TOTAL_PAGAR = %s)")
            parametros.extend([responsavel, pagcorp, total])
        
        query = f"""
        UPDATE PEDIDOS 
        SET DEPOSITADO = 'DEPOSITADO'
        WHERE (DEPOSITADO IS NULL OR DEPOSITADO != 'DEPOSITADO')
        AND ({' OR '.join(condicoes)})
        """
        
        # Converter lista para tupla (pymssql exige tupla ou dict)
        cursor.execute(query, tuple(parametros))
        pedidos_atualizados = cursor.rowcount
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"✅ {pedidos_atualizados} pedidos atualizados em UMA query!")
        
        return jsonify({
            'success': True,
            'message': f'{pedidos_atualizados} pedidos depositados',
            'pedidos_atualizados': pedidos_atualizados
        })
        
    except Exception as e:
        print(f"❌ Erro ao depositar: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== INICIALIZAÇÃO ==========
if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print(f"📊 Dashboard: http://localhost:5000")
    print(f"🔧 Database: {SQL_DATABASE}")
    print("✅ Servidor iniciado!")
    
    port = int(os.environ.get('PORT', 5000))
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()