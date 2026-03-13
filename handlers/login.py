from telegram import Update
from telegram.ext import ContextTypes
from database.db import validar_login, usuario_existe


async def iniciar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia fluxo de login"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if not usuario_existe(user_id):
        await query.edit_message_text("❌ Você não está cadastrado. Use /start e clique em Cadastrar.")
        return
    
    await query.edit_message_text("🔐 Digite sua senha:")
    context.user_data['aguardando_senha'] = True


async def verificar_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica senha do login"""
    if not context.user_data.get('aguardando_senha'):
        return
    
    senha = update.message.text
    user_id = update.effective_user.id
    
    if validar_login(user_id, senha):
        await update.message.reply_text(
            "✅ *Login realizado!*\n\n"
            "Use /start para ver os contatos de emergência."
        )
    else:
        await update.message.reply_text("❌ Senha incorreta. Tente novamente ou use /start.")
    
    context.user_data['aguardando_senha'] = False