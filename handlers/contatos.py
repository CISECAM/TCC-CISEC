from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import listar_categorias, listar_contatos_por_categoria, buscar_contatos


def formatar_contato(contato):
    """Formata contato para exibição"""
    texto = f"*{contato['nome_profissional']}*\n"
    texto += f"📞 {contato['telefone']}\n"
    
    if contato['whatsapp']:
        link_wa = f"https://wa.me/55{contato['whatsapp'].replace('-', '').replace(' ', '')}"
        texto += f"💬 [Abrir WhatsApp]({link_wa})\n"
    
    if contato['endereco']:
        texto += f"📍 {contato['endereco']}\n"
    
    if contato['descricao']:
        texto += f"📝 {contato['descricao']}\n"
    
    return texto


async def mostrar_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra botões de categorias"""
    query = update.callback_query
    await query.answer()
    
    categorias = listar_categorias()
    
    keyboard = [[InlineKeyboardButton(cat, callback_data=f'cat_{cat}')] for cat in categorias]
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data='start')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📞 *Escolha uma categoria:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def mostrar_contatos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra contatos da categoria selecionada"""
    query = update.callback_query
    await query.answer()
    
    categoria = query.data.replace('cat_', '')
    contatos = listar_contatos_por_categoria(categoria)
    
    if not contatos:
        await query.edit_message_text("❌ Nenhum contato encontrado.")
        return
    
    texto = f"📞 *{categoria}*\n\n"
    for contato in contatos:
        texto += formatar_contato(contato) + "\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data='contatos')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        texto,
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


async def iniciar_busca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia busca por termo"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔍 Digite o nome do profissional ou serviço:")
    context.user_data['aguardando_busca'] = True


async def realizar_busca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Realiza busca no banco"""
    if not context.user_data.get('aguardando_busca'):
        return
    
    termo = update.message.text
    contatos = buscar_contatos(termo)
    
    if not contatos:
        await update.message.reply_text(f"❌ Nenhum resultado para '{termo}'")
    else:
        texto = f"🔍 *Resultados para '{termo}':*\n\n"
        for contato in contatos:
            texto += formatar_contato(contato) + "\n"
        
        await update.message.reply_text(texto, parse_mode='Markdown', disable_web_page_preview=True)
    
    context.user_data['aguardando_busca'] = False