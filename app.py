#!/usr/bin/env python3

import os
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import pyodbc
from queue import Queue
from threading import Lock
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ========== CONFIGURAÇÕES CENTRALIZADAS ==========
SQL_SERVER = os.getenv('SQL_SERVER', 'localhost')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'database')
SQL_USERNAME = os.getenv('SQL_USERNAME', 'user')
SQL_PASSWORD = os.getenv('SQL_PASSWORD', 'password')

# ========== CONNECTION POOL ==========
class ConnectionPool:
    def __init__(self, pool_size=5):
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()
        self._initialize_pool()
    
    def _create_connection(self):
        """Cria nova conexão pyodbc"""
        connection_string = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={SQL_SERVER};'
            f'DATABASE={SQL_DATABASE};'
            f'UID={SQL_USERNAME};'
            f'PWD={SQL_PASSWORD};'
            f'Encrypt=yes;'
            f'TrustServerCertificate=yes;'
            f'Connection Timeout=30;'
        )
        return pyodbc.connect(connection_string)
    
    def _initialize_pool(self):
        """Inicializa pool com conexões"""
        for _ in range(self.pool_size):
            try:
                conn = self._create_connection()
                self.pool.put(conn)
            except Exception as e:
                print(f"⚠️ Erro ao criar conexão do pool: {e}")
    
    def get_connection(self):
        """Obtém conexão do pool"""
        try:
            conn = self.pool.get(timeout=10)
            # Testa se conexão está ativa
            try:
                conn.cursor().execute("SELECT 1")
                return conn
            except:
                # Reconecta se estiver morta
                try:
                    conn.close()
                except:
                    pass
                return self._create_connection()
        except:
            return self._create_connection()
    
    def return_connection(self, conn):
        """Retorna conexão ao pool"""
        try:
            if self.pool.qsize() < self.pool_size:
                self.pool.put(conn)
            else:
                conn.close()
        except:
            try:
                conn.close()
            except:
                pass

# Inicializar pool global
pool = ConnectionPool(pool_size=10)

# ========== FUNÇÕES AUXILIARES ==========
def conectar_azure_sql():
    """Obtém conexão do pool (mantida para compatibilidade)"""
    return pool.get_connection()

def dict_row_factory(cursor):
    """Converte Row em dict para JSON"""
    columns = [column[0] for column in cursor.description]
    def create_row(row):
        return dict(zip(columns, row))
    return create_row

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
    """Busca todos os pedidos - OTIMIZADO"""
    print("🔍 GET /api/pedidos")
    
    connection = None
    try:
        connection = conectar_azure_sql()
        if not connection:
            return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

        cursor = connection.cursor()
        
        # SELECT otimizado: apenas colunas necessárias + datetime convertido no SQL
        cursor.execute("""
            SELECT 
                RESPONSAVEL_PELO_CARTAO,
                PAGCORP,
                TOTAL_PAGAR,
                CONVERT(VARCHAR(23), DATA_ENVIO1, 126) as DATA_ENVIO1,
                DEPOSITADO,
                FECHAMENTO,
                APROVADO_POR,
                PROJETO,
                OBSERVACOES
            FROM PEDIDOS WITH (NOLOCK)
            WHERE DATA_ENVIO1 >= DATEADD(day, -15, GETDATE())
            ORDER BY DATA_ENVIO1 DESC
        """)
        
        # Converter para dict
        columns = [column[0] for column in cursor.description]
        dados = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        pool.return_connection(connection)
        
        print(f"✅ {len(dados)} registros retornados")
        
        return jsonify({
            'success': True,
            'data': dados,
            'columns': columns,
            'count': len(dados)
        })
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if connection:
            try:
                connection.close()
            except:
                pass
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pedidos/depositar', methods=['POST'])
def depositar_pedidos():
    """Atualiza status de depositado - OTIMIZADO COM MERGE"""
    print("💰 POST /api/pedidos/depositar")
    
    connection = None
    try:
        data = request.get_json()
        pedidos = data.get('pedidos', [])
        
        if not pedidos:
            print("⚠️ Nenhum pedido encontrado no request")
            return jsonify({'success': False, 'error': 'Nenhum pedido'}), 400
        
        print(f"📋 Processando {len(pedidos)} pedidos...")
        
        connection = conectar_azure_sql()
        if not connection:
            return jsonify({'success': False, 'error': 'Erro de conexão'}), 500
        
        cursor = connection.cursor()
        
        # 🚀 OTIMIZAÇÃO: Usar tabela temporária + MERGE (muito mais rápido que OR dinâmico)
        # 1. Criar tabela temporária
        cursor.execute("""
            CREATE TABLE #TempDepositos (
                RESPONSAVEL_PELO_CARTAO NVARCHAR(255),
                PAGCORP NVARCHAR(100),
                TOTAL_PAGAR DECIMAL(18,2)
            )
        """)
        
        # 2. Inserir dados em batch
        valores = [(p.get('RESPONSAVEL_PELO_CARTAO'), p.get('PAGCORP'), p.get('TOTAL_PAGAR')) 
                   for p in pedidos]
        
        cursor.executemany(
            "INSERT INTO #TempDepositos (RESPONSAVEL_PELO_CARTAO, PAGCORP, TOTAL_PAGAR) VALUES (?, ?, ?)",
            valores
        )
        
        # 3. MERGE otimizado (1 operação ao invés de N)
        cursor.execute("""
            UPDATE p
            SET p.DEPOSITADO = 'DEPOSITADO'
            FROM PEDIDOS p
            INNER JOIN #TempDepositos t ON 
                p.RESPONSAVEL_PELO_CARTAO = t.RESPONSAVEL_PELO_CARTAO AND
                p.PAGCORP = t.PAGCORP AND
                p.TOTAL_PAGAR = t.TOTAL_PAGAR
            WHERE (p.DEPOSITADO IS NULL OR p.DEPOSITADO != 'DEPOSITADO')
        """)
        
        pedidos_atualizados = cursor.rowcount
        
        # 4. Limpar temp table
        cursor.execute("DROP TABLE #TempDepositos")
        
        connection.commit()
        cursor.close()
        pool.return_connection(connection)
        
        print(f"✅ {pedidos_atualizados} pedidos atualizados (MERGE otimizado)!")
        
        return jsonify({
            'success': True,
            'message': f'{pedidos_atualizados} pedidos depositados',
            'pedidos_atualizados': pedidos_atualizados
        })
        
    except Exception as e:
        print(f"❌ Erro ao depositar: {e}")
        if connection:
            try:
                connection.rollback()
                connection.close()
            except:
                pass
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