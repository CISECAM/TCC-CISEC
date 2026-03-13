from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import usuario_existe, get_usuario


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu principal do bot"""
    user = update.effective_user
    
    # Verifica se está logado
    esta_logado = usuario_existe(user.id)
    
    # Botões do menu
    keyboard = [
        [InlineKeyboardButton("📋 Cadastrar", callback_data='cadastro')],
        [InlineKeyboardButton("🔐 Login", callback_data='login')],
    ]
    
    if esta_logado:
        keyboard.append([InlineKeyboardButton("📞 Ver Contatos", callback_data='contatos')])
        keyboard.append([InlineKeyboardButton("🔍 Buscar", callback_data='buscar')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if esta_logado:
        usuario = get_usuario(user.id)
        mensagem = f"👋 Olá, {usuario['nome']}!\n\nBem-vindo ao *CISEC* - Guia de Emergências do seu bairro."
    else:
        mensagem = f"👋 Olá, {user.first_name}!\n\nBem-vindo ao *CISEC* - Guia de Emergências do seu bairro.\n\nCadastre-se ou faça login para acessar os contatos."
    
    await update.message.reply_text(
        mensagem,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )