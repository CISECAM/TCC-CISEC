from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import cadastrar_hospede, hospede_existe, validar_chave_acesso

# Estados da conversa
CHAVE_ACESSO, NOME, TELEFONE, QUARTO, SENHA = range(5)

async def iniciar_cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia fluxo de cadastro com chave de acesso"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if hospede_existe(user_id):
        await query.edit_message_text("❌ Você já está cadastrado neste hotel!")
        return ConversationHandler.END

    await query.edit_message_text(
        "🏨 *Bem-vindo ao Hotel!*\n\n"
        "Para se cadastrar, digite sua *Chave de Acesso*:\n"
        "_(Fornecida na recepção)_",
        parse_mode='Markdown'
    )
    return CHAVE_ACESSO

async def receber_chave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Valida chave de acesso"""
    chave = update.message.text.strip()
    
    if not validar_chave_acesso(chave):
        await update.message.reply_text(
            "❌ *Chave inválida ou já utilizada!*\n\n"
            "Verifique com a recepção ou tente novamente:",
            parse_mode='Markdown'
        )
        return CHAVE_ACESSO
    
    # Chave válida, salva e continua
    context.user_data['chave_acesso'] = chave
    await update.message.reply_text("✅ Chave válida!\n\nQual seu nome completo?")
    return NOME

async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nome'] = update.message.text
    await update.message.reply_text("📱 Qual seu telefone? (Ex: 11999998888)")
    return TELEFONE

async def receber_telefone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['telefone'] = update.message.text
    await update.message.reply_text("🚪 Qual o número do seu quarto? (Ex: 205)")
    return QUARTO

async def receber_quarto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['quarto'] = update.message.text
    await update.message.reply_text("🔑 Crie uma senha para acessar o app (mínimo 6 caracteres):")
    return SENHA

async def receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    senha = update.message.text
    user_id = update.effective_user.id

    if len(senha) < 6:
        await update.message.reply_text("❌ Senha muito curta. Digite novamente (mínimo 6 caracteres):")
        return SENHA

    # Cadastra no banco
    sucesso = cadastrar_hospede(
        telegram_id=user_id,
        nome=context.user_data['nome'],
        telefone=context.user_data['telefone'],
        quarto=context.user_data['quarto'],
        senha=senha,
        chave_acesso=context.user_data['chave_acesso']
    )

    if sucesso:
        await update.message.reply_text(
            "✅ *Check-in realizado com sucesso!*\n\n"
            f"Quarto: {context.user_data['quarto']}\n"
            "Use /start para acessar os serviços do hotel.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Erro no cadastro. Tente novamente.")

    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cadastro cancelado.")
    return ConversationHandler.END