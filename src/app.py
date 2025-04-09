import webview
import json
import os
import tempfile
import win32print
import win32api
import re
import sys
import base64
from datetime import datetime

class ChurrascariaApp:
    def __init__(self):
        # Dados do cardápio
        self.cardapio = {
            "refeicoes": [
                {"id": 1, "nome": "Almoço Executivo", "preco": 25.00, "categoria": "refeicao"},
                {"id": 2, "nome": "Almoço Premium", "preco": 35.00, "categoria": "refeicao"},
                {"id": 3, "nome": "Almoço Vegetariano", "preco": 22.00, "categoria": "refeicao"}
            ],
            "bebidas": [
                {"id": 4, "nome": "Refrigerante", "preco": 5.00, "categoria": "bebida"},
                {"id": 5, "nome": "Cerveja", "preco": 7.00, "categoria": "bebida"}
            ],
            "sobremesas": [
                {"id": 6, "nome": "Pudim", "preco": 8.00, "categoria": "sobremesa"},
                {"id": 7, "nome": "Sorvete", "preco": 6.00, "categoria": "sobremesa"}
            ]
        }
        
        # Variáveis de estado
        self.pedido_atual = []
        self.cpf_cnpj = ""
        self.comprovante = ""
        
        # Informações sobre o sistema
        self.sobre_info = {
            "versao": "2.3",
            "desenvolvedor": "Churrascaria Sabor Gaúcho LTDA",
            "cnpj": "12.345.678/0001-99",
            "contato": "contato@churrascaria.com.br",
            "telefone": "(51) 1234-5678",
            "github": "https://github.com/seu-usuario"
        }
        
        self.historico_versoes = [
            "v2.3 (15/09/2023) - Adicionado controle de quantidade por item",
            "v2.2 (15/08/2023) - Adicionada interface moderna",
            "v2.1 (15/07/2023) - Adicionado campo CPF/CNPJ",
            "v2.0 (10/07/2023) - Sistema de impressão direta",
            "v1.0 (01/06/2023) - Versão inicial"
        ]

        # Configuração de caminhos
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Cria a janela principal
        self.window = webview.create_window(
            'Sistema Churrascaria',
            html=self.get_html(),
            width=1300,
            height=900,
            resizable=True,
            text_select=True,
            confirm_close=True
        )
        
        # Expõe funções Python para o JavaScript
        self.window.expose(
            self.adicionar_item,
            self.remover_item,
            self.finalizar_pedido,
            self.validar_cpf_cnpj,
            self.adicionar_item_personalizado,
            self.mostrar_sobre,
            self.get_pedido_atual,
            self.imprimir_comprovante,
            self.salvar_comprovante,
            self.atualizar_quantidade
        )

    def get_html(self):
        """Retorna o HTML completo da aplicação"""
        try:
            return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Churrascaria</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{
            --primary: #d9534f;
            --secondary: #5bc0de;
        }}
        body {{
            background-color: #f8f9fa;
            font-family: 'Segoe UI', sans-serif;
        }}
        .card-item {{
            transition: transform 0.2s;
            cursor: pointer;
        }}
        .card-item:hover {{
            transform: scale(1.03);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .bg-churrasco {{
            background-color: var(--primary);
            color: white;
        }}
        .badge-categoria {{
            position: absolute;
            top: 10px;
            right: 10px;
        }}
        .item-personalizado {{
            background-color: #f8f9fa;
            border-left: 4px solid var(--secondary);
        }}
        .modal-about {{
            max-width: 800px;
        }}
        .github-btn {{
            background-color: #333;
            color: white;
            border: none;
        }}
        .github-btn:hover {{
            background-color: #555;
            color: white;
        }}
        .quantidade-input {{
            width: 50px;
            text-align: center;
        }}
        .btn-quantidade {{
            width: 30px;
            padding: 0;
        }}
        .item-pedido {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }}
        .item-info {{
            flex-grow: 1;
        }}
        .item-controles {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .item-valor {{
            min-width: 80px;
            text-align: right;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg bg-churrasco mb-4">
        <div class="container">
            <a class="navbar-brand" href="#">
                Churrascaria Tempero Gaúcho
            </a>
            <div>
                <button class="btn btn-outline-light me-2" onclick="adicionarItemPersonalizado()">
                    <i class="fas fa-plus-circle"></i> Personalizado
                </button>
                <button class="btn btn-outline-light" onclick="mostrarSobre()">
                    <i class="fas fa-info-circle"></i> Sobre
                </button>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="row">
            <!-- Cardápio -->
            <div class="col-md-8">
                <h2 class="mb-4"><i class="fas fa-book-open me-2"></i>Cardápio</h2>
                
                <ul class="nav nav-tabs mb-4" id="categoryTabs">
                    <li class="nav-item">
                        <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#refeicoes">
                            <i class="fas fa-utensils me-1"></i> Refeições
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#bebidas">
                            <i class="fas fa-glass-whiskey me-1"></i> Bebidas
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#sobremesas">
                            <i class="fas fa-ice-cream me-1"></i> Sobremesas
                        </button>
                    </li>
                </ul>

                <div class="tab-content">
                    <div class="tab-pane fade show active" id="refeicoes">
                        <div class="row row-cols-1 row-cols-md-2 g-4">
                            {self.generate_cardapio_html('refeicoes')}
                        </div>
                    </div>
                    
                    <div class="tab-pane fade" id="bebidas">
                        <div class="row row-cols-1 row-cols-md-2 g-4">
                            {self.generate_cardapio_html('bebidas')}
                        </div>
                    </div>
                    
                    <div class="tab-pane fade" id="sobremesas">
                        <div class="row row-cols-1 row-cols-md-2 g-4">
                            {self.generate_cardapio_html('sobremesas')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pedido -->
            <div class="col-md-4">
                <div class="card sticky-top" style="top: 20px;">
                    <div class="card-header bg-churrasco text-white">
                        <h5 class="mb-0"><i class="fas fa-clipboard-list me-2"></i>Meu Pedido</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">CPF/CNPJ (opcional):</label>
                            <input type="text" class="form-control" id="cpf-cnpj" placeholder="000.000.000-00">
                        </div>
                        
                        <ul class="list-group mb-3" id="lista-pedido">
                            <li class="list-group-item d-flex justify-content-between align-items-center text-muted">
                                Nenhum item selecionado
                            </li>
                        </ul>
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5>Total:</h5>
                            <h5 id="total-pedido">R$ 0,00</h5>
                        </div>
                        <button class="btn btn-danger w-100" onclick="finalizarPedido()">
                            <i class="fas fa-print me-2"></i> Emitir Comprovante
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Sobre -->
    <div class="modal fade" id="sobreModal" tabindex="-1">
        <div class="modal-dialog modal-about">
            <div class="modal-content">
                <div class="modal-header bg-churrasco text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-info-circle me-2"></i>Sobre o Sistema
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="text-center mb-4">
                        <h4>Sistema de Gestão - Churrascaria</h4>
                        <p class="text-muted">Versão {self.sobre_info['versao']}</p>
                    </div>
                    
                    <div class="mb-4">
                        <h5><i class="fas fa-building me-2"></i>Informações</h5>
                        <div class="ps-4">
                            <p><strong>Razão Social:</strong> {self.sobre_info['desenvolvedor']}</p>
                            <p><strong>CNPJ:</strong> {self.sobre_info['cnpj']}</p>
                            <p><strong>Contato:</strong> {self.sobre_info['contato']}</p>
                            <p><strong>Telefone:</strong> {self.sobre_info['telefone']}</p>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <h5><i class="fas fa-history me-2"></i>Histórico de Versões</h5>
                        <ul class="ps-4">
                            {''.join(f'<li>{versao}</li>' for versao in self.historico_versoes)}
                        </ul>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn github-btn" onclick="window.open('{self.sobre_info['github']}', '_blank')">
                        <i class="fab fa-github me-2"></i>GitHub
                    </button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-2"></i>Fechar
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Item Personalizado -->
    <div class="modal fade" id="itemPersonalizadoModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-churrasco text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-plus-circle me-2"></i>Adicionar Item Personalizado
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Nome do Item:</label>
                        <input type="text" class="form-control" id="item-nome">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Preço (R$):</label>
                        <input type="text" class="form-control" id="item-preco" placeholder="00.00">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Quantidade:</label>
                        <input type="number" class="form-control" id="item-quantidade" value="1" min="1">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-2"></i>Cancelar
                    </button>
                    <button type="button" class="btn btn-primary" onclick="confirmarItemPersonalizado()">
                        <i class="fas fa-check me-2"></i>Adicionar
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Verificação se a API está disponível
        function checkAPI() {{
            if (typeof pywebview === 'undefined' || !pywebview.api) {{
                document.body.innerHTML = `
                    <div class="container mt-5">
                        <div class="alert alert-danger">
                            <h4>Erro: API não disponível</h4>
                            <p>A aplicação não conseguiu se comunicar com o backend.</p>
                            <button onclick="window.location.reload()" class="btn btn-warning">
                                <i class="fas fa-sync-alt"></i> Recarregar
                            </button>
                        </div>
                    </div>
                `;
                return false;
            }}
            return true;
        }}

        // Funções para o pedido
        function adicionarItem(id) {{
            if (!checkAPI()) return;
            
            // Verifica se o item já está no pedido
            pywebview.api.get_pedido_atual().then(data => {{
                const itemExistente = data.itens.findIndex(item => item.item.id === id);
                if (itemExistente >= 0) {{
                    // Se já existe, aumenta a quantidade
                    pywebview.api.atualizar_quantidade(itemExistente, 1).then(() => {{
                        atualizarPedido();
                    }});
                }} else {{
                    // Se não existe, adiciona novo item com quantidade 1
                    pywebview.api.adicionar_item(id).then(() => {{
                        atualizarPedido();
                    }});
                }}
            }}).catch(err => {{
                console.error('Erro ao adicionar item:', err);
            }});
        }}
        
        function removerItem(index) {{
            if (!checkAPI()) return;
            
            pywebview.api.remover_item(index).then(() => {{
                atualizarPedido();
            }}).catch(err => {{
                console.error('Erro ao remover item:', err);
            }});
        }}
        
        function atualizarQuantidade(index, delta) {{
            if (!checkAPI()) return;
            
            pywebview.api.atualizar_quantidade(index, delta).then(() => {{
                atualizarPedido();
            }}).catch(err => {{
                console.error('Erro ao atualizar quantidade:', err);
            }});
        }}
        
        function atualizarPedido() {{
            if (!checkAPI()) return;
            
            pywebview.api.get_pedido_atual().then(data => {{
                const lista = document.getElementById('lista-pedido');
                const totalElement = document.getElementById('total-pedido');
                
                lista.innerHTML = '';
                
                if (data.itens.length === 0) {{
                    lista.innerHTML = '<li class="list-group-item text-muted">Nenhum item selecionado</li>';
                    totalElement.textContent = 'R$ 0,00';
                    return;
                }}
                
                data.itens.forEach((pedido, index) => {{
                    const item = pedido.item;
                    const li = document.createElement('li');
                    li.className = 'list-group-item ' + 
                                  (item.categoria === 'personalizado' ? 'item-personalizado' : '');
                    
                    li.innerHTML = `
                        <div class="item-pedido">
                            <div class="item-info">
                                <strong>${{item.nome}}</strong>
                                <small class="d-block text-muted">R$ ${{item.preco.toFixed(2)}} (unidade)</small>
                            </div>
                            <div class="item-controles">
                                <div class="input-group input-group-sm">
                                    <button class="btn btn-outline-secondary btn-quantidade" type="button" onclick="atualizarQuantidade(${{index}}, -1)">
                                        <i class="fas fa-minus"></i>
                                    </button>
                                    <input type="text" class="form-control quantidade-input" value="${{pedido.quantidade}}" readonly>
                                    <button class="btn btn-outline-secondary btn-quantidade" type="button" onclick="atualizarQuantidade(${{index}}, 1)">
                                        <i class="fas fa-plus"></i>
                                    </button>
                                </div>
                                <div class="item-valor">
                                    R$ ${{(item.preco * pedido.quantidade).toFixed(2)}}
                                </div>
                                <button class="btn btn-sm btn-outline-danger" onclick="removerItem(${{index}})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        </div>
                    `;
                    lista.appendChild(li);
                }});
                
                totalElement.textContent = `R$ ${{data.total.toFixed(2)}}`;
            }}).catch(err => {{
                console.error('Erro ao atualizar pedido:', err);
            }});
        }}
        
        function validarCPF() {{
            if (!checkAPI()) return;
            
            const cpf = document.getElementById('cpf-cnpj').value;
            pywebview.api.validar_cpf_cnpj(cpf).then(resultado => {{
                if (!resultado.valid) {{
                    alert('CPF/CNPJ inválido! Digite 11 dígitos para CPF ou 14 para CNPJ.');
                }}
            }}).catch(err => {{
                console.error('Erro ao validar CPF/CNPJ:', err);
            }});
        }}
        
        function finalizarPedido() {{
            if (!checkAPI()) return;
            
            const cpf = document.getElementById('cpf-cnpj').value;
            
            pywebview.api.finalizar_pedido(cpf).then(resultado => {{
                if (resultado.success) {{
                    // Mostra opções ao usuário
                    const opcao = confirm('Pedido finalizado!\\nTotal: R$ ' + resultado.total.toFixed(2) + 
                                  '\\n\\nDeseja imprimir o comprovante?\\n(Cancelar para apenas salvar)');
                    
                    if (opcao) {{
                        pywebview.api.imprimir_comprovante().then(res => {{
                            if (!res.success) {{
                                alert(res.message);
                            }}
                        }}).catch(err => {{
                            console.error('Erro ao imprimir:', err);
                        }});
                    }} else {{
                        pywebview.api.salvar_comprovante().then(res => {{
                            if (!res.success) {{
                                alert(res.message);
                            }}
                        }}).catch(err => {{
                            console.error('Erro ao salvar:', err);
                        }});
                    }}
                    
                    document.getElementById('cpf-cnpj').value = '';
                    atualizarPedido();
                }} else {{
                    alert(resultado.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao finalizar pedido:', err);
            }});
        }}
        
        // Funções para o modal Sobre
        function mostrarSobre() {{
            if (!checkAPI()) return;
            
            pywebview.api.mostrar_sobre().then(data => {{
                new bootstrap.Modal(document.getElementById('sobreModal')).show();
            }}).catch(err => {{
                console.error('Erro ao mostrar sobre:', err);
            }});
        }}
        
        // Funções para itens personalizados
        function adicionarItemPersonalizado() {{
            new bootstrap.Modal(document.getElementById('itemPersonalizadoModal')).show();
        }}
        
        function confirmarItemPersonalizado() {{
            if (!checkAPI()) return;
            
            const nome = document.getElementById('item-nome').value.trim();
            const preco = document.getElementById('item-preco').value.trim();
            const quantidade = parseInt(document.getElementById('item-quantidade').value) || 1;
            
            if (!nome) {{
                alert('Digite um nome para o item!');
                return;
            }}
            
            pywebview.api.adicionar_item_personalizado(nome, preco, quantidade).then(resultado => {{
                if (resultado.success) {{
                    document.getElementById('item-nome').value = '';
                    document.getElementById('item-preco').value = '';
                    document.getElementById('item-quantidade').value = '1';
                    bootstrap.Modal.getInstance(document.getElementById('itemPersonalizadoModal')).hide();
                    atualizarPedido();
                }} else {{
                    alert(resultado.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao adicionar item personalizado:', err);
            }});
        }}
        
        // Atualiza o pedido automaticamente
        setInterval(atualizarPedido, 1000);
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {{
            // Verifica se todos os recursos estão carregados
            if (typeof bootstrap !== 'undefined' && typeof pywebview !== 'undefined') {{
                atualizarPedido();
            }} else {{
                setTimeout(function() {{
                    if (typeof bootstrap === 'undefined' || typeof pywebview === 'undefined') {{
                        checkAPI();
                    }} else {{
                        atualizarPedido();
                    }}
                }}, 500);
            }}
        }});
    </script>
</body>
</html>
            """
        except Exception as e:
            print(f"ERRO ao gerar HTML: {str(e)}")
            return f"""
            <!DOCTYPE html>
            <html>
            <body style="padding: 20px; font-family: Arial;">
                <h1 style="color: red;">Erro ao carregar a aplicação</h1>
                <p>{str(e)}</p>
                <button onclick="window.location.reload()">Recarregar</button>
            </body>
            </html>
            """

    def generate_cardapio_html(self, categoria):
        """Gera o HTML dos itens do cardápio"""
        items_html = []
        for item in self.cardapio.get(categoria, []):
            icon = {
                "refeicoes": "fa-utensils",
                "bebidas": "fa-glass-whiskey",
                "sobremesas": "fa-ice-cream"
            }.get(item['categoria'], 'fa-circle')
            
            items_html.append(f"""
            <div class="col">
                <div class="card card-item h-100" onclick="adicionarItem({item['id']})">
                    <div class="card-body position-relative">
                        <span class="badge bg-primary badge-categoria">
                            <i class="fas {icon} me-1"></i>{item['categoria'].capitalize()}
                        </span>
                        <h5 class="card-title">{item['nome']}</h5>
                        <p class="card-text text-muted">R$ {item['preco']:.2f}</p>
                    </div>
                </div>
            </div>
            """)
        return ''.join(items_html)

    def adicionar_item(self, item_id):
        """Adiciona um item ao pedido com quantidade padrão 1"""
        for categoria in self.cardapio.values():
            for item in categoria:
                if item['id'] == item_id:
                    # Verifica se o item já está no pedido
                    for pedido in self.pedido_atual:
                        if pedido['item']['id'] == item_id:
                            pedido['quantidade'] += 1
                            return {"success": True}
                    
                    # Se não estiver, adiciona novo item
                    self.pedido_atual.append({
                        "item": item.copy(),
                        "quantidade": 1
                    })
                    return {"success": True}
        return {"success": False, "message": "Item não encontrado"}

    def atualizar_quantidade(self, index, delta):
        """Atualiza a quantidade de um item no pedido"""
        try:
            if 0 <= index < len(self.pedido_atual):
                self.pedido_atual[index]['quantidade'] += delta
                
                # Remove o item se a quantidade for menor que 1
                if self.pedido_atual[index]['quantidade'] < 1:
                    del self.pedido_atual[index]
                
                return {"success": True}
            return {"success": False, "message": "Índice inválido"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def adicionar_item_personalizado(self, nome, preco, quantidade=1):
        """Adiciona um item personalizado ao pedido"""
        try:
            preco = float(preco)
            quantidade = int(quantidade)
            
            if preco <= 0:
                return {"success": False, "message": "O preço deve ser maior que zero"}
            if quantidade < 1:
                return {"success": False, "message": "A quantidade deve ser pelo menos 1"}
                
            novo_item = {
                "item": {
                    "id": len(self.pedido_atual) + 1000,  # IDs altos para itens personalizados
                    "nome": nome,
                    "preco": preco,
                    "categoria": "personalizado",
                    "descricao": "Item personalizado pelo cliente"
                },
                "quantidade": quantidade
            }
            self.pedido_atual.append(novo_item)
            return {"success": True}
        except ValueError:
            return {"success": False, "message": "Preço ou quantidade inválido. Use números (ex: 15.90)"}

    def remover_item(self, index):
        """Remove um item do pedido"""
        try:
            del self.pedido_atual[index]
            return {"success": True}
        except IndexError:
            return {"success": False, "message": "Índice inválido"}

    def get_pedido_atual(self):
        """Retorna o estado atual do pedido"""
        return {
            "itens": self.pedido_atual,
            "total": sum(item['item']['preco'] * item['quantidade'] for item in self.pedido_atual)
        }

    def validar_cpf_cnpj(self, documento):
        """Valida o CPF/CNPJ"""
        documento = re.sub(r'[^0-9]', '', documento)
        if len(documento) == 11:
            self.cpf_cnpj = f"CPF: {documento[:3]}.{documento[3:6]}.{documento[6:9]}-{documento[9:]}"
            return {"valid": True}
        elif len(documento) == 14:
            self.cpf_cnpj = f"CNPJ: {documento[:2]}.{documento[2:5]}.{documento[5:8]}/{documento[8:12]}-{documento[12:]}"
            return {"valid": True}
        elif documento == "":
            self.cpf_cnpj = ""
            return {"valid": True}
        else:
            return {"valid": False}

    def mostrar_sobre(self):
        """Retorna informações para a tela Sobre"""
        return {
            "versao": self.sobre_info["versao"],
            "desenvolvedor": self.sobre_info["desenvolvedor"],
            "cnpj": self.sobre_info["cnpj"],
            "contato": self.sobre_info["contato"],
            "telefone": self.sobre_info["telefone"],
            "historico": self.historico_versoes,
            "github": self.sobre_info["github"]
        }

    def finalizar_pedido(self, cpf_cnpj=""):
        """Finaliza o pedido e prepara o comprovante"""
        if not self.pedido_atual:
            return {"success": False, "message": "Nenhum item selecionado para emitir comprovante."}
        
        # Valida CPF/CNPJ
        validacao = self.validar_cpf_cnpj(cpf_cnpj)
        if not validacao['valid']:
            return {"success": False, "message": "CPF/CNPJ inválido! Digite 11 dígitos para CPF ou 14 para CNPJ."}
        
        # Calcula o total
        total = sum(item['item']['preco'] * item['quantidade'] for item in self.pedido_atual)
        self.comprovante = self.gerar_comprovante(total)
        
        return {"success": True, "total": total}

    def gerar_comprovante(self, total):
        """Gera o texto do comprovante com as quantidades"""
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        cabecalho = f"CHURRASCARIA SABOR GAÚCHO\nRua dos Sabores, 123\nCNPJ: 12.345.678/0001-99\n{data_hora}\n"
        
        if self.cpf_cnpj:
            cabecalho += f"{self.cpf_cnpj}\n"
        
        cabecalho += "="*40 + "\n"
        
        itens = ""
        for pedido in self.pedido_atual:
            item = pedido['item']
            quantidade = pedido['quantidade']
            subtotal = item['preco'] * quantidade
            itens += f"{quantidade}x {item['nome'].ljust(25)} R$ {item['preco']:6.2f} = R$ {subtotal:7.2f}\n"
        
        rodape = "="*40 + "\n"
        rodape += f"TOTAL{' ' * 35}R$ {total:7.2f}\n"
        rodape += "="*40 + "\n"
        rodape += "Obrigado pela preferência!\n"
        rodape += "Volte sempre!"
        
        return cabecalho + itens + rodape

    def imprimir_comprovante(self):
        """Imprime o comprovante diretamente"""
        try:
            temp_path = os.path.join(tempfile.gettempdir(), "comprovante_churrascaria.txt")
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(self.comprovante)
            
            if self.verificar_impressoras():
                os.startfile(temp_path, "print")
                return {"success": True, "message": "Comprovante enviado para impressão!"}
            else:
                return {"success": False, "message": "Nenhuma impressora encontrada!"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao imprimir: {str(e)}"}

    def salvar_comprovante(self):
        """Salva o comprovante em um arquivo"""
        try:
            temp_path = os.path.join(tempfile.gettempdir(), "comprovante_churrascaria.txt")
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(self.comprovante)
            os.startfile(temp_path)
            return {"success": True, "message": "Comprovante salvo com sucesso!"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao salvar comprovante: {str(e)}"}

    def verificar_impressoras(self):
        """Verifica se há impressoras disponíveis"""
        try:
            impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            return len(impressoras) > 0
        except:
            return False

    def run(self):
        """Inicia a aplicação"""
        try:
            # Verifica se o WebView2 está instalado
            if hasattr(webview, 'util') and hasattr(webview.util, 'is_webview_installed'):
                if not webview.util.is_webview_installed():
                    print("WebView2 Runtime não está instalado. Tentando instalar...")
                    webview.util.install_webview2()
            
            # Inicia a aplicação normalmente
            webview.start()
        except Exception as e:
            print(f"ERRO FATAL: {str(e)}")
            input("Pressione Enter para sair...")

if __name__ == "__main__":
    try:
        app = ChurrascariaApp()
        app.run()
    except Exception as e:
        print(f"ERRO INICIALIZAÇÃO: {str(e)}")
        input("Pressione Enter para sair...")