#!/usr/bin/env python3
"""
Script para executar todos os testes do RCS Gateway.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Executa um comando e exibe o resultado."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {command}")
        print(f"Código de saída: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Função principal."""
    print("🚀 Iniciando testes do RCS Gateway")
    
    # Verificar se estamos no diretório correto
    if not Path("main.py").exists():
        print("❌ Execute este script no diretório raiz do projeto (onde está o main.py)")
        sys.exit(1)
    
    # Instalar dependências de teste se necessário
    print("\n📦 Verificando dependências...")
    try:
        import pytest
        import httpx
        print("✅ Dependências de teste já instaladas")
    except ImportError:
        print("📦 Instalando dependências de teste...")
        if not run_command("pip install pytest pytest-asyncio pytest-mock", "Instalando dependências"):
            sys.exit(1)
    
    # Lista de comandos de teste
    test_commands = [
        {
            "command": "python -m pytest tests/ -v",
            "description": "Executando todos os testes"
        },
        {
            "command": "python -m pytest tests/test_rcs_basic.py -v",
            "description": "Testes RCS Basic"
        },
        {
            "command": "python -m pytest tests/test_rcs_single.py -v",
            "description": "Testes RCS Single"
        },
        {
            "command": "python -m pytest tests/test_rcs_webhook.py -v",
            "description": "Testes RCS Webhook e Callbacks"
        },
        {
            "command": "python -m pytest tests/test_templates.py -v",
            "description": "Testes de Templates"
        },
        {
            "command": "python -m pytest tests/test_validations.py -v",
            "description": "Testes de Validações"
        }
    ]
    
    # Executar testes
    failed_tests = []
    
    for test in test_commands:
        if not run_command(test["command"], test["description"]):
            failed_tests.append(test["description"])
    
    # Relatório final
    print(f"\n{'='*60}")
    print("📊 RELATÓRIO FINAL")
    print(f"{'='*60}")
    
    if failed_tests:
        print(f"❌ {len(failed_tests)} grupo(s) de teste falharam:")
        for failed in failed_tests:
            print(f"   - {failed}")
        print(f"\n✅ {len(test_commands) - len(failed_tests)} grupo(s) de teste passaram")
        sys.exit(1)
    else:
        print("🎉 Todos os testes passaram com sucesso!")
        print(f"✅ {len(test_commands)} grupo(s) de teste executados")
    
    # Executar relatório de cobertura se disponível
    print(f"\n{'='*60}")
    print("📈 Tentando gerar relatório de cobertura...")
    print(f"{'='*60}")
    
    try:
        subprocess.run("pip install pytest-cov", shell=True, check=True, capture_output=True)
        run_command(
            "python -m pytest tests/ --cov=. --cov-report=html --cov-report=term",
            "Relatório de cobertura"
        )
        print("📊 Relatório de cobertura gerado em htmlcov/index.html")
    except:
        print("ℹ️  Para relatório de cobertura, instale: pip install pytest-cov")

if __name__ == "__main__":
    main()
