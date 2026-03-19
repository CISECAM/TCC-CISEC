from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import validar_login, hospede_existe

MENU_LOGADO = 1

async def iniciar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia fluxo de login"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if not hospede_existe(user_id):
        await query.edit_message_text(
            "❌ Você não está cadastrado.\n\n"
            "Use /start e clique em Check-in para se cadastrar."
        )
        return ConversationHandler.END
    
    await query.edit_message_text("🔐 Digite sua senha:")
    context.user_data['aguardando_senha'] = True
    return MENU_LOGADO

async def verificar_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica senha e mostra menu do hotel"""
    if not context.user_data.get('aguardando_senha'):
        return None
    
    senha = update.message.text
    user_id = update.effective_user.id
    
    if validar_login(user_id, senha):
        context.user_data['aguardando_senha'] = False
        
        hospede = get_hospede(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🛎️ Serviços do Hotel", callback_data='servicos')],
            [InlineKeyboardButton("🛏️ Meu Quarto", callback_data='meu_quarto')],
            [InlineKeyboardButton("👥 Hóspedes", callback_data='hospedes')],
            [InlineKeyboardButton("🔍 Buscar", callback_data='buscar')],
            [InlineKeyboardButton("❌ Sair (Logout)", callback_data='voltar_inicio')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ *Bem-vindo, {hospede['nome']}!*\n\n"
            f"Quarto: *{hospede['quarto']}*\n\n"
            f"O que deseja?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ Senha incorreta. Tente novamente ou use /start."
        )
        return MENU_LOGADO

async def cancelar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Login cancelado.")
    return ConversationHandler.END