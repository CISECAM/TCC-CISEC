from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_todos_hospedes

async def mostrar_hospedes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra lista de hóspedes (apenas números e quartos)"""
    query = update.callback_query
    await query.answer()
    
    hospedes = get_todos_hospedes()
    
    if not hospedes:
        texto = "👥 *Hóspedes*\n\n_Nenhum hóspede cadastrado ainda._"
    else:
        texto = f"👥 *Hóspedes do Hotel*\n\n"
        texto += f"Total: {len(hospedes)} hóspede(s)\n\n"
        texto += "📱 *Contatos cadastrados:*\n\n"
        
        for i, (telefone, quarto) in enumerate(hospedes, 1):
            # Oculta parte do telefone
            if len(telefone) > 4:
                tel_oculto = "*" * (len(telefone)-4) + telefone[-4:]
            else:
                tel_oculto = telefone
            
            texto += f"{i}. Quarto {quarto} - `{tel_oculto}`\n"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data='menu_logado')],
        [InlineKeyboardButton("❌ Sair", callback_data='voltar_inicio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        texto,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )