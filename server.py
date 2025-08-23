from flask import Flask, jsonify, send_file
import pymssql
import json
from datetime import datetime
import os

app = Flask(__name__)

# Configurações do banco Azure SQL
SQL_SERVER = 'alrflorestal.database.windows.net'
SQL_DATABASE = 'Tabela_teste'
SQL_USERNAME = 'sqladmin'
SQL_PASSWORD = 'SenhaForte123!'

def conectar_azure_sql():
    """Conecta ao Azure SQL Server"""
    try:
        connection = pymssql.connect(
            server=SQL_SERVER,
            user=SQL_USERNAME,
            password=SQL_PASSWORD,
            database=SQL_DATABASE,
            timeout=30,
            login_timeout=30
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

@app.route('/')
def dashboard():
    """Serve o dashboard HTML"""
    return send_file('dashboard.html')

@app.route('/api/pedidos')
def get_pedidos():
    """API para buscar dados da tabela PEDIDOS"""
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
        
        print(f"✅ Consulta executada com sucesso: {len(dados_processados)} registros encontrados")
        
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

@app.route('/health')
def health():
    """Endpoint de saúde para verificar se o servidor está funcionando"""
    return jsonify({
        'status': 'ok',
        'server': 'Python Flask',
        'database': 'Azure SQL Server'
    })

if __name__ == '__main__':
    try:
        print("🚀 Iniciando servidor Flask...")
        print("📊 Dashboard: http://localhost:5000")
        print("🔌 API: http://localhost:5000/api/pedidos")
        print("🔧 Configurações:")
        print(f"   Server: {SQL_SERVER}")
        print(f"   Database: {SQL_DATABASE}")
        print(f"   User: {SQL_USERNAME}")
        print("✅ Iniciando app.run()...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()