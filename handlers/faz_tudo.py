from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_connection

def get_servicos_faz_tudo():
    """Busca serviços do tipo 'Faz Tudo' ou 'Serviços' do banco"""
    conn = get_connection()
    cursor = conn.cursor()
    
    #====================================================================#
    # Busca na tabela de contatos onde categoria é 'Serviços' ou similar #
    #====================================================================#

    cursor.execute("""
        SELECT nome_profissional, telefone, whatsapp, descricao 
        FROM contatos 
        WHERE categoria = 'Serviços' 
        ORDER BY nome_profissional
    """)
    
    servicos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return servicos

async def mostrar_faz_tudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra lista de Faz Tudo"""
    query = update.callback_query
    await query.answer()
    
    servicos = get_servicos_faz_tudo()
    
    if not servicos:
        texto = "🛠️ *Faz Tudo*\n\n_Nenhum serviço cadastrado ainda._"
    else:
        texto = "🛠️ *Lista de Faz Tudo - Serviços do Bairro*\n\n"
        
        for servico in servicos:
            texto += f"*{servico['nome_profissional']}*\n"
            texto += f"📞 {servico['telefone']}\n"
            if servico['whatsapp']:
                link_wa = f"https://wa.me/55{servico['whatsapp'].replace('-', '').replace(' ', '')}"
                texto += f"💬 [WhatsApp]({link_wa})\n"
            if servico['descricao']:
                texto += f"📝 {servico['descricao']}\n"
            texto += "\n"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data='menu_logado')],
        [InlineKeyboardButton("❌ Sair (Voltar ao Login)", callback_data='voltar_inicio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        texto,
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def menu_logado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Volta ao menu logado"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🛠️ Faz Tudo", callback_data='faz_tudo')],
        [InlineKeyboardButton("👥 Pessoas Cadastradas", callback_data='pessoas')],
        [InlineKeyboardButton("📞 Contatos de Emergência", callback_data='contatos')],
        [InlineKeyboardButton("🔍 Buscar", callback_data='buscar')],
        [InlineKeyboardButton("❌ Sair (Voltar ao Login)", callback_data='voltar_inicio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "O que você deseja fazer?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )