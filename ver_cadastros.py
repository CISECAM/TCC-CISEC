import sqlite3

def ver_usuarios():
    conn = sqlite3.connect('cisec_bot.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT nome, telefone, cep, data_cadastro 
        FROM usuarios 
        ORDER BY data_cadastro DESC
    """)
    
    usuarios = cursor.fetchall()
    conn.close()
    
    if not usuarios:
        print("😕 Nenhum usuário cadastrado ainda.")
        return
    
    print(f"\n👥 TOTAL DE CADASTRADOS: {len(usuarios)}\n")
    print("=" * 50)
    
    for i, usuario in enumerate(usuarios, 1):
        nome, telefone, cep, data = usuario
        print(f"\n{i}. Nome: {nome}")
        print(f"   Telefone: {telefone}")
        print(f"   CEP: {cep}")
        print(f"   Data: {data}")
        print("-" * 50)

if __name__ == "__main__":
    ver_usuarios()