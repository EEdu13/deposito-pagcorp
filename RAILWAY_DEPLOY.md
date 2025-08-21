# 🚀 DEPLOY NO RAILWAY - VARIÁVEIS DE AMBIENTE

## ⚙️ Configuração das Variáveis no Railway:

Acesse o painel do Railway → Settings → Environment Variables e adicione:

```
SQL_SERVER=alrflorestal.database.windows.net
SQL_DATABASE=Tabela_teste
SQL_USERNAME=sqladmin
SQL_PASSWORD=SenhaForte123!
```

## 📁 Arquivos necessários para deploy:

✅ `app.py` - Servidor Flask principal
✅ `dashboard-pedidos-real.html` - Interface do usuário
✅ `requirements.txt` - Dependências Python
✅ `Procfile` - Comando de inicialização
✅ `railway.json` - Configuração do Railway

## 🌐 Como acessar após deploy:

O Railway vai gerar uma URL automática como:
`https://seu-projeto-railway.up.railway.app`

## 🔧 Comandos locais para teste:

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar localmente
python app.py
```

## 📝 Nota de Segurança:

- ✅ Credenciais removidas do código
- ✅ Usando variáveis de ambiente
- ✅ Pronto para produção no Railway

## 🎯 Sistema Funcional:

- ✅ Conexão com Azure SQL Server
- ✅ Interface "DEPÓSITO DE SALDO PAGCORP" 
- ✅ Botão depositar funcionando
- ✅ Atualização automática da interface
- ✅ Filtros por data e status
- ✅ Agrupamento por líder e dia
