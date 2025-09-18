import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='rcsintegra',
        user='rcsintegra',
        password='rcsintegra123'
    )
    print("SUCESSO: Conexao estabelecida!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT current_user, current_database();")
    result = cursor.fetchone()
    print(f"Usuario: {result[0]}, Database: {result[1]}")
    
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    count = cursor.fetchone()[0]
    print(f"Tabelas encontradas: {count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERRO: {e}")