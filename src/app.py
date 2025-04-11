import webview
import json
import os
import tempfile
import win32print
import win32api
import re
from datetime import datetime, date
import random
import csv
from fpdf import FPDF
import threading
import tkinter as tk
from tkinter import filedialog

class ChurrascariaApp:
    def __init__(self):
        # Dados do cardápio
        self.cardapio = {
            "refeicoes": [
                {"id": 1, "nome": "Almoço Executivo", "preco": 25.00, "categoria": "refeicao", "ncm": "2106.90.90", "un": "UN"},
                {"id": 2, "nome": "Almoço Premium", "preco": 35.00, "categoria": "refeicao", "ncm": "2106.90.90", "un": "UN"},
                {"id": 3, "nome": "Almoço Vegetariano", "preco": 22.00, "categoria": "refeicao", "ncm": "2106.90.90", "un": "UN"}
            ],
            "bebidas": [
                {"id": 4, "nome": "Refrigerante", "preco": 5.00, "categoria": "bebida", "ncm": "2202.10.00", "un": "UN"},
                {"id": 5, "nome": "Cerveja", "preco": 7.00, "categoria": "bebida", "ncm": "2203.00.00", "un": "UN"}
            ],
            "sobremesas": [
                {"id": 6, "nome": "Pudim", "preco": 8.00, "categoria": "sobremesa", "ncm": "2106.90.90", "un": "UN"},
                {"id": 7, "nome": "Sorvete", "preco": 6.00, "categoria": "sobremesa", "ncm": "2105.00.00", "un": "UN"}
            ]
        }
        
        # Variáveis de estado
        self.pedido_atual = []
        self.cpf_cnpj = ""
        self.comprovante = ""
        self.entrega = False
        self.nome_cliente = ""
        self.endereco_rua = ""
        self.endereco_bairro = ""
        self.endereco_numero = ""
        self.sem_numero = False
        self.forma_pagamento = "dinheiro"  # Padrão: dinheiro
        self.taxa_entrega = 5.00  # Valor fixo da taxa de entrega
        
        # Cadastro de empresas
        self.empresas = []
        self.pedidos_empresas = []
        
        # Registro de vendas
        self.vendas_dia = []
        self.vendas_mes = []
        
        # Configurações do sistema
        self.configuracoes = {
            "pasta_comprovantes": os.path.join(tempfile.gettempdir(), "Comprovantes"),
            "pasta_relatorios_empresas": os.path.join(tempfile.gettempdir(), "Relatorios Empresas"),
            "pasta_relatorios_excel": os.path.join(tempfile.gettempdir(), "Relatorios Excel"),
            "impressora_padrao": win32print.GetDefaultPrinter() if self.verificar_impressoras() else ""
        }
        
        # Informações sobre o sistema e dados fiscais
        self.sobre_info = {
            "versao": "2.8",
            "desenvolvedor": "Churrascaria Sabor Gaúcho LTDA",
            "cnpj": "12.345.678/0001-99",
            "contato": "contato@churrascaria.com.br",
            "telefone": "(51) 1234-5678",
            "github": "https://github.com/seu-usuario",
            "endereco": "Rua dos Sabores, 123 - Centro - Porto Alegre/RS",
            "ie": "123.456.789.111",
            "im": "12345-6",
            "codigo_ibge": "4314902"
        }
        
        self.historico_versoes = [
            "v2.8 (20/01/2024) - Adicionado configurações de pastas e opção de múltiplos itens em pedidos corporativos",
            "v2.7 (15/01/2024) - Adicionado cadastro de empresas, pedidos corporativos e relatórios",
            "v2.6 (15/12/2023) - Adicionado seleção de forma de pagamento e campos detalhados de endereço",
            "v2.5 (15/11/2023) - Adicionado sistema de nota fiscal no comprovante",
            "v2.4 (15/10/2023) - Adicionado sistema de entrega com taxa",
            "v2.3 (15/09/2023) - Adicionado controle de quantidade por item",
            "v2.2 (15/08/2023) - Adicionada interface moderna",
            "v2.1 (15/07/2023) - Adicionado campo CPF/CNPJ",
            "v2.0 (10/07/2023) - Sistema de impressão direta",
            "v1.0 (01/06/2023) - Versão inicial"
        ]

        # Configuração de caminhos
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.carregar_dados()
        
        # Cria as pastas de configuração se não existirem
        self.criar_pastas_configuracao()
        
        # Cria a janela principal
        self.window = webview.create_window(
            'Sistema Churrascaria',
            html=self.get_html(),
            width=1450,
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
            self.atualizar_quantidade,
            self.set_entrega,
            self.set_dados_entrega,
            self.set_forma_pagamento,
            self.set_sem_numero,
            self.limpar_pedido,
            self.cadastrar_empresa,
            self.get_empresas,
            self.remover_empresa,
            self.adicionar_pedido_empresa,
            self.get_pedidos_empresa,
            self.gerar_relatorio_empresa,
            self.get_relatorio_dia,
            self.get_relatorio_mes,
            self.get_configuracoes,
            self.salvar_configuracoes,
            self.selecionar_pasta,
            self.exportar_relatorio_dia_csv,
            self.exportar_relatorio_mes_csv,
            self.remover_pedido_empresa,
            self.get_cardapio_categoria,
            self.get_item_cardapio
        )

    def criar_pastas_configuracao(self):
        """Cria as pastas de configuração se não existirem"""
        try:
            os.makedirs(self.configuracoes["pasta_comprovantes"], exist_ok=True)
            os.makedirs(self.configuracoes["pasta_relatorios_empresas"], exist_ok=True)
            os.makedirs(self.configuracoes["pasta_relatorios_excel"], exist_ok=True)
        except Exception as e:
            print(f"Erro ao criar pastas de configuração: {str(e)}")

    def carregar_dados(self):
        """Carrega os dados salvos de empresas, pedidos e configurações"""
        try:
            if os.path.exists('empresas.json'):
                with open('empresas.json', 'r', encoding='utf-8') as f:
                    self.empresas = json.load(f)
            
            if os.path.exists('pedidos_empresas.json'):
                with open('pedidos_empresas.json', 'r', encoding='utf-8') as f:
                    self.pedidos_empresas = json.load(f)
                    
            if os.path.exists('vendas_dia.json'):
                with open('vendas_dia.json', 'r', encoding='utf-8') as f:
                    self.vendas_dia = json.load(f)
                    
            if os.path.exists('vendas_mes.json'):
                with open('vendas_mes.json', 'r', encoding='utf-8') as f:
                    self.vendas_mes = json.load(f)
                    
            if os.path.exists('configuracoes.json'):
                with open('configuracoes.json', 'r', encoding='utf-8') as f:
                    self.configuracoes = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados: {str(e)}")

    def salvar_dados(self):
        """Salva os dados de empresas, pedidos e configurações"""
        try:
            with open('empresas.json', 'w', encoding='utf-8') as f:
                json.dump(self.empresas, f, ensure_ascii=False, indent=2)
                
            with open('pedidos_empresas.json', 'w', encoding='utf-8') as f:
                json.dump(self.pedidos_empresas, f, ensure_ascii=False, indent=2)
                
            with open('vendas_dia.json', 'w', encoding='utf-8') as f:
                json.dump(self.vendas_dia, f, ensure_ascii=False, indent=2)
                
            with open('vendas_mes.json', 'w', encoding='utf-8') as f:
                json.dump(self.vendas_mes, f, ensure_ascii=False, indent=2)
                
            with open('configuracoes.json', 'w', encoding='utf-8') as f:
                json.dump(self.configuracoes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")
    def get_cardapio_categoria(self, categoria):
        """Retorna os itens do cardápio de uma categoria específica."""
        return self.cardapio.get(categoria, [])
    
    
    def get_item_cardapio(self, item_id):
        """Retorna um item do cardápio com base no ID."""
        for categoria in self.cardapio.values():
            for item in categoria:
                if str(item["id"]) == str(item_id):  # compara como string para evitar problemas
                    return item
        return None

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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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
        .entrega-section {{
            margin-top: 15px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            display: none;
        }}
        .btn-pagamento {{
            flex: 1;
            margin: 2px;
        }}
        .btn-pagamento.active {{
            background-color: var(--primary);
            color: white;
        }}
        .numero-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .sem-numero {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .nav-link.active {{
            font-weight: bold;
            background-color: rgba(255, 255, 255, 0.1);
        }}
        .tab-pane {{
            padding: 15px 0;
        }}
        .table-responsive {{
            max-height: 400px;
            overflow-y: auto;
        }}
        .form-section {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .quantidade-empresa {{
            width: 60px;
        }}
        .config-section {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .item-empresa {{
            margin-bottom: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .btn-adicionar-item {{
            margin-top: 10px;
        }}
        .categoria-empresa {{
            margin-bottom: 15px;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
        }}
        .categoria-title {{
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
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
                <button class="btn btn-outline-light me-2" onclick="mostrarConfiguracoes()">
                    <i class="fas fa-cog"></i> Configurações
                </button>
                <button class="btn btn-outline-light" onclick="mostrarSobre()">
                    <i class="fas fa-info-circle"></i> Sobre
                </button>
            </div>
        </div>
    </nav>

    <div class="container">
        <ul class="nav nav-tabs mb-4" id="mainTabs">
            <li class="nav-item">
                <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#cardapio-tab">
                    <i class="fas fa-utensils me-1"></i> Cardápio
                </button>
            </li>
            <li class="nav-item">
                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#empresas-tab">
                    <i class="fas fa-building me-1"></i> Empresas
                </button>
            </li>
            <li class="nav-item">
                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#relatorios-tab">
                    <i class="fas fa-chart-bar me-1"></i> Relatórios
                </button>
            </li>
        </ul>

        <div class="tab-content">
            <!-- Tab Cardápio -->
            <div class="tab-pane fade show active" id="cardapio-tab">
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
                                
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="entrega-checkbox" onchange="toggleEntrega()">
                                    <label class="form-check-label" for="entrega-checkbox">
                                        É para entrega? (Taxa: R$ {self.taxa_entrega:.2f})
                                    </label>
                                </div>
                                
                                <div class="entrega-section" id="entrega-section">
                                    <div class="mb-3">
                                        <label class="form-label">Nome do Cliente:</label>
                                        <input type="text" class="form-control" id="nome-cliente" placeholder="Nome completo">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Rua:</label>
                                        <input type="text" class="form-control" id="endereco-rua" placeholder="Nome da rua">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Bairro:</label>
                                        <input type="text" class="form-control" id="endereco-bairro" placeholder="Nome do bairro">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Número:</label>
                                        <div class="numero-container">
                                            <input type="text" class="form-control" id="endereco-numero" placeholder="Número">
                                            <div class="sem-numero">
                                                <input type="checkbox" id="sem-numero" onchange="toggleSemNumero()">
                                                <label for="sem-numero">s/n</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Forma de Pagamento:</label>
                                    <div class="d-flex flex-wrap">
                                        <button type="button" class="btn btn-outline-secondary btn-pagamento" 
                                            onclick="selecionarPagamento('dinheiro')" id="btn-dinheiro">
                                            <i class="fas fa-money-bill-wave me-1"></i> Dinheiro
                                        </button>
                                        <button type="button" class="btn btn-outline-secondary btn-pagamento" 
                                            onclick="selecionarPagamento('pix')" id="btn-pix">
                                            <i class="fa-brands fa-pix"></i> PIX
                                        </button>
                                        <button type="button" class="btn btn-outline-secondary btn-pagamento" 
                                            onclick="selecionarPagamento('debito')" id="btn-debito">
                                            <i class="fas fa-credit-card me-1"></i> Débito
                                        </button>
                                        <button type="button" class="btn btn-outline-secondary btn-pagamento" 
                                            onclick="selecionarPagamento('credito')" id="btn-credito">
                                            <i class="fas fa-credit-card me-1"></i> Crédito
                                        </button>
                                    </div>
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

            <!-- Tab Empresas -->
            <div class="tab-pane fade" id="empresas-tab">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header bg-churrasco text-white">
                                <h5 class="mb-0"><i class="fas fa-building me-2"></i>Cadastro de Empresas</h5>
                            </div>
                            <div class="card-body">
                                <div class="form-section">
                                    <div class="mb-3">
                                        <label class="form-label">Nome da Empresa:</label>
                                        <input type="text" class="form-control" id="empresa-nome" placeholder="Nome completo">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">CNPJ:</label>
                                        <input type="text" class="form-control" id="empresa-cnpj" placeholder="00.000.000/0000-00">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Endereço:</label>
                                        <input type="text" class="form-control" id="empresa-rua" placeholder="Nome da rua">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Bairro:</label>
                                        <input type="text" class="form-control" id="empresa-bairro" placeholder="Nome do bairro">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Número:</label>
                                        <div class="numero-container">
                                            <input type="text" class="form-control" id="empresa-numero" placeholder="Número">
                                            <div class="sem-numero">
                                                <input type="checkbox" id="empresa-sem-numero" onchange="toggleEmpresaSemNumero()">
                                                <label for="empresa-sem-numero">s/n</label>
                                            </div>
                                        </div>
                                    </div>
                                    <button class="btn btn-primary w-100" onclick="cadastrarEmpresa()">
                                        <i class="fas fa-save me-2"></i> Cadastrar Empresa
                                    </button>
                                </div>

                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Nome</th>
                                                <th>CNPJ</th>
                                                <th>Endereço</th>
                                                <th>Ações</th>
                                            </tr>
                                        </thead>
                                        <tbody id="tabela-empresas">
                                            <!-- Dados serão preenchidos via JavaScript -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header bg-churrasco text-white">
                                <h5 class="mb-0"><i class="fas fa-clipboard-list me-2"></i>Pedidos Corporativos</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label class="form-label">Selecione a Empresa:</label>
                                    <select class="form-select" id="empresa-selecionada" onchange="carregarPedidosEmpresa()">
                                        <option value="">Selecione uma empresa</option>
                                        <!-- Opções serão preenchidas via JavaScript -->
                                    </select>
                                </div>

                                <div class="form-section" id="form-pedido-empresa" style="display: none;">
                                    <h5>Novo Pedido</h5>
                                    <div class="mb-3">
                                        <label class="form-label">Data:</label>
                                        <input type="date" class="form-control" id="pedido-data">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Funcionário:</label>
                                        <input type="text" class="form-control" id="pedido-funcionario" placeholder="Nome do funcionário">
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label class="form-label">Categoria:</label>
                                        <select class="form-select" id="categoria-item" onchange="carregarItensPorCategoria()">
                                            <option value="">Selecione uma categoria</option>
                                            <option value="refeicoes">Refeições</option>
                                            <option value="bebidas">Bebidas</option>
                                            <option value="sobremesas">Sobremesas</option>
                                        </select>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label class="form-label">Item:</label>
                                        <select class="form-select" id="item-selecionado">
                                            <option value="">Selecione um item</option>
                                            <!-- Itens serão carregados dinamicamente -->
                                        </select>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label class="form-label">Quantidade:</label>
                                        <input type="number" class="form-control quantidade-empresa" id="quantidade-item" value="1" min="1">
                                    </div>
                                    
                                    <button class="btn btn-primary w-100" onclick="adicionarItemEmpresa()">
                                        <i class="fas fa-plus-circle me-2"></i> Adicionar Item
                                    </button>
                                    
                                    <div class="mt-3" id="itens-adicionados">
                                        <!-- Itens adicionados serão exibidos aqui -->
                                    </div>
                                    
                                    <button class="btn btn-success w-100 mt-3" onclick="finalizarPedidoEmpresa()">
                                        <i class="fas fa-check-circle me-2"></i> Finalizar Pedido
                                    </button>
                                </div>

                                <div class="table-responsive mt-3" id="tabela-pedidos-empresa" style="display: none;">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Data</th>
                                                <th>Funcionário</th>
                                                <th>Itens</th>
                                                <th>Total</th>
                                                <th>Ações</th>
                                            </tr>
                                        </thead>
                                        <tbody id="lista-pedidos-empresa">
                                            <!-- Dados serão preenchidos via JavaScript -->
                                        </tbody>
                                    </table>
                                    
                                    <div class="d-flex justify-content-between align-items-center mt-3">
                                        <h5>Total do Mês:</h5>
                                        <h5 id="total-empresa">R$ 0,00</h5>
                                    </div>
                                    
                                    <div class="d-flex justify-content-between align-items-center mt-1">
                                        <h5>Total Geral:</h5>
                                        <h5 id="total-geral-empresa">R$ 0,00</h5>
                                    </div>
                                    
                                    <button class="btn btn-success mt-2 w-100" onclick="gerarRelatorioEmpresa()">
                                        <i class="fas fa-file-pdf me-2"></i> Gerar Relatório
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab Relatórios -->
            <div class="tab-pane fade" id="relatorios-tab">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header bg-churrasco text-white">
                                <h5 class="mb-0"><i class="fas fa-sun me-2"></i>Relatório Diário</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label class="form-label">Selecione o Dia:</label>
                                    <input type="date" class="form-control" id="relatorio-dia" onchange="carregarRelatorioDia()">
                                </div>
                                
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Hora</th>
                                                <th>Cliente</th>
                                                <th>Itens</th>
                                                <th>Total</th>
                                            </tr>
                                        </thead>
                                        <tbody id="tabela-relatorio-dia">
                                            <!-- Dados serão preenchidos via JavaScript -->
                                        </tbody>
                                    </table>
                                </div>
                                
                                <div class="d-flex justify-content-between align-items-center mt-3">
                                    <h5>Total do Dia:</h5>
                                    <h5 id="total-dia">R$ 0,00</h5>
                                </div>
                                
                                <button class="btn btn-success mt-2 w-100" onclick="exportarRelatorioDia()">
                                    <i class="fas fa-file-excel me-2"></i> Exportar para Excel
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header bg-churrasco text-white">
                                <h5 class="mb-0"><i class="fas fa-calendar-alt me-2"></i>Relatório Mensal</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label class="form-label">Selecione o Mês:</label>
                                    <input type="month" class="form-control" id="relatorio-mes" onchange="carregarRelatorioMes()">
                                </div>
                                
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Dia</th>
                                                <th>Vendas</th>
                                                <th>Total</th>
                                            </tr>
                                        </thead>
                                        <tbody id="tabela-relatorio-mes">
                                            <!-- Dados serão preenchidos via JavaScript -->
                                        </tbody>
                                    </table>
                                </div>
                                
                                <div class="d-flex justify-content-between align-items-center mt-3">
                                    <h5>Total do Mês:</h5>
                                    <h5 id="total-mes">R$ 0,00</h5>
                                </div>
                                
                                <button class="btn btn-success mt-2 w-100" onclick="exportarRelatorioMes()">
                                    <i class="fas fa-file-excel me-2"></i> Exportar para Excel
                                </button>
                            </div>
                        </div>
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
                            <p><strong>Inscrição Estadual:</strong> {self.sobre_info['ie']}</p>
                            <p><strong>Endereço:</strong> {self.sobre_info['endereco']}</p>
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

    <!-- Modal Tipo Comprovante -->
    <div class="modal fade" id="tipoComprovanteModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-churrasco text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-print me-2"></i>Tipo de Comprovante
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Selecione o tipo de comprovante que deseja imprimir:</p>
                    <div class="d-grid gap-2">
                        <button type="button" class="btn btn-primary" onclick="imprimirComprovante('nota_fiscal')">
                            <i class="fas fa-file-invoice me-2"></i>Nota Fiscal Completa
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="imprimirComprovante('simples')">
                            <i class="fas fa-receipt me-2"></i>Notinha Simples
                        </button>
                        <button type="button" class="btn btn-success" onclick="salvarComprovantePDF('nota_fiscal')">
                            <i class="fas fa-save me-2"></i>Salvar Nota Fiscal (PDF)
                        </button>
                        <button type="button" class="btn btn-info" onclick="salvarComprovantePDF('simples')">
                            <i class="fas fa-save me-2"></i>Salvar Notinha (PDF)
                        </button>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-2"></i>Cancelar
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Configurações -->
    <div class="modal fade" id="configuracoesModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-churrasco text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-cog me-2"></i>Configurações do Sistema
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="config-section">
                        <h5><i class="fas fa-folder me-2"></i>Pastas</h5>
                        <div class="mb-3">
                            <label class="form-label">Pasta para salvar comprovantes:</label>
                            <div class="input-group">
                                <input type="text" class="form-control" id="pasta-comprovantes">
                                <button class="btn btn-outline-secondary" type="button" onclick="selecionarPasta('comprovantes')">
                                    <i class="fas fa-folder-open"></i>
                                </button>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Pasta para salvar relatórios de empresas:</label>
                            <div class="input-group">
                                <input type="text" class="form-control" id="pasta-relatorios-empresas">
                                <button class="btn btn-outline-secondary" type="button" onclick="selecionarPasta('relatorios-empresas')">
                                    <i class="fas fa-folder-open"></i>
                                </button>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Pasta para salvar relatórios em Excel:</label>
                            <div class="input-group">
                                <input type="text" class="form-control" id="pasta-relatorios-excel">
                                <button class="btn btn-outline-secondary" type="button" onclick="selecionarPasta('relatorios-excel')">
                                    <i class="fas fa-folder-open"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="config-section">
                        <h5><i class="fas fa-print me-2"></i>Impressão</h5>
                        <div class="mb-3">
                            <label class="form-label">Impressora padrão:</label>
                            <select class="form-select" id="impressora-padrao">
                                <!-- Opções serão preenchidas via JavaScript -->
                            </select>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-2"></i>Cancelar
                    </button>
                    <button type="button" class="btn btn-primary" onclick="salvarConfiguracoes()">
                        <i class="fas fa-save me-2"></i>Salvar Configurações
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

        // Função para mostrar/ocultar seção de entrega
        function toggleEntrega() {{
            const checkbox = document.getElementById('entrega-checkbox');
            const entregaSection = document.getElementById('entrega-section');
            
            if (checkbox.checked) {{
                entregaSection.style.display = 'block';
                pywebview.api.set_entrega(true).then(() => {{
                    atualizarPedido();
                }});
            }} else {{
                entregaSection.style.display = 'none';
                pywebview.api.set_entrega(false).then(() => {{
                    atualizarPedido();
                }});
            }}
            
        }}

        // Função para alternar sem número
        function toggleSemNumero() {{
            const semNumero = document.getElementById('sem-numero').checked;
            const numeroInput = document.getElementById('endereco-numero');
            
            numeroInput.disabled = semNumero;
            if (semNumero) {{
                numeroInput.value = '';
            }}
            
            pywebview.api.set_sem_numero(semNumero).catch(err => {{
                console.error('Erro ao atualizar sem número:', err);
            }});
        }}

        // Função para alternar sem número da empresa
        function toggleEmpresaSemNumero() {{
            const semNumero = document.getElementById('empresa-sem-numero').checked;
            const numeroInput = document.getElementById('empresa-numero');
            
            numeroInput.disabled = semNumero;
            if (semNumero) {{
                numeroInput.value = '';
            }}
        }}

        // Função para atualizar dados de entrega
        function atualizarDadosEntrega() {{
            const nome = document.getElementById('nome-cliente').value;
            const rua = document.getElementById('endereco-rua').value;
            const bairro = document.getElementById('endereco-bairro').value;
            const numero = document.getElementById('endereco-numero').value;
            
            pywebview.api.set_dados_entrega(nome, rua, bairro, numero).catch(err => {{
                console.error('Erro ao atualizar dados de entrega:', err);
            }});
        }}

        // Função para selecionar forma de pagamento
        function selecionarPagamento(tipo) {{
            // Remove a classe active de todos os botões
            document.querySelectorAll('.btn-pagamento').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Adiciona a classe active ao botão selecionado
            document.getElementById(`btn-${{tipo}}`).classList.add('active');
            
            // Atualiza no backend
            pywebview.api.set_forma_pagamento(tipo).catch(err => {{
                console.error('Erro ao atualizar forma de pagamento:', err);
            }});
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
                
                // Adiciona taxa de entrega se aplicável
                if (data.entrega) {{
                    const li = document.createElement('li');
                    li.className = 'list-group-item bg-light';
                    li.innerHTML = `
                        <div class="item-pedido">
                            <div class="item-info">
                                <strong>Taxa de Entrega</strong>
                            </div>
                            <div class="item-controles">
                                <div class="item-valor">
                                    R$ ${{data.taxa_entrega.toFixed(2)}}
                                </div>
                            </div>
                        </div>
                    `;
                    lista.appendChild(li);
                }}
                
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
            const entrega = document.getElementById('entrega-checkbox').checked;
            
            if (entrega) {{
                const nome = document.getElementById('nome-cliente').value.trim();
                const rua = document.getElementById('endereco-rua').value.trim();
                const bairro = document.getElementById('endereco-bairro').value.trim();
                const numero = document.getElementById('endereco-numero').value.trim();
                const semNumero = document.getElementById('sem-numero').checked;
                
                if (!nome || !rua || !bairro || (!numero && !semNumero)) {{
                    alert('Por favor, preencha todos os dados de entrega!');
                    return;
                }}
                
                // Atualiza os dados de entrega antes de finalizar
                pywebview.api.set_dados_entrega(nome, rua, bairro, numero).then(() => {{
                    pywebview.api.finalizar_pedido(cpf).then(resultado => {{
                        if (resultado.success) {{
                            // Mostra o modal para escolher o tipo de comprovante
                            new bootstrap.Modal(document.getElementById('tipoComprovanteModal')).show();
                        }} else {{
                            alert(resultado.message);
                        }}
                    }});
                }});
            }} else {{
                pywebview.api.finalizar_pedido(cpf).then(resultado => {{
                    if (resultado.success) {{
                        // Mostra o modal para escolher o tipo de comprovante
                        new bootstrap.Modal(document.getElementById('tipoComprovanteModal')).show();
                    }} else {{
                        alert(resultado.message);
                    }}
                }});
            }}
        }}
        
        function imprimirComprovante(tipo) {{
            if (!checkAPI()) return;
            
            // Fecha o modal de seleção
            bootstrap.Modal.getInstance(document.getElementById('tipoComprovanteModal')).hide();
            
            pywebview.api.imprimir_comprovante(tipo).then(res => {{
                if (res.success) {{
                    // Limpa o pedido e CPF após impressão
                    document.getElementById('cpf-cnpj').value = '';
                    document.getElementById('entrega-checkbox').checked = false;
                    document.getElementById('nome-cliente').value = '';
                    document.getElementById('endereco-rua').value = '';
                    document.getElementById('endereco-bairro').value = '';
                    document.getElementById('endereco-numero').value = '';
                    document.getElementById('sem-numero').checked = false;
                    document.getElementById('entrega-section').style.display = 'none';
                    pywebview.api.limpar_pedido().then(() => {{
                        atualizarPedido();
                    }});
                }} else {{
                    alert(res.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao imprimir:', err);
            }});
        }}
        
        function salvarComprovantePDF(tipo) {{
            if (!checkAPI()) return;
            
            // Fecha o modal de seleção
            bootstrap.Modal.getInstance(document.getElementById('tipoComprovanteModal')).hide();
            
            pywebview.api.salvar_comprovante(tipo).then(res => {{
                if (res.success) {{
                    // Limpa o pedido e CPF após salvar
                    document.getElementById('cpf-cnpj').value = '';
                    document.getElementById('entrega-checkbox').checked = false;
                    document.getElementById('nome-cliente').value = '';
                    document.getElementById('endereco-rua').value = '';
                    document.getElementById('endereco-bairro').value = '';
                    document.getElementById('endereco-numero').value = '';
                    document.getElementById('sem-numero').checked = false;
                    document.getElementById('entrega-section').style.display = 'none';
                    pywebview.api.limpar_pedido().then(() => {{
                        atualizarPedido();
                    }});
                }} else {{
                    alert(res.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao salvar:', err);
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
        
        // Funções para empresas
        function carregarEmpresas() {{
            if (!checkAPI()) return;
            
            pywebview.api.get_empresas().then(empresas => {{
                const tabela = document.getElementById('tabela-empresas');
                const select = document.getElementById('empresa-selecionada');
                
                tabela.innerHTML = '';
                select.innerHTML = '<option value="">Selecione uma empresa</option>';
                
                empresas.forEach((empresa, index) => {{
                    // Adiciona à tabela
                    const tr = document.createElement('tr');
                    const endereco = `${{empresa.rua}}, ${{empresa.sem_numero ? 's/n' : empresa.numero}} - ${{empresa.bairro}}`;
                    
                    tr.innerHTML = `
                        <td>${{empresa.nome}}</td>
                        <td>${{empresa.cnpj}}</td>
                        <td>${{endereco}}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="removerEmpresa(${{index}})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tabela.appendChild(tr);
                    
                    // Adiciona ao select
                    const option = document.createElement('option');
                    option.value = index;
                    option.textContent = `${{empresa.nome}} (CNPJ: ${{empresa.cnpj}})`;
                    select.appendChild(option);
                }});
            }}).catch(err => {{
                console.error('Erro ao carregar empresas:', err);
            }});
        }}
        
        function cadastrarEmpresa() {{
            if (!checkAPI()) return;
            
            const nome = document.getElementById('empresa-nome').value.trim();
            const cnpj = document.getElementById('empresa-cnpj').value.trim();
            const rua = document.getElementById('empresa-rua').value.trim();
            const bairro = document.getElementById('empresa-bairro').value.trim();
            const numero = document.getElementById('empresa-numero').value.trim();
            const semNumero = document.getElementById('empresa-sem-numero').checked;
            
            if (!nome || !cnpj || !rua || !bairro || (!numero && !semNumero)) {{
                alert('Por favor, preencha todos os campos obrigatórios!');
                return;
            }}
            
            pywebview.api.cadastrar_empresa(nome, cnpj, rua, bairro, numero, semNumero).then(resultado => {{
                if (resultado.success) {{
                    // Limpa os campos
                    document.getElementById('empresa-nome').value = '';
                    document.getElementById('empresa-cnpj').value = '';
                    document.getElementById('empresa-rua').value = '';
                    document.getElementById('empresa-bairro').value = '';
                    document.getElementById('empresa-numero').value = '';
                    document.getElementById('empresa-sem-numero').checked = false;
                    
                    // Recarrega a lista de empresas
                    carregarEmpresas();
                    alert('Empresa cadastrada com sucesso!');
                }} else {{
                    alert(resultado.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao cadastrar empresa:', err);
            }});
        }}
        
        function removerEmpresa(index) {{
            if (!checkAPI()) return;
            
            if (confirm('Tem certeza que deseja remover esta empresa?')) {{
                pywebview.api.remover_empresa(index).then(resultado => {{
                    if (resultado.success) {{
                        carregarEmpresas();
                        // Limpa a seleção de empresa
                        document.getElementById('empresa-selecionada').value = '';
                        document.getElementById('form-pedido-empresa').style.display = 'none';
                        document.getElementById('tabela-pedidos-empresa').style.display = 'none';
                        alert('Empresa removida com sucesso!');
                    }} else {{
                        alert(resultado.message);
                    }}
                }}).catch(err => {{
                    console.error('Erro ao remover empresa:', err);
                }});
            }}
        }}
        
        function carregarPedidosEmpresa() {{
            if (!checkAPI()) return;
            
            const select = document.getElementById('empresa-selecionada');
            const empresaIndex = select.value;
            
            if (!empresaIndex) {{
                document.getElementById('form-pedido-empresa').style.display = 'none';
                document.getElementById('tabela-pedidos-empresa').style.display = 'none';
                return;
            }}
            
            document.getElementById('form-pedido-empresa').style.display = 'block';
            
            pywebview.api.get_pedidos_empresa(empresaIndex).then(pedidos => {{
                const tabela = document.getElementById('lista-pedidos-empresa');
                const totalElement = document.getElementById('total-empresa');
                const totalGeralElement = document.getElementById('total-geral-empresa');
                
                tabela.innerHTML = '';
                let totalMes = 0;
                let totalGeral = 0;
                
                // Filtra pedidos do mês atual
                const hoje = new Date();
                const mesAtual = hoje.getMonth() + 1;
                const anoAtual = hoje.getFullYear();
                
                pedidos.forEach((pedido, index) => {{
                    const tr = document.createElement('tr');
                    const data = new Date(pedido.data);
                    const dataFormatada = data.toLocaleDateString('pt-BR');
                    
                    // Formata os itens para exibição
                    const itens = pedido.itens.map(item => `${{item.item.nome}} (x${{item.quantidade}})`).join(', ');
                    
                    // Calcula o total do pedido
                    const totalPedido = pedido.itens.reduce((sum, item) => sum + (item.item.preco * item.quantidade), 0);
                    
                    totalGeral += totalPedido;
                    
                    // Verifica se é do mês atual
                    if (data.getMonth() + 1 === mesAtual && data.getFullYear() === anoAtual) {{
                        totalMes += totalPedido;
                    }}
                    
                    tr.innerHTML = `
                        <td>${{dataFormatada}}</td>
                        <td>${{pedido.funcionario}}</td>
                        <td>${{itens}}</td>
                        <td>R$ ${{totalPedido.toFixed(2)}}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="removerPedidoEmpresa(${{empresaIndex}}, ${{index}})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tabela.appendChild(tr);
                }});
                
                totalElement.textContent = `R$ ${{totalMes.toFixed(2)}}`;
                totalGeralElement.textContent = `R$ ${{totalGeral.toFixed(2)}}`;
                document.getElementById('tabela-pedidos-empresa').style.display = 'block';
            }}).catch(err => {{
                console.error('Erro ao carregar pedidos da empresa:', err);
            }});
        }}
        
        // Funções para carregar itens por categoria
        function carregarItensPorCategoria() {{
            const categoria = document.getElementById('categoria-item').value;
            const selectItem = document.getElementById('item-selecionado');
            
            selectItem.innerHTML = '<option value="">Selecione um item</option>';
            
            if (!categoria) return;
            
            pywebview.api.get_cardapio_categoria(categoria).then(itens => {{
                itens.forEach(item => {{
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = `${{item.nome}} - R$ ${{item.preco.toFixed(2)}}`;
                    selectItem.appendChild(option);
                }});
            }}).catch(err => {{
                console.error('Erro ao carregar itens:', err);
            }});
        }}
        
        function adicionarItemEmpresa() {{
            if (!checkAPI()) return;
            
            const itemId = document.getElementById('item-selecionado').value;
            const quantidade = parseInt(document.getElementById('quantidade-item').value) || 1;
            
            if (!itemId || quantidade < 1) {{
                alert('Selecione um item e informe uma quantidade válida!');
                return;
            }}
            
            pywebview.api.get_item_cardapio(itemId).then(item => {{
                const container = document.getElementById('itens-adicionados');
                
                const div = document.createElement('div');
                div.className = 'item-empresa';
                div.dataset.id = itemId;
                div.dataset.quantidade = quantidade;
                
                div.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${{item.nome}}</strong>
                            <div>Quantidade: ${{quantidade}} - R$ ${{(item.preco * quantidade).toFixed(2)}}</div>
                        </div>
                        <button class="btn btn-sm btn-danger" onclick="this.parentElement.parentElement.remove()">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;
                
                container.appendChild(div);
                
                // Limpa os campos
                document.getElementById('item-selecionado').value = '';
                document.getElementById('quantidade-item').value = 1;
            }}).catch(err => {{
                console.error('Erro ao adicionar item:', err);
                alert('Erro ao adicionar item!');
            }});
        }}
        
        function finalizarPedidoEmpresa() {{
            if (!checkAPI()) return;
            
            const empresaIndex = document.getElementById('empresa-selecionada').value;
            const data = document.getElementById('pedido-data').value;
            const funcionario = document.getElementById('pedido-funcionario').value.trim();
            
            if (!empresaIndex || !data || !funcionario) {{
                alert('Preencha todos os campos obrigatórios!');
                return;
            }}
            
            const itensDivs = document.querySelectorAll('#itens-adicionados .item-empresa');
            if (itensDivs.length === 0) {{
                alert('Adicione pelo menos um item ao pedido!');
                return;
            }}
            
            // Coleta os itens adicionados
            const itens = [];
            itensDivs.forEach(div => {{
                const itemId = div.dataset.id;
                const quantidade = parseInt(div.dataset.quantidade);
                
                itens.push({{
                    id: itemId,
                    quantidade: quantidade
                }});
            }});
            
            pywebview.api.adicionar_pedido_empresa(parseInt(empresaIndex), data, funcionario, itens).then(resultado => {{
                if (resultado.success) {{
                    // Limpa os campos
                    document.getElementById('pedido-data').value = '';
                    document.getElementById('pedido-funcionario').value = '';
                    document.getElementById('itens-adicionados').innerHTML = '';
                    
                    // Recarrega os pedidos
                    carregarPedidosEmpresa();
                    alert('Pedido adicionado com sucesso!');
                }} else {{
                    alert(resultado.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao finalizar pedido:', err);
                alert('Erro ao finalizar pedido!');
            }});
        }}
        
        function removerPedidoEmpresa(empresaIndex, pedidoIndex) {{
            if (!checkAPI()) return;
            
            if (confirm('Tem certeza que deseja remover este pedido?')) {{
                pywebview.api.remover_pedido_empresa(empresaIndex, pedidoIndex).then(resultado => {{
                    if (resultado.success) {{
                        carregarPedidosEmpresa();
                        alert('Pedido removido com sucesso!');
                    }} else {{
                        alert(resultado.message);
                    }}
                }}).catch(err => {{
                    console.error('Erro ao remover pedido:', err);
                }});
            }}
        }}
        
        function gerarRelatorioEmpresa() {{
            if (!checkAPI()) return;
            
            const empresaIndex = document.getElementById('empresa-selecionada').value;
            
            if (!empresaIndex) {{
                alert('Selecione uma empresa primeiro!');
                return;
            }}
            
            const opcao = confirm('Deseja imprimir o relatório da empresa?\\n(Cancelar para apenas salvar)');
            
            pywebview.api.gerar_relatorio_empresa(parseInt(empresaIndex), opcao).then(resultado => {{
                if (resultado.success) {{
                    alert(resultado.message);
                }} else {{
                    alert(resultado.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao gerar relatório:', err);
            }});
        }}
        
        // Funções para relatórios
        function carregarRelatorioDia() {{
            if (!checkAPI()) return;
            
            const data = document.getElementById('relatorio-dia').value;
            
            if (!data) return;
            
            pywebview.api.get_relatorio_dia(data).then(relatorio => {{
                const tabela = document.getElementById('tabela-relatorio-dia');
                const totalElement = document.getElementById('total-dia');
                
                tabela.innerHTML = '';
                let total = 0;
                
                relatorio.vendas.forEach(venda => {{
                    const tr = document.createElement('tr');
                    const dataHora = new Date(venda.data_hora);
                    const horaFormatada = dataHora.toLocaleTimeString('pt-BR');
                    
                    // Formata os itens
                    const itens = venda.itens.map(item => `${{item.nome}} (x${{item.quantidade}})`).join(', ');
                    
                    total += venda.total;
                    
                    tr.innerHTML = `
                        <td>${{horaFormatada}}</td>
                        <td>${{venda.cliente || 'Não identificado'}}</td>
                        <td>${{itens}}</td>
                        <td>R$ ${{venda.total.toFixed(2)}}</td>
                    `;
                    tabela.appendChild(tr);
                }});
                
                totalElement.textContent = `R$ ${{total.toFixed(2)}}`;
            }}).catch(err => {{
                console.error('Erro ao carregar relatório diário:', err);
            }});
        }}
        
        function carregarRelatorioMes() {{
            if (!checkAPI()) return;
            
            const mes = document.getElementById('relatorio-mes').value;
            
            if (!mes) return;
            
            pywebview.api.get_relatorio_mes(mes).then(relatorio => {{
                const tabela = document.getElementById('tabela-relatorio-mes');
                const totalElement = document.getElementById('total-mes');
                
                tabela.innerHTML = '';
                let total = 0;
                
                relatorio.vendas.forEach(venda => {{
                    const tr = document.createElement('tr');
                    const data = new Date(venda.data);
                    const dataFormatada = data.toLocaleDateString('pt-BR');
                    
                    total += venda.total;
                    
                    tr.innerHTML = `
                        <td>${{dataFormatada}}</td>
                        <td>${{venda.quantidade}}</td>
                        <td>R$ ${{venda.total.toFixed(2)}}</td>
                    `;
                    tabela.appendChild(tr);
                }});
                
                totalElement.textContent = `R$ ${{total.toFixed(2)}}`;
            }}).catch(err => {{
                console.error('Erro ao carregar relatório mensal:', err);
            }});
        }}
        
        function exportarRelatorioDia() {{
            if (!checkAPI()) return;
            
            const data = document.getElementById('relatorio-dia').value;
            
            if (!data) {{
                alert('Selecione um dia primeiro!');
                return;
            }}
            
            pywebview.api.exportar_relatorio_dia_csv(data).then(resultado => {{
                if (resultado.success) {{
                    alert(resultado.message);
                }} else {{
                    alert(resultado.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao exportar relatório:', err);
                alert('Erro ao exportar relatório!');
            }});
        }}
        
        function exportarRelatorioMes() {{
            if (!checkAPI()) return;
            
            const mes = document.getElementById('relatorio-mes').value;
            
            if (!mes) {{
                alert('Selecione um mês primeiro!');
                return;
            }}
            
            pywebview.api.exportar_relatorio_mes_csv(mes).then(resultado => {{
                if (resultado.success) {{
                    alert(resultado.message);
                }} else {{
                    alert(resultado.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao exportar relatório:', err);
                alert('Erro ao exportar relatório!');
            }});
        }}
        
        // Funções para configurações
        function mostrarConfiguracoes() {{
            if (!checkAPI()) return;
            
            pywebview.api.get_configuracoes().then(config => {{
                document.getElementById('pasta-comprovantes').value = config.pasta_comprovantes;
                document.getElementById('pasta-relatorios-empresas').value = config.pasta_relatorios_empresas;
                document.getElementById('pasta-relatorios-excel').value = config.pasta_relatorios_excel;
                
                // Preenche as impressoras disponíveis
                const selectImpressora = document.getElementById('impressora-padrao');
                selectImpressora.innerHTML = '';
                
                if (config.impressora_padrao) {{
                    const option = document.createElement('option');
                    option.value = config.impressora_padrao;
                    option.textContent = config.impressora_padrao;
                    selectImpressora.appendChild(option);
                }}
                
                new bootstrap.Modal(document.getElementById('configuracoesModal')).show();
            }}).catch(err => {{
                console.error('Erro ao carregar configurações:', err);
            }});
        }}
        
        function selecionarPasta(tipo) {{
            if (!checkAPI()) return;
            
            pywebview.api.selecionar_pasta().then(caminho => {{
                if (caminho) {{
                    document.getElementById(`pasta-${{tipo}}`).value = caminho;
                }}
            }}).catch(err => {{
                console.error('Erro ao selecionar pasta:', err);
            }});
        }}
        
        function salvarConfiguracoes() {{
            if (!checkAPI()) return;
            
            const configuracoes = {{
                pasta_comprovantes: document.getElementById('pasta-comprovantes').value,
                pasta_relatorios_empresas: document.getElementById('pasta-relatorios-empresas').value,
                pasta_relatorios_excel: document.getElementById('pasta-relatorios-excel').value,
                impressora_padrao: document.getElementById('impressora-padrao').value
            }};
            
            pywebview.api.salvar_configuracoes(configuracoes).then(resultado => {{
                if (resultado.success) {{
                    alert('Configurações salvas com sucesso!');
                    bootstrap.Modal.getInstance(document.getElementById('configuracoesModal')).hide();
                }} else {{
                    alert(resultado.message);
                }}
            }}).catch(err => {{
                console.error('Erro ao salvar configurações:', err);
            }});
        }}
        
        // Atualiza o pedido automaticamente
        setInterval(atualizarPedido, 1000);
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {{
            // Verifica se todos os recursos estão carregados
            if (typeof bootstrap !== 'undefined' && typeof pywebview !== 'undefined') {{
                atualizarPedido();
                // Seleciona dinheiro como padrão
                selecionarPagamento('dinheiro');
                
                // Carrega as empresas
                carregarEmpresas();
                
                // Define a data atual como padrão nos relatórios
                const hoje = new Date().toISOString().split('T')[0];
                document.getElementById('relatorio-dia').value = hoje;
                
                const mesAtual = new Date().toISOString().slice(0, 7);
                document.getElementById('relatorio-mes').value = mesAtual;
                
                // Carrega os relatórios iniciais
                carregarRelatorioDia();
                carregarRelatorioMes();
            }} else {{
                setTimeout(function() {{
                    if (typeof bootstrap === 'undefined' || typeof pywebview === 'undefined') {{
                        checkAPI();
                    }} else {{
                        atualizarPedido();
                        // Seleciona dinheiro como padrão
                        selecionarPagamento('dinheiro');
                        
                        // Carrega as empresas
                        carregarEmpresas();
                        
                        // Define a data atual como padrão nos relatórios
                        const hoje = new Date().toISOString().split('T')[0];
                        document.getElementById('relatorio-dia').value = hoje;
                        
                        const mesAtual = new Date().toISOString().slice(0, 7);
                        document.getElementById('relatorio-mes').value = mesAtual;
                        
                        // Carrega os relatórios iniciais
                        carregarRelatorioDia();
                        carregarRelatorioMes();
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
                    "descricao": "Item personalizado pelo cliente",
                    "ncm": "2106.90.90",  # NCM genérico para alimentos
                    "un": "UN"
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
        total_itens = sum(item['item']['preco'] * item['quantidade'] for item in self.pedido_atual)
        total = total_itens + (self.taxa_entrega if self.entrega else 0)
        
        return {
            "itens": self.pedido_atual,
            "total": total,
            "entrega": self.entrega,
            "taxa_entrega": self.taxa_entrega,
            "forma_pagamento": self.forma_pagamento
        }

    def set_entrega(self, entrega):
        """Define se o pedido é para entrega"""
        self.entrega = entrega
        return {"success": True}

    def set_dados_entrega(self, nome, rua, bairro, numero):
        """Define os dados de entrega"""
        self.nome_cliente = nome
        self.endereco_rua = rua
        self.endereco_bairro = bairro
        self.endereco_numero = numero
        return {"success": True}

    def set_sem_numero(self, sem_numero):
        """Define se o endereço é sem número"""
        self.sem_numero = sem_numero
        return {"success": True}

    def set_forma_pagamento(self, forma):
        """Define a forma de pagamento"""
        self.forma_pagamento = forma
        return {"success": True}

    def limpar_pedido(self):
        """Limpa o pedido atual e o CPF/CNPJ"""
        self.pedido_atual = []
        self.cpf_cnpj = ""
        self.entrega = False
        self.nome_cliente = ""
        self.endereco_rua = ""
        self.endereco_bairro = ""
        self.endereco_numero = ""
        self.sem_numero = False
        self.forma_pagamento = "dinheiro"
        return {"success": True}

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
            "github": self.sobre_info["github"],
            "endereco": self.sobre_info["endereco"],
            "ie": self.sobre_info["ie"],
            "im": self.sobre_info["im"]
        }

    def finalizar_pedido(self, cpf_cnpj=""):
        """Finaliza o pedido e prepara o comprovante"""
        if not self.pedido_atual:
            return {"success": False, "message": "Nenhum item selecionado para emitir comprovante."}
        
        # Valida CPF/CNPJ
        validacao = self.validar_cpf_cnpj(cpf_cnpj)
        if not validacao['valid']:
            return {"success": False, "message": "CPF/CNPJ inválido! Digite 11 dígitos para CPF ou 14 para CNPJ."}
        
        # Valida dados de entrega se necessário
        if self.entrega and (not self.nome_cliente or not self.endereco_rua or not self.endereco_bairro or (not self.endereco_numero and not self.sem_numero)):
            return {"success": False, "message": "Preencha todos os dados de entrega!"}
        
        # Calcula o total
        total_itens = sum(item['item']['preco'] * item['quantidade'] for item in self.pedido_atual)
        self.total_pedido = total_itens + (self.taxa_entrega if self.entrega else 0)
        
        # Registra a venda para relatório
        self.registrar_venda()
        
        return {"success": True, "total": self.total_pedido}

    def registrar_venda(self):
        """Registra a venda atual para os relatórios"""
        now = datetime.now()
        data_hora = now.isoformat()
        data = now.strftime("%Y-%m-%d")
        
        # Cria o registro da venda
        venda = {
            "data_hora": data_hora,
            "cliente": self.nome_cliente if self.nome_cliente else self.cpf_cnpj if self.cpf_cnpj else "Não identificado",
            "itens": [{
                "id": item['item']['id'],
                "nome": item['item']['nome'],
                "preco": item['item']['preco'],
                "quantidade": item['quantidade'],
                "categoria": item['item']['categoria']
            } for item in self.pedido_atual],
            "total": self.total_pedido,
            "forma_pagamento": self.forma_pagamento,
            "entrega": self.entrega
        }
        
        # Adiciona ao registro do dia
        self.vendas_dia.append(venda)
        
        # Atualiza o registro do mês
        mes_atual = now.strftime("%Y-%m")
        venda_mes_existente = next((v for v in self.vendas_mes if v["data"] == data), None)
        
        if venda_mes_existente:
            venda_mes_existente["quantidade"] += 1
            venda_mes_existente["total"] += self.total_pedido
        else:
            self.vendas_mes.append({
                "data": data,
                "quantidade": 1,
                "total": self.total_pedido
            })
        
        # Salva os dados
        self.salvar_dados()

    def gerar_comprovante(self, tipo='nota_fiscal'):
        """Gera o texto do comprovante com ou sem nota fiscal"""
        now = datetime.now()
        data_hora = now.strftime("%d/%m/%Y %H:%M:%S")
        
        if tipo == 'nota_fiscal':
            return self.gerar_comprovante_nota_fiscal(data_hora, now)
        else:
            return self.gerar_comprovante_simples(data_hora)

    def gerar_comprovante_nota_fiscal(self, data_hora, now):
        """Gera o texto do comprovante com formato de nota fiscal"""
        numero_nota = random.randint(1000, 9999)
        serie_nota = "1"
        modelo_nota = "59"  # Modelo 59 para NFC-e
        codigo_verificacao = f"{random.randint(100000, 999999)}"
        
        cabecalho = (
            f"{'CHURRASCARIA SABOR GAÚCHO'.center(40)}\n"
            f"{self.sobre_info['endereco'].center(40)}\n"
            f"CNPJ: {self.sobre_info['cnpj']} IE: {self.sobre_info['ie']}\n"
            f"IM: {self.sobre_info['im']}\n"
            f"{'-'*40}\n"
            f"NFC-e N° {numero_nota} Série {serie_nota}\n"
            f"Data: {data_hora}\n"
            f"Código de Verificação: {codigo_verificacao}\n"
            f"Modelo: {modelo_nota}\n"
            f"{'-'*40}\n"
        )
        
        if self.cpf_cnpj:
            cabecalho += f"CONSUMIDOR: {self.cpf_cnpj}\n"
        else:
            cabecalho += "CONSUMIDOR: Não identificado\n"
            
        if self.entrega:
            numero_endereco = "s/n" if self.sem_numero else self.endereco_numero
            cabecalho += (
                f"\nENTREGA PARA:\n"
                f"{self.nome_cliente}\n"
                f"{self.endereco_rua}, {numero_endereco} - {self.endereco_bairro}\n"
                f"{'-'*40}\n"
            )
        
        itens = "CÓD  DESCRIÇÃO                  QTD  UN  VL UNIT  VL TOTAL\n"
        itens += "-"*40 + "\n"
        
        for pedido in self.pedido_atual:
            item = pedido['item']
            quantidade = pedido['quantidade']
            subtotal = item['preco'] * quantidade
            
            # Formata cada linha do item
            codigo = str(item['id']).ljust(4)
            descricao = item['nome'][:22].ljust(22)
            qtd = str(quantidade).ljust(3)
            un = item.get('un', 'UN').ljust(2)
            vl_unit = f"{item['preco']:.2f}".rjust(6)
            vl_total = f"{subtotal:.2f}".rjust(7)
            
            itens += f"{codigo} {descricao} {qtd} {un} {vl_unit} {vl_total}\n"
        
        rodape = "-"*40 + "\n"
        
        if self.entrega:
            total_itens = sum(item['item']['preco'] * item['quantidade'] for item in self.pedido_atual)
            rodape += f"Subtotal{' ' * 30}R$ {total_itens:7.2f}\n"
            rodape += f"Taxa de Entrega{' ' * 24}R$ {self.taxa_entrega:7.2f}\n"
        
        rodape += f"TOTAL{' ' * 35}R$ {self.total_pedido:7.2f}\n"
        rodape += "-"*40 + "\n"
        rodape += f"FORMA DE PAGAMENTO: {self.forma_pagamento.upper()}\n"
        rodape += f"Valor Recebido: R$ {self.total_pedido:.2f}\n"
        rodape += f"Troco: R$ 0,00\n"
        rodape += "-"*40 + "\n"
        rodape += f"Protocolo de Autorização: {random.randint(100000000000000, 999999999999999)}\n"
        rodape += f"Data de Autorização: {data_hora}\n"
        rodape += f"Consulte pela Chave de Acesso:\n"
        rodape += f"NFe{now.year}{now.month:02d}{self.sobre_info['cnpj'].replace('.', '').replace('/', '').replace('-', '')}{modelo_nota}{serie_nota.zfill(3)}{str(numero_nota).zfill(9)}{codigo_verificacao}\n"
        rodape += "-"*40 + "\n"
        rodape += "Obrigado pela preferência!\n"
        rodape += "Volte sempre!"
        
        return cabecalho + itens + rodape

    def gerar_comprovante_simples(self, data_hora):
        """Gera um comprovante simples sem detalhes fiscais"""
        cabecalho = (
            f"{'CHURRASCARIA SABOR GAÚCHO'.center(40)}\n"
            f"{self.sobre_info['endereco'].center(40)}\n"
            f"{'-'*40}\n"
            f"Data: {data_hora}\n"
            f"{'-'*40}\n"
        )
        
        if self.cpf_cnpj:
            cabecalho += f"Cliente: {self.cpf_cnpj}\n"
            
        if self.entrega:
            numero_endereco = "s/n" if self.sem_numero else self.endereco_numero
            cabecalho += (
                f"\nENTREGA PARA:\n"
                f"{self.nome_cliente}\n"
                f"{self.endereco_rua}, {numero_endereco} - {self.endereco_bairro}\n"
                f"{'-'*40}\n"
            )
        
        itens = "ITEM                         QTD  VALOR\n"
        itens += "-"*40 + "\n"
        
        for pedido in self.pedido_atual:
            item = pedido['item']
            quantidade = pedido['quantidade']
            subtotal = item['preco'] * quantidade
            
            # Formata cada linha do item
            descricao = item['nome'][:25].ljust(25)
            qtd = str(quantidade).ljust(3)
            vl_total = f"{subtotal:.2f}".rjust(6)
            
            itens += f"{descricao} {qtd} {vl_total}\n"
        
        rodape = "-"*40 + "\n"
        
        if self.entrega:
            total_itens = sum(item['item']['preco'] * item['quantidade'] for item in self.pedido_atual)
            rodape += f"Subtotal: R$ {total_itens:.2f}\n"
            rodape += f"Taxa de Entrega: R$ {self.taxa_entrega:.2f}\n"
        
        rodape += f"TOTAL: R$ {self.total_pedido:.2f}\n"
        rodape += "-"*40 + "\n"
        rodape += f"FORMA DE PAGAMENTO: {self.forma_pagamento.upper()}\n"
        rodape += "-"*40 + "\n"
        rodape += "Obrigado pela preferência!\n"
        rodape += "Volte sempre!"
        
        return cabecalho + itens + rodape

    def imprimir_comprovante(self, tipo='nota_fiscal'):
        """Imprime o comprovante diretamente sem diálogo de salvar"""
        try:
            if not self.verificar_impressoras():
                return {"success": False, "message": "Nenhuma impressora encontrada!"}
            
            # Gera o comprovante conforme o tipo selecionado
            self.comprovante = self.gerar_comprovante(tipo)
            
            # Obtém a impressora padrão
            printer_name = win32print.GetDefaultPrinter()
            
            # Abre a impressora
            hprinter = win32print.OpenPrinter(printer_name)
            
            try:
                # Inicia um trabalho de impressão
                job_info = ("Comprovante Churrascaria", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                
                try:
                    win32print.StartPagePrinter(hprinter)
                    
                    # Converte o texto para bytes (UTF-8)
                    comprovante_bytes = self.comprovante.encode('utf-8')
                    
                    # Envia o texto para impressão
                    win32print.WritePrinter(hprinter, comprovante_bytes)
                    
                    win32print.EndPagePrinter(hprinter)
                finally:
                    win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)
            
            return {"success": True, "message": "Comprovante enviado para impressão!"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao imprimir: {str(e)}"}

    def salvar_comprovante(self, tipo='nota_fiscal'):
        """Salva o comprovante em um arquivo PDF"""
        try:
            # Gera o comprovante conforme o tipo selecionado
            comprovante_texto = self.gerar_comprovante(tipo)
            
            # Cria o PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            
            # Divide o texto em linhas e adiciona ao PDF
            for linha in comprovante_texto.split('\n'):
                pdf.cell(200, 5, txt=linha, ln=1, align='L')
            
            # Define o nome do arquivo
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"comprovante_{now}.pdf"
            caminho_completo = os.path.join(self.configuracoes["pasta_comprovantes"], nome_arquivo)
            
            # Salva o PDF
            pdf.output(caminho_completo)
            
            return {"success": True, "message": f"Comprovante salvo em: {caminho_completo}"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao salvar comprovante: {str(e)}"}

    def verificar_impressoras(self):
        """Verifica se há impressoras disponíveis"""
        try:
            impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            return len(impressoras) > 0
        except:
            return False

    # Funções para empresas
    def cadastrar_empresa(self, nome, cnpj, rua, bairro, numero, sem_numero):
        """Cadastra uma nova empresa"""
        try:
            # Valida o CNPJ
            cnpj = re.sub(r'[^0-9]', '', cnpj)
            if len(cnpj) != 14:
                return {"success": False, "message": "CNPJ inválido! Deve conter 14 dígitos."}
            
            # Formata o CNPJ
            cnpj_formatado = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
            
            # Verifica se a empresa já existe
            if any(empresa['cnpj'] == cnpj_formatado for empresa in self.empresas):
                return {"success": False, "message": "Já existe uma empresa cadastrada com este CNPJ!"}
            
            # Adiciona a empresa
            nova_empresa = {
                "id": len(self.empresas) + 1,
                "nome": nome,
                "cnpj": cnpj_formatado,
                "rua": rua,
                "bairro": bairro,
                "numero": numero,
                "sem_numero": sem_numero
            }
            
            self.empresas.append(nova_empresa)
            self.salvar_dados()
            
            return {"success": True, "message": "Empresa cadastrada com sucesso!"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao cadastrar empresa: {str(e)}"}

    def get_empresas(self):
        """Retorna a lista de empresas cadastradas"""
        return self.empresas

    def remover_empresa(self, index):
        """Remove uma empresa pelo índice"""
        try:
            index = int(index)  # Garante que o índice seja um inteiro
            if 0 <= index < len(self.empresas):
                # Remove também os pedidos associados a esta empresa
                empresa_id = self.empresas[index]['id']
                self.pedidos_empresas = [pedido for pedido in self.pedidos_empresas if pedido['empresa_id'] != empresa_id]
                
                # Remove a empresa
                del self.empresas[index]
                self.salvar_dados()
                return {"success": True, "message": "Empresa removida com sucesso!"}
            return {"success": False, "message": "Índice inválido"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def adicionar_pedido_empresa(self, empresa_index, data, funcionario, itens):
        """Adiciona um pedido corporativo para uma empresa"""
        try:
            empresa_index = int(empresa_index)  # Garante que o índice seja um inteiro
            if 0 <= empresa_index < len(self.empresas):
                empresa = self.empresas[empresa_index]
                
                # Converte os itens para o formato padrão com IDs
                itens_completos = []
                for item in itens:
                    # Busca o item no cardápio
                    item_cardapio = None
                    for categoria in self.cardapio.values():
                        for item_cat in categoria:
                            if item_cat['id'] == int(item['id']):
                                item_cardapio = item_cat.copy()
                                break
                        if item_cardapio:
                            break
                    
                    # Se não encontrou, cria um item personalizado
                    if not item_cardapio:
                        item_cardapio = {
                            "id": len(self.pedido_atual) + 1000,  # IDs altos para itens personalizados
                            "nome": "Item Corporativo",
                            "preco": 0,
                            "categoria": "corporativo",
                            "descricao": "Item corporativo",
                            "ncm": "2106.90.90",  # NCM genérico para alimentos
                            "un": "UN"
                        }
                    
                    itens_completos.append({
                        "item": item_cardapio,
                        "quantidade": int(item['quantidade'])
                    })
                
                novo_pedido = {
                    "empresa_id": empresa['id'],
                    "data": data,
                    "funcionario": funcionario,
                    "itens": itens_completos,
                    "total": sum(item['item']['preco'] * item['quantidade'] for item in itens_completos)
                }
                
                self.pedidos_empresas.append(novo_pedido)
                self.salvar_dados()
                
                return {"success": True, "message": "Pedido adicionado com sucesso!"}
            return {"success": False, "message": "Índice de empresa inválido"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_pedidos_empresa(self, empresa_index):
        """Retorna os pedidos de uma empresa específica"""
        try:
            empresa_index = int(empresa_index)  # Garante que o índice seja um inteiro
            if 0 <= empresa_index < len(self.empresas):
                empresa_id = self.empresas[empresa_index]['id']
                pedidos = [pedido for pedido in self.pedidos_empresas if pedido['empresa_id'] == empresa_id]
                return pedidos
            return []
        except Exception as e:
            print(f"Erro ao obter pedidos da empresa: {str(e)}")
            return []       

    def get_pedidos_empresa(self, empresa_index):
        """Retorna os pedidos de uma empresa específica"""
        try:
            empresa_index = int(empresa_index)  # Garante que o índice seja um inteiro
            if 0 <= empresa_index < len(self.empresas):
                empresa_id = self.empresas[empresa_index]['id']
                pedidos = [pedido for pedido in self.pedidos_empresas if pedido['empresa_id'] == empresa_id]
                return pedidos
            return []
        except Exception as e:
            print(f"Erro ao obter pedidos da empresa: {str(e)}")
            return []

    def remover_pedido_empresa(self, empresa_index, pedido_index):
        """Remove um pedido corporativo"""
        try:
            empresa_index = int(empresa_index)
            pedido_index = int(pedido_index)
            
            if 0 <= empresa_index < len(self.empresas):
                empresa_id = self.empresas[empresa_index]['id']
                
                # Encontra os pedidos da empresa
                pedidos_empresa = [i for i, pedido in enumerate(self.pedidos_empresas) if pedido['empresa_id'] == empresa_id]
                
                if 0 <= pedido_index < len(pedidos_empresa):
                    # Remove o pedido da lista geral
                    del self.pedidos_empresas[pedidos_empresa[pedido_index]]
                    self.salvar_dados()
                    return {"success": True, "message": "Pedido removido com sucesso!"}
            return {"success": False, "message": "Índice inválido"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def gerar_relatorio_empresa(self, empresa_index, imprimir=False):
        """Gera um relatório de pedidos para uma empresa"""
        try:
            empresa_index = int(empresa_index)  # Garante que o índice seja um inteiro
            if 0 <= empresa_index < len(self.empresas):
                empresa = self.empresas[empresa_index]
                pedidos = self.get_pedidos_empresa(empresa_index)
                
                if not pedidos:
                    return {"success": False, "message": "Nenhum pedido encontrado para esta empresa!"}
                
                # Calcula o total
                total = sum(pedido['total'] for pedido in pedidos)
                
                # Gera o relatório
                now = datetime.now()
                data_hora = now.strftime("%d/%m/%Y %H:%M:%S")
                
                # Corrigido: Verifica se há pedidos antes de calcular min/max
                datas_pedidos = [pedido['data'] for pedido in pedidos]
                periodo = f"{min(datas_pedidos)} a {max(datas_pedidos)}" if pedidos else "Nenhum pedido"
                
                relatorio = (
                    f"{'RELATÓRIO DE PEDIDOS'.center(40)}\n"
                    f"{'CHURRASCARIA SABOR GAÚCHO'.center(40)}\n"
                    f"{'-'*40}\n"
                    f"Empresa: {empresa['nome']}\n"
                    f"CNPJ: {empresa['cnpj']}\n"
                    f"Endereço: {empresa['rua']}, {'s/n' if empresa['sem_numero'] else empresa['numero']} - {empresa['bairro']}\n"
                    f"Data do Relatório: {data_hora}\n"
                    f"{'-'*40}\n"
                    f"Período: {periodo}\n"
                    f"{'-'*40}\n"
                    f"DATA       FUNCIONÁRIO          ITENS{' ' * 20}TOTAL\n"
                    f"{'-'*40}\n"
                )
                
                for pedido in pedidos:
                    data = datetime.strptime(pedido['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
                    funcionario = pedido['funcionario'][:20].ljust(20)
                    
                    # Formata os itens do pedido
                    itens = ", ".join([f"{item['item']['nome']} (x{item['quantidade']})" for item in pedido['itens']])
                    
                    relatorio += f"{data} {funcionario} {itens[:40].ljust(40)} R$ {pedido['total']:.2f}\n"
                
                relatorio += (
                    f"{'-'*40}\n"
                    f"{'TOTAL:'.rjust(70)} R$ {total:.2f}\n"
                    f"{'-'*40}\n"
                    f"Obrigado pela preferência!\n"
                )
                
                if imprimir:
                    # Imprime o relatório
                    if not self.verificar_impressoras():
                        return {"success": False, "message": "Nenhuma impressora encontrada!"}
                    
                    printer_name = win32print.GetDefaultPrinter()
                    hprinter = win32print.OpenPrinter(printer_name)
                    
                    try:
                        job_info = ("Relatório Empresa", None, "RAW")
                        job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                        
                        try:
                            win32print.StartPagePrinter(hprinter)
                            win32print.WritePrinter(hprinter, relatorio.encode('utf-8'))
                            win32print.EndPagePrinter(hprinter)
                        finally:
                            win32print.EndDocPrinter(hprinter)
                    finally:
                        win32print.ClosePrinter(hprinter)
                    
                    return {"success": True, "message": "Relatório impresso com sucesso!"}
                else:
                    # Salva o relatório em um arquivo PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    
                    for linha in relatorio.split('\n'):
                        pdf.cell(200, 5, txt=linha, ln=1, align='L')
                    
                    nome_arquivo = f"relatorio_{empresa['nome']}_{now.strftime('%Y%m%d')}.pdf"
                    caminho_completo = os.path.join(self.configuracoes["pasta_relatorios_empresas"], nome_arquivo)
                    pdf.output(caminho_completo)
                    
                    return {"success": True, "message": f"Relatório salvo em: {caminho_completo}"}
            
            return {"success": False, "message": "Índice de empresa inválido"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao gerar relatório: {str(e)}"}

    # Funções para relatórios
    def get_relatorio_dia(self, data):
        """Retorna o relatório de vendas de um dia específico"""
        try:
            vendas_dia = [venda for venda in self.vendas_dia if venda['data_hora'].startswith(data)]
            
            return {
                "data": data,
                "vendas": vendas_dia,
                "total": sum(venda['total'] for venda in vendas_dia)
            }
        except Exception as e:
            print(f"Erro ao gerar relatório diário: {str(e)}")
            return {
                "data": data,
                "vendas": [],
                "total": 0
            }

    def get_relatorio_mes(self, mes):
        """Retorna o relatório de vendas de um mês específico"""
        try:
            # Agrupa vendas por dia
            vendas_por_dia = {}
            
            for venda in self.vendas_dia:
                venda_data = venda['data_hora'][:10]  # YYYY-MM-DD
                if venda_data.startswith(mes):
                    if venda_data not in vendas_por_dia:
                        vendas_por_dia[venda_data] = {
                            "data": venda_data,
                            "quantidade": 0,
                            "total": 0
                        }
                    
                    vendas_por_dia[venda_data]["quantidade"] += 1
                    vendas_por_dia[venda_data]["total"] += venda['total']
            
            # Converte para lista ordenada por data
            vendas = sorted(vendas_por_dia.values(), key=lambda x: x['data'])
            
            return {
                "mes": mes,
                "vendas": vendas,
                "total": sum(dia['total'] for dia in vendas)
            }
        except Exception as e:
            print(f"Erro ao gerar relatório mensal: {str(e)}")
            return {
                "mes": mes,
                "vendas": [],
                "total": 0
            }

    def exportar_relatorio_dia_csv(self, data):
        """Exporta o relatório diário para um arquivo CSV"""
        try:
            relatorio = self.get_relatorio_dia(data)
            
            # Define o nome do arquivo
            nome_arquivo = f"relatorio_dia_{data}.csv"
            caminho_completo = os.path.join(self.configuracoes["pasta_relatorios_excel"], nome_arquivo)
            
            # Cria o conteúdo CSV
            with open(caminho_completo, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Escreve o cabeçalho
                writer.writerow(["Data", "Hora", "Cliente", "Itens", "Total"])
                
                # Escreve os dados
                for venda in relatorio['vendas']:
                    data_hora = datetime.fromisoformat(venda['data_hora'])
                    data_formatada = data_hora.strftime("%d/%m/%Y")
                    hora_formatada = data_hora.strftime("%H:%M:%S")
                    
                    # Formata os itens
                    itens = ", ".join([f"{item['nome']} (x{item['quantidade']})" for item in venda['itens']])
                    
                    writer.writerow([
                        data_formatada,
                        hora_formatada,
                        venda['cliente'] or "Não identificado",
                        itens,
                        f"R$ {venda['total']:.2f}"
                    ])
                
                # Escreve o total
                writer.writerow([])
                writer.writerow(["", "", "Total:", f"R$ {relatorio['total']:.2f}"])
            
            return {"success": True, "message": f"Relatório exportado para: {caminho_completo}"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao exportar relatório: {str(e)}"}

    def exportar_relatorio_mes_csv(self, mes):
        """Exporta o relatório mensal para um arquivo CSV"""
        try:
            relatorio = self.get_relatorio_mes(mes)
            
            # Define o nome do arquivo
            nome_arquivo = f"relatorio_mes_{mes}.csv"
            caminho_completo = os.path.join(self.configuracoes["pasta_relatorios_excel"], nome_arquivo)
            
            # Cria o conteúdo CSV
            with open(caminho_completo, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Escreve o cabeçalho
                writer.writerow(["Data", "Quantidade de Vendas", "Total"])
                
                # Escreve os dados
                for venda in relatorio['vendas']:
                    data = datetime.strptime(venda['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
                    writer.writerow([
                        data,
                        venda['quantidade'],
                        f"R$ {venda['total']:.2f}"
                    ])
                
                # Escreve o total
                writer.writerow([])
                writer.writerow(["Total:", "", f"R$ {relatorio['total']:.2f}"])
            
            return {"success": True, "message": f"Relatório exportado para: {caminho_completo}"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao exportar relatório: {str(e)}"}

    # Funções para configurações
    def get_configuracoes(self):
        """Retorna as configurações atuais do sistema"""
        return self.configuracoes

    def salvar_configuracoes(self, novas_configuracoes):
        """Salva as novas configurações do sistema"""
        try:
            self.configuracoes.update(novas_configuracoes)
            self.salvar_dados()
            
            # Cria as pastas se não existirem
            os.makedirs(self.configuracoes["pasta_comprovantes"], exist_ok=True)
            os.makedirs(self.configuracoes["pasta_relatorios_empresas"], exist_ok=True)
            os.makedirs(self.configuracoes["pasta_relatorios_excel"], exist_ok=True)
            
            return {"success": True, "message": "Configurações salvas com sucesso!"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao salvar configurações: {str(e)}"}

    def selecionar_pasta(self):
        """Abre um diálogo para selecionar uma pasta"""
        try:
            # Usa Tkinter para abrir o diálogo de seleção de pasta
            root = tk.Tk()
            root.withdraw()  # Esconde a janela principal
            pasta = filedialog.askdirectory()
            root.destroy()
            
            return pasta
        except Exception as e:
            print(f"Erro ao selecionar pasta: {str(e)}")
            return None

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