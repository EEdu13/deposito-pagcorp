# 💳 DEPÓSITO DE SALDO PAGCORP

Sistema web para gerenciamento de depósitos de saldo PAGCORP, desenvolvido em Flask + HTML/CSS/JavaScript.

## 🚀 Deploy no Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/EEdu13/deposito-pagcorp)

## ⚙️ Configuração

### Variáveis de Ambiente Necessárias:

```
SQL_SERVER=seu-servidor-azure.database.windows.net
SQL_DATABASE=nome-do-banco
SQL_USERNAME=usuario
SQL_PASSWORD=senha
```

## 🎯 Funcionalidades

- ✅ **Conexão Azure SQL Server** - Conecta diretamente ao banco de dados
- ✅ **Interface Responsiva** - Design moderno e intuitivo  
- ✅ **Depósito em Lote** - Depositar múltiplos pedidos de uma vez
- ✅ **Filtros Avançados** - Por data, status (Pendente/Aprovado/Depositado)
- ✅ **Agrupamento Inteligente** - Por líder e dia para facilitar gestão
- ✅ **Atualização em Tempo Real** - Interface atualiza automaticamente após depósito
- ✅ **Notificações Visuais** - Feedback claro das operações

## 🛠️ Tecnologias

- **Backend**: Python Flask + Flask-CORS
- **Database**: Azure SQL Server (pymssql)
- **Frontend**: HTML5 + CSS3 + JavaScript (Vanilla)
- **Deploy**: Railway

## 🏃‍♂️ Execução Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# Executar
python app.py
```

Acesse: `http://localhost:5000`

## 📊 Interface

### Tela Principal
- Cabeçalho com logo 💳 "DEPÓSITO DE SALDO PAGCORP"
- Filtros por data de envio
- Botões de status: Todos, Pendente, Aprovado, Depositado
- Seleção em massa para depósitos

### Cards de Pedidos
- **Não Depositado**: Botão verde 💰 para depositar
- **Depositado**: Badge verde "✓ DEPOSITADO"
- Informações do responsável, valor e quantidade de pedidos
- Detalhes expansíveis

## 🔒 Segurança

- ✅ Credenciais em variáveis de ambiente
- ✅ CORS configurado adequadamente
- ✅ Validação de dados no backend
- ✅ Tratamento de erros robusto

## 📁 Estrutura do Projeto

```
├── app.py                     # Servidor Flask principal
├── dashboard-pedidos-real.html # Interface do usuário
├── requirements.txt           # Dependências Python
├── Procfile                   # Comando Railway
├── railway.json              # Configuração Railway
├── .env.example              # Exemplo de variáveis
├── .gitignore                # Arquivos ignorados
└── RAILWAY_DEPLOY.md         # Instruções de deploy
```

## 🎨 Design

Interface moderna com:
- Gradiente azul no cabeçalho
- Cards com sombras e hover effects
- Botões com animações suaves
- Responsive design para mobile
- Tema de cores profissional

---

**Desenvolvido para otimizar o processo de depósito de saldos PAGCORP** 🚀
