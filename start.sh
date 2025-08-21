#!/bin/bash

# Encontrar o executável Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Python não encontrado!"
    exit 1
fi

echo "Usando: $PYTHON_CMD"
echo "Versão: $($PYTHON_CMD --version)"

# Executar a aplicação
exec $PYTHON_CMD app.py
