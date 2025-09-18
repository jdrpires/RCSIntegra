#!/usr/bin/env python3
"""
Script para executar testes em modo simulação.
"""

import os
import sys
import subprocess

def main():
    """Executa os testes em modo simulação."""
    
    # Definir variáveis de ambiente para simulação
    env = os.environ.copy()
    env['SIMULATION_MODE'] = 'True'
    env['DATABASE_URL'] = 'sqlite:///./test.db'
    
    print("🧪 Executando testes em modo simulação...")
    print("📊 Configurações:")
    print(f"   - SIMULATION_MODE: {env.get('SIMULATION_MODE')}")
    print(f"   - DATABASE_URL: {env.get('DATABASE_URL')}")
    print()
    
    # Executar testes
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', 
            '-v',
            '--tb=short',
            '-x'  # Para na primeira falha
        ], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print("\n✅ Todos os testes passaram!")
        else:
            print(f"\n❌ Testes falharam com código: {result.returncode}")
            
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
        return 1
    except Exception as e:
        print(f"\n💥 Erro ao executar testes: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())