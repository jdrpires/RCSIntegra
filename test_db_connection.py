#!/usr/bin/env python3
"""
Teste de conexão com PostgreSQL para validar credenciais do DBeaver
"""
import psycopg2
import sys

def test_connection():
    """Testa conexão com PostgreSQL"""
    try:
        # Configurações de conexão
        conn_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'rcsintegra',
            'user': 'rcsintegra',
            'password': 'rcsintegra123'
        }
        
        print("Testando conexao PostgreSQL...")
        print(f"Host: {conn_params['host']}")
        print(f"Port: {conn_params['port']}")
        print(f"Database: {conn_params['database']}")
        print(f"User: {conn_params['user']}")
        
        # Conecta ao banco
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Testa consulta simples
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"SUCESSO: Conexao bem-sucedida!")
        print(f"PostgreSQL Version: {version}")
        
        # Lista tabelas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\nTabelas disponiveis ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print(f"\nCredenciais para DBeaver:")
        print(f"Host: localhost")
        print(f"Port: 5432")
        print(f"Database: rcsintegra")
        print(f"Username: rcsintegra")
        print(f"Password: rcsintegra123")
        
        return True
        
    except psycopg2.Error as e:
        print(f"ERRO PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)