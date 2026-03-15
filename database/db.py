import sqlite3
import hashlib


def get_connection():
    conn = sqlite3.connect('cisec_bot.db')
    conn.row_factory = sqlite3.Row
    return conn


def hash_senha(senha):
    """Criptografa senha"""
    return hashlib.sha256(senha.encode()).hexdigest()


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            cep TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de contatos de emergência
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            nome_profissional TEXT NOT NULL,
            telefone TEXT NOT NULL,
            whatsapp TEXT,
            endereco TEXT,
            descricao TEXT
        )
    ''')
    
    # Insere contatos padrão (se estiver vazio)
    cursor.execute("SELECT COUNT(*) FROM contatos")
    if cursor.fetchone()[0] == 0:
        contatos_padrao = [
            ('Emergência', 'Polícia Militar', '190', None, 'Todo o bairro', 'Emergência policial'),
            ('Emergência', 'Bombeiros', '193', None, 'Todo o bairro', 'Emergência médica/incêndio'),
            ('Emergência', 'SAMU', '192', None, 'Todo o bairro', 'Ambulância'),
            ('Saúde', 'UBS Bairro', '(11) 3333-4444', '11999998888', 'Rua das Flores, 123', 'Posto de saúde'),
            ('Serviços', 'Chaveiro 24h', '(11) 5555-6666', '11977776666', 'Rua Principal, 456', 'Chaveiro emergencial'),
            ('Serviços', 'Borracheiro', '(11) 7777-8888', '11988887777', 'Av. Central, 789', 'Borracharia 24 horas'),
            ('Condomínio', 'Síndico João', '(11) 9999-0000', '11999990000', 'Administração', 'Síndico do condomínio'),
        ]
        cursor.executemany('''
            INSERT INTO contatos (categoria, nome_profissional, telefone, whatsapp, endereco, descricao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', contatos_padrao)
        print("Contatos padrão inseridos!")
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado!")


def usuario_existe(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE telegram_id = ?", (telegram_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None


def cadastrar_usuario(telegram_id, nome, telefone, cep, senha):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        senha_hash = hash_senha(senha)
        cursor.execute('''
            INSERT INTO usuarios (telegram_id, nome, telefone, cep, senha_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, nome, telefone, cep, senha_hash))
        conn.commit()
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
        SELECT * FROM usuarios WHERE telegram_id = ? AND senha_hash = ?
    ''', (telegram_id, senha_hash))
    
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None


def get_usuario(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE telegram_id = ?", (telegram_id,))
    resultado = cursor.fetchone()
    conn.close()
    return dict(resultado) if resultado else None


def listar_categorias():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT categoria FROM contatos ORDER BY categoria")
    categorias = [row['categoria'] for row in cursor.fetchall()]
    conn.close()
    return categorias


def listar_contatos_por_categoria(categoria):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM contatos WHERE categoria = ? ORDER BY nome_profissional
    ''', (categoria,))
    contatos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return contatos


def buscar_contatos(termo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM contatos 
        WHERE nome_profissional LIKE ? OR descricao LIKE ?
        ORDER BY nome_profissional
    ''', (f'%{termo}%', f'%{termo}%'))
    contatos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return contatos

def get_connection():
    """Retorna conexão com o banco"""
    import sqlite3
    conn = sqlite3.connect('cisec_bot.db')
    conn.row_factory = sqlite3.Row
    return conn