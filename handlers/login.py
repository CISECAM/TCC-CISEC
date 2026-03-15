from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import validar_login, usuario_existe

# Estados
MENU_LOGADO = 1

async def iniciar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia fluxo de login"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if not usuario_existe(user_id):
        await query.edit_message_text(
            "❌ Você não está cadastrado.\n\n"
            "Use /start e clique em Cadastrar primeiro."
        )
        return ConversationHandler.END
    
    await query.edit_message_text("🔐 Digite sua senha:")
    context.user_data['aguardando_senha'] = True
    return MENU_LOGADO

async def verificar_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica senha e mostra menu logado"""
    if not context.user_data.get('aguardando_senha'):
        return None  
        
    senha = update.message.text
    user_id = update.effective_user.id
    
    if validar_login(user_id, senha):
        
        #=================================#
        # Remove flag de aguardando senha #
        #=================================#

        context.user_data['aguardando_senha'] = False
        
        #=============================================#
        # Menu após login com as 4 opções solicitadas #
        #=============================================#

        keyboard = [
            [InlineKeyboardButton("🛠️ Faz Tudo", callback_data='faz_tudo')],
            [InlineKeyboardButton("👥 Pessoas Cadastradas", callback_data='pessoas')],
            [InlineKeyboardButton("📞 Contatos de Emergência", callback_data='contatos')],
            [InlineKeyboardButton("🔍 Buscar", callback_data='buscar')],
            [InlineKeyboardButton("❌ Sair (Voltar ao Login)", callback_data='voltar_inicio')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ *Login realizado com sucesso!*\n\n"
            "O que você deseja fazer?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ Senha incorreta. Tente novamente ou use /start para voltar."
        )
        return MENU_LOGADO

async def cancelar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela login e volta ao início"""
    await update.message.reply_text("Login cancelado. Use /start para voltar.")
    return ConversationHandler.END