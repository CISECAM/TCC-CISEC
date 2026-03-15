from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import usuario_existe, get_usuario

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tela inicial - Apenas Login e Cadastro"""
    user = update.effective_user
    
    #==================================#
    # Limpa dados de sessão anteriores #
    #==================================#
    context.user_data.clear()

    #=======================================================#
    # SEMPRE mostra apenas Login e Cadastro na tela inicial #
    #=======================================================#
    
    keyboard = [
        [InlineKeyboardButton("🔐 Login", callback_data='login')],
        [InlineKeyboardButton("📝 Cadastrar", callback_data='cadastro')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    mensagem = (
        f"👋 Olá, {user.first_name}!\n\n"
        f"Bem-vindo ao *CISEC* - Guia de Emergências do seu bairro.\n\n"
        f"🔐 Já tem cadastro? Faça *Login*\n"
        f"📝 Novo aqui? *Cadastre-se*"
    )
    
    #=============================================#
    # Se veio de callback (botão), edita mensagem #
    #=============================================#

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            mensagem,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:

        #================================================#
        # Se veio de comando /start, envia nova mensagem #
        #================================================#
        
        await update.message.reply_text(
            mensagem,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def voltar_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Volta para tela inicial de login/cadastro"""
    query = update.callback_query
    await query.answer()
    await start(update, context)