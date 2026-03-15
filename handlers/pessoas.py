from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_connection

def get_telefones_cadastrados():
    """Retorna apenas os telefones dos usuários cadastrados"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT telefone, data_cadastro 
        FROM usuarios 
        ORDER BY data_cadastro DESC
    """)
    
    telefones = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return telefones

async def mostrar_pessoas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra lista de pessoas cadastradas (apenas números)"""
    query = update.callback_query
    await query.answer()
    
    telefones = get_telefones_cadastrados()
    
    if not telefones:
        texto = "👥 *Pessoas Cadastradas*\n\n_Nenhuma pessoa cadastrada ainda._"
    else:
        texto = f"👥 *Pessoas Cadastradas*\n\n"
        texto += f"Total: {len(telefones)} pessoa(s)\n\n"
        texto += "📱 *Números cadastrados:*\n\n"
        
        for i, pessoa in enumerate(telefones, 1):
            tel = pessoa['telefone']
            # Oculta parte do número para privacidade (mostra só últimos 4 dígitos)
            if len(tel) > 4:
                tel_oculto = "*" * (len(tel)-4) + tel[-4:]
            else:
                tel_oculto = tel
            
            data = pessoa['data_cadastro'][:10] if pessoa['data_cadastro'] else 'N/A'
            texto += f"{i}. `{tel_oculto}`\n"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data='menu_logado')],
        [InlineKeyboardButton("❌ Sair (Voltar ao Login)", callback_data='voltar_inicio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        texto,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )