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
from handlers.start import start, voltar_inicio
from handlers.cadastro import (
    iniciar_cadastro, receber_nome, receber_telefone,
    receber_cep, receber_senha, cancelar, NOME, TELEFONE, CEP, SENHA
)
from handlers.login import (
    iniciar_login, verificar_senha, cancelar_login, MENU_LOGADO
)
from handlers.contatos import (
    mostrar_categorias, mostrar_contatos, iniciar_busca, realizar_busca
)
from handlers.faz_tudo import mostrar_faz_tudo, menu_logado
from handlers.pessoas import mostrar_pessoas

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

    # Handler de login (conversa em etapas)
    login_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(iniciar_login, pattern='^login$')],
        states={
            MENU_LOGADO: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_senha)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar_login)],
    )

    # Registra handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(cadastro_handler)
    app.add_handler(login_handler)
    
    # Handlers de callback (botões)
    app.add_handler(CallbackQueryHandler(mostrar_categorias, pattern='^contatos$'))
    app.add_handler(CallbackQueryHandler(mostrar_contatos, pattern='^cat_'))
    app.add_handler(CallbackQueryHandler(iniciar_busca, pattern='^buscar$'))
    app.add_handler(CallbackQueryHandler(voltar_inicio, pattern='^voltar_inicio$'))
    app.add_handler(CallbackQueryHandler(mostrar_faz_tudo, pattern='^faz_tudo$'))
    app.add_handler(CallbackQueryHandler(mostrar_pessoas, pattern='^pessoas$'))
    app.add_handler(CallbackQueryHandler(menu_logado, pattern='^menu_logado$'))

    # Handlers de mensagens 
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, realizar_busca))

    print("Bot CISEC iniciado! Pressione Ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()