import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)

# Importa do banco
from database.db import init_db

# Importa handlers
from handlers.start import start
from handlers.cadastro import (
    iniciar_cadastro, receber_nome, receber_telefone,
    receber_cep, receber_senha, cancelar, NOME, TELEFONE, CEP, SENHA
)
from handlers.login import iniciar_login, verificar_senha
from handlers.contatos import (
    mostrar_categorias, mostrar_contatos, iniciar_busca, realizar_busca
)

# Carrega .env
load_dotenv()

# Configura logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Pega token
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN não encontrado no .env")

# Inicializa banco
init_db()


async def voltar_start(update: Update, context):
    """Volta ao menu principal"""
    query = update.callback_query
    await query.answer()
    await start(update, context)


def main():
    """Inicia o bot"""
    app = Application.builder().token(TOKEN).build()
    
    # Handler de cadastro (conversa em etapas)
    cadastro_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(iniciar_cadastro, pattern='^cadastro$')],
        states={
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)],
            TELEFONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_telefone)],
            CEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_cep)],
            SENHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_senha)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    )
    
    # Registra handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(cadastro_handler)
    app.add_handler(CallbackQueryHandler(iniciar_login, pattern='^login$'))
    app.add_handler(CallbackQueryHandler(mostrar_categorias, pattern='^contatos$'))
    app.add_handler(CallbackQueryHandler(mostrar_contatos, pattern='^cat_'))
    app.add_handler(CallbackQueryHandler(iniciar_busca, pattern='^buscar$'))
    app.add_handler(CallbackQueryHandler(voltar_start, pattern='^start$'))
    
    # Handlers de mensagens (login e busca)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_senha))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, realizar_busca))
    
    print("Bot CISEC iniciado! Pressione Ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()