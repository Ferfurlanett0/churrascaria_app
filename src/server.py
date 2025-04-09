from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
import sys

# CAMINHOS ABSOLUTOS (AJUSTE ESTE VALOR COM O CAMINHO COMPLETO QUE VOCÊ ME ENVIOU)
PROJECT_ROOT = r"D:\Arquivos de Usuario\Documents\DEV\churrascaria_app"

# Configuração de caminhos
def get_template_dir():
    """Retorna o diretório de templates correto"""
    if getattr(sys, 'frozen', False):
        # Modo PyInstaller
        return os.path.join(sys._MEIPASS, 'src', 'templates')
    else:
        # Modo desenvolvimento
        return os.path.join(PROJECT_ROOT, 'src', 'templates')

def get_static_dir():
    """Retorna o diretório static correto"""
    if getattr(sys, 'frozen', False):
        # Modo PyInstaller
        return os.path.join(sys._MEIPASS, 'src', 'static')
    else:
        # Modo desenvolvimento
        return os.path.join(PROJECT_ROOT, 'src', 'static')

TEMPLATE_DIR = get_template_dir()
STATIC_DIR = get_static_dir()

app = Flask(__name__,
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)

# Verificação de caminhos (DEBUG IMPORTANTE)
print("\n" + "="*70)
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"TEMPLATE_DIR: {TEMPLATE_DIR}")
print(f"STATIC_DIR: {STATIC_DIR}")
print("="*70 + "\n")

# Verifica se os diretórios existem
if not os.path.exists(TEMPLATE_DIR):
    print(f"ERRO: Pasta de templates não encontrada em {TEMPLATE_DIR}")
if not os.path.exists(STATIC_DIR):
    print(f"AVISO: Pasta static não encontrada em {STATIC_DIR}")

# Dados do cardápio (mantido igual)
CARDAPIO = [
    {"id": 1, "nome": "Almoço Executivo", "preco": 25.00, "categoria": "refeicao"},
    {"id": 2, "nome": "Almoço Premium", "preco": 35.00, "categoria": "refeicao"},
    {"id": 3, "nome": "Bebida", "preco": 5.00, "categoria": "bebida"},
    {"id": 4, "nome": "Sobremesa", "preco": 8.00, "categoria": "sobremesa"}
]

pedido_atual = []

@app.route('/')
def home():
    """Rota principal com verificação EXTRA de template"""
    template_path = os.path.join(TEMPLATE_DIR, 'index.html')
    
    if not os.path.exists(template_path):
        error_msg = f"""
        <h1>ERRO CRÍTICO: Template não encontrado</h1>
        <p><strong>Sistema procurou em:</strong> <code>{template_path}</code></p>
        <p><strong>Estrutura esperada:</strong></p>
        <pre>
        {PROJECT_ROOT}/
        └── src/
            ├── templates/
            │   └── index.html
            ├── static/
            ├── app.py
            └── server.py
        </pre>
        <p><strong>Verifique:</strong></p>
        <ol>
            <li>Se o arquivo index.html existe na pasta templates</li>
            <li>Se o nome do arquivo está correto (sem erros de capitalização)</li>
            <li>Se a estrutura de pastas está exatamente como acima</li>
        </ol>
        """
        return error_msg, 500
    
    return render_template('index.html')

@app.route('/api/cardapio')
def get_cardapio():
    return jsonify(CARDAPIO)

@app.route('/api/pedido', methods=['GET', 'POST'])
def gerenciar_pedido():
    global pedido_atual
    
    if request.method == 'POST':
        data = request.get_json()
        item_id = data.get('item_id')
        acao = data.get('acao')
        
        item = next((i for i in CARDAPIO if i['id'] == item_id), None)
        
        if acao == 'adicionar':
            pedido_atual.append(item)
        elif acao == 'remover':
            if item in pedido_atual:
                pedido_atual.remove(item)
        
        return jsonify({"success": True})
    
    return jsonify(pedido_atual)

@app.route('/api/emitir-comprovante', methods=['POST'])
def emitir_comprovante():
    global pedido_atual
    data = request.get_json()
    
    # Gera o comprovante
    comprovante = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "itens": pedido_atual,
        "total": sum(item['preco'] for item in pedido_atual),
        "cliente": data.get('cliente', {})
    }
    
    # Limpa o pedido
    pedido_atual = []
    
    return jsonify(comprovante)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)