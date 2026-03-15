from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import cadastrar_usuario, usuario_existe

# Estados da conversa
NOME, TELEFONE, CEP, SENHA = range(4)

async def iniciar_cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia fluxo de cadastro"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if usuario_existe(user_id):
        await query.edit_message_text("❌ Você já está cadastrado!")
        return ConversationHandler.END

    await query.edit_message_text("📋 *Cadastro*\n\nQual seu nome completo?", parse_mode='Markdown')
    return NOME

async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nome'] = update.message.text
    await update.message.reply_text("📱 Qual seu telefone? (Ex: 11999998888)")
    return TELEFONE

async def receber_telefone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['telefone'] = update.message.text
    await update.message.reply_text("📍 Qual seu CEP? (Ex: 01001000)")
    return CEP

async def receber_cep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cep'] = update.message.text
    await update.message.reply_text("🔑 Crie uma senha (mínimo 6 caracteres):")
    return SENHA

async def receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    senha = update.message.text
    user_id = update.effective_user.id

    if len(senha) < 6:
        await update.message.reply_text("❌ Senha muito curta. Digite novamente (mínimo 6 caracteres):")
        return SENHA

    # Cadastra no banco
    sucesso = cadastrar_usuario(
        telegram_id=user_id,
        nome=context.user_data['nome'],
        telefone=context.user_data['telefone'],
        cep=context.user_data['cep'],
        senha=senha
    )

    if sucesso:
        await update.message.reply_text(
            "✅ *Cadastro realizado com sucesso!*\n\n"
            "Use /start para acessar o menu.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Erro no cadastro. Tente novamente.")

    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cadastro cancelado.")
    return ConversationHandler.END