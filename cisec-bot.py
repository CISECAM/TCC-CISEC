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
    iniciar_cadastro, receber_chave, receber_nome, receber_telefone,
    receber_quarto, receber_senha, cancelar, 
    CHAVE_ACESSO, NOME, TELEFONE, QUARTO, SENHA
)
from handlers.login import (
    iniciar_login, verificar_senha, cancelar_login, MENU_LOGADO
)
from handlers.servicos import (
    mostrar_categorias, mostrar_servicos, iniciar_busca, 
    realizar_busca, meu_quarto, menu_logado
)
from handlers.hospedes import mostrar_hospedes

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
    """Inicia o bot do Hotel"""
    app = Application.builder().token(TOKEN).build()

    # Handler de cadastro (com chave de acesso)
    cadastro_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(iniciar_cadastro, pattern='^cadastro$')],
        states={
            CHAVE_ACESSO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_chave)],
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)],
            TELEFONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_telefone)],
            QUARTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_quarto)],
            SENHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_senha)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    )

    # Handler de login
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
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(mostrar_categorias, pattern='^servicos$'))
    app.add_handler(CallbackQueryHandler(mostrar_servicos, pattern='^serv_'))
    app.add_handler(CallbackQueryHandler(iniciar_busca, pattern='^buscar$'))
    app.add_handler(CallbackQueryHandler(voltar_inicio, pattern='^voltar_inicio$'))
    app.add_handler(CallbackQueryHandler(meu_quarto, pattern='^meu_quarto$'))
    app.add_handler(CallbackQueryHandler(mostrar_hospedes, pattern='^hospedes$'))
    app.add_handler(CallbackQueryHandler(menu_logado, pattern='^menu_logado$'))

    # Mensagens
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, realizar_busca))

    print("🏨 Bot do Hotel iniciado! Pressione Ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()