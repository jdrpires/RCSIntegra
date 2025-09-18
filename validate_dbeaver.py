#!/usr/bin/env python3
import subprocess
import sys

def test_dbeaver_connection():
    """Valida se as credenciais funcionam para DBeaver"""
    
    print("=== VALIDACAO DBEAVER ===")
    print("Host: localhost")
    print("Port: 5432") 
    print("Database: rcsintegra")
    print("Username: rcsintegra")
    print("Password: rcsintegra123")
    print("URL: jdbc:postgresql://localhost:5432/rcsintegra")
    print()
    
    # Testa via Docker (simula conexão externa)
    try:
        cmd = [
            "docker", "run", "--rm", "--network", "host",
            "-e", "PGPASSWORD=rcsintegra123",
            "postgres:15-alpine",
            "psql", "-h", "localhost", "-U", "rcsintegra", "-d", "rcsintegra",
            "-c", "SELECT current_user, current_database(), version();"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ SUCESSO: Conexao externa funcionando!")
            print("Resultado:")
            print(result.stdout)
            
            # Lista tabelas
            cmd2 = [
                "docker", "run", "--rm", "--network", "host",
                "-e", "PGPASSWORD=rcsintegra123", 
                "postgres:15-alpine",
                "psql", "-h", "localhost", "-U", "rcsintegra", "-d", "rcsintegra",
                "-c", "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"
            ]
            
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
            if result2.returncode == 0:
                print("Tabelas disponíveis:")
                print(result2.stdout)
            
            return True
        else:
            print("❌ ERRO na conexao:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    success = test_dbeaver_connection()
    
    if success:
        print("\n🎯 CONFIGURACAO DBEAVER:")
        print("1. Abra DBeaver")
        print("2. Nova Conexao > PostgreSQL")
        print("3. Configure:")
        print("   Host: localhost")
        print("   Port: 5432")
        print("   Database: rcsintegra") 
        print("   Username: rcsintegra")
        print("   Password: rcsintegra123")
        print("4. Teste a conexao")
        print("5. Salve e conecte!")
    else:
        print("\n❌ Problema na configuracao. Verifique os containers.")
    
    sys.exit(0 if success else 1)