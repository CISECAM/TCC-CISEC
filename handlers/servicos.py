from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import listar_categorias_servicos, listar_servicos_por_categoria, buscar_servicos

def formatar_servico(servico):
    """Formata serviço para exibição"""
    texto = f"*{servico['nome_servico']}*\n"
    texto += f"📞 Ramal: {servico['telefone']}\n"
    
    if servico['whatsapp']:
        link_wa = f"https://wa.me/55{servico['whatsapp'].replace('-', '').replace(' ', '')}"
        texto += f"💬 [WhatsApp]({link_wa})\n"
    
    if servico['descricao']:
        texto += f"📝 {servico['descricao']}\n"
    
    if servico['horario_funcionamento']:
        texto += f"🕐 {servico['horario_funcionamento']}\n"
    
    return texto

async def mostrar_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra categorias de serviços do hotel"""
    query = update.callback_query
    await query.answer()
    
    categorias = listar_categorias_servicos()
    
    keyboard = [[InlineKeyboardButton(cat, callback_data=f'serv_{cat}')] for cat in categorias]
    keyboard.append([InlineKeyboardButton("🔙 Voltar ao Menu", callback_data='menu_logado')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🛎️ *Serviços do Hotel*\n\nEscolha uma categoria:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def mostrar_servicos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra serviços da categoria"""
    query = update.callback_query
    await query.answer()
    
    categoria = query.data.replace('serv_', '')
    servicos = listar_servicos_por_categoria(categoria)
    
    if not servicos:
        await query.edit_message_text("❌ Nenhum serviço disponível.")
        return
    
    texto = f"🛎️ *{categoria}*\n\n"
    for servico in servicos:
        texto += formatar_servico(servico) + "\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data='servicos')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        texto,
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def iniciar_busca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia busca"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔍 Digite o nome do serviço:")
    context.user_data['aguardando_busca'] = True

async def realizar_busca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Realiza busca"""
    if not context.user_data.get('aguardando_busca'):
        return
    
    termo = update.message.text
    servicos = buscar_servicos(termo)
    
    if not servicos:
        await update.message.reply_text(f"❌ Nenhum serviço encontrado para '{termo}'")
    else:
        texto = f"🔍 *Resultados para '{termo}':*\n\n"
        for servico in servicos:
            texto += formatar_servico(servico) + "\n"
        
        await update.message.reply_text(texto, parse_mode='Markdown', disable_web_page_preview=True)
    
    context.user_data['aguardando_busca'] = False

async def meu_quarto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra info do quarto do hóspede"""
    query = update.callback_query
    await query.answer()
    
    from database.db import get_hospede
    hospede = get_hospede(update.effective_user.id)
    
    texto = (
        f"🛏️ *Meu Quarto*\n\n"
        f"Número: *{hospede['quarto']}*\n"
        f"Hóspede: {hospede['nome']}\n"
        f"Check-in: {hospede['data_checkin'][:10]}\n\n"
        f"Para solicitar serviços, use o menu principal."
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data='menu_logado')],
        [InlineKeyboardButton("❌ Sair", callback_data='voltar_inicio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(texto, reply_markup=reply_markup, parse_mode='Markdown')

async def menu_logado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Volta ao menu logado"""
    query = update.callback_query
    await query.answer()
    
    from database.db import get_hospede
    hospede = get_hospede(update.effective_user.id)
    
    keyboard = [
        [InlineKeyboardButton("🛎️ Serviços do Hotel", callback_data='servicos')],
        [InlineKeyboardButton("🛏️ Meu Quarto", callback_data='meu_quarto')],
        [InlineKeyboardButton("👥 Hóspedes", callback_data='hospedes')],
        [InlineKeyboardButton("🔍 Buscar", callback_data='buscar')],
        [InlineKeyboardButton("❌ Sair (Logout)", callback_data='voltar_inicio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"O que deseja, {hospede['nome']}?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )