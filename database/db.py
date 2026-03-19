import sqlite3
import hashlib

def get_connection():
    conn = sqlite3.connect('hotel_bot.db')  # Nome novo
    conn.row_factory = sqlite3.Row
    return conn

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de hóspedes (antiga tabela usuarios)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospedes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            quarto TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            chave_acesso TEXT NOT NULL,
            data_checkin TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de serviços do hotel
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos_hotel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            nome_servico TEXT NOT NULL,
            telefone TEXT NOT NULL,
            whatsapp TEXT,
            descricao TEXT,
            horario_funcionamento TEXT
        )
    ''')
    
    # Tabela de chaves de acesso válidas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chaves_acesso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE NOT NULL,
            descricao TEXT,
            ativa BOOLEAN DEFAULT 1,
            usada_por INTEGER,
            data_uso TIMESTAMP
        )
    ''')
    
    # Insere chaves padrão se estiver vazio
    cursor.execute("SELECT COUNT(*) FROM chaves_acesso")
    if cursor.fetchone()[0] == 0:
        chaves_padrao = [
            ('HOTEL2024', 'Chave Geral', 1, None, None),
            ('RECEP01', 'Recepção', 1, None, None),
            ('ADMIN99', 'Administrador', 1, None, None),
        ]
        cursor.executemany('''
            INSERT INTO chaves_acesso (chave, descricao, ativa, usada_por, data_uso)
            VALUES (?, ?, ?, ?, ?)
        ''', chaves_padrao)
        print("Chaves de acesso padrão criadas!")
    
    # Insere serviços padrão se estiver vazio
    cursor.execute("SELECT COUNT(*) FROM servicos_hotel")
    if cursor.fetchone()[0] == 0:
        servicos_padrao = [
            ('Recepção', 'Recepção 24h', '0', None, 'Atendimento geral', '24 horas'),
            ('Quarto', 'Room Service', '101', None, 'Serviço de quarto', '06:00 - 23:00'),
            ('Limpeza', 'Serviço de Limpeza', '102', None, 'Limpeza diária', '08:00 - 18:00'),
            ('Manutenção', 'Manutenção', '103', None, 'Problemas no quarto', '24 horas'),
            ('Restaurante', 'Restaurante', '200', None, 'Café, almoço e jantar', '06:00 - 22:00'),
            ('Lavanderia', 'Lavanderia', '201', None, 'Lavagem de roupas', '08:00 - 20:00'),
        ]
        cursor.executemany('''
            INSERT INTO servicos_hotel (categoria, nome_servico, telefone, whatsapp, descricao, horario_funcionamento)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', servicos_padrao)
        print("Serviços do hotel inseridos!")
    
    conn.commit()
    conn.close()
    print("Banco de dados do hotel inicializado!")

def validar_chave_acesso(chave):
    """Verifica se a chave é válida e não foi usada"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM chaves_acesso 
        WHERE chave = ? AND ativa = 1 AND usada_por IS NULL
    ''', (chave,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def marcar_chave_usada(chave, telegram_id):
    """Marca chave como usada pelo hóspede"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE chaves_acesso 
        SET usada_por = ?, data_uso = CURRENT_TIMESTAMP
        WHERE chave = ?
    ''', (telegram_id, chave))
    conn.commit()
    conn.close()

def hospede_existe(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospedes WHERE telegram_id = ?", (telegram_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def cadastrar_hospede(telegram_id, nome, telefone, quarto, senha, chave_acesso):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        senha_hash = hash_senha(senha)
        cursor.execute('''
            INSERT INTO hospedes (telegram_id, nome, telefone, quarto, senha_hash, chave_acesso)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (telegram_id, nome, telefone, quarto, senha_hash, chave_acesso))
        conn.commit()
        
        # Marca chave como usada
        marcar_chave_usada(chave_acesso, telegram_id)
        
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validar_login(telegram_id, senha):
    conn = get_connection()
    cursor = conn.cursor()
    senha_hash = hash_senha(senha)
    cursor.execute('''
        SELECT * FROM hospedes WHERE telegram_id = ? AND senha_hash = ?
    ''', (telegram_id, senha_hash))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def get_hospede(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospedes WHERE telegram_id = ?", (telegram_id,))
    resultado = cursor.fetchone()
    conn.close()
    return dict(resultado) if resultado else None

def listar_categorias_servicos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT categoria FROM servicos_hotel ORDER BY categoria")
    categorias = [row['categoria'] for row in cursor.fetchall()]
    conn.close()
    return categorias

def listar_servicos_por_categoria(categoria):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM servicos_hotel WHERE categoria = ? ORDER BY nome_servico
    ''', (categoria,))
    servicos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return servicos

def buscar_servicos(termo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM servicos_hotel 
        WHERE nome_servico LIKE ? OR descricao LIKE ?
        ORDER BY nome_servico
    ''', (f'%{termo}%', f'%{termo}%'))
    servicos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return servicos

def get_todos_hospedes():
    """Retorna apenas números dos hóspedes cadastrados"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT telefone, quarto FROM hospedes ORDER BY data_checkin DESC")
    hospedes = cursor.fetchall()
    conn.close()
    return hospedes

def get_connection():
    """Retorna conexão com o banco"""
    import sqlite3
    conn = sqlite3.connect('hotel_bot.db')
    conn.row_factory = sqlite3.Row
    return conn