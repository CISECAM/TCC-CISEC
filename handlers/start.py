from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import hospede_existe, get_hospede

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tela inicial do Hotel"""
    user = update.effective_user
    
    # Limpa dados de sessão anteriores
    context.user_data.clear()
    
    # SEMPRE mostra apenas Login e Cadastro na tela inicial
    keyboard = [
        [InlineKeyboardButton("🔐 Login", callback_data='login')],
        [InlineKeyboardButton("📝 Check-in (Cadastrar)", callback_data='cadastro')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    mensagem = (
        f"🏨 *Bem-vindo ao Hotel!*\n\n"
        f"Olá, {user.first_name}!\n\n"
        f"🔐 Já é hóspede? Faça *Login*\n"
        f"📝 Novo hóspede? Faça *Check-in*"
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            mensagem,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            mensagem,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def voltar_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Volta para tela inicial"""
    query = update.callback_query
    await query.answer()
    await start(update, context)