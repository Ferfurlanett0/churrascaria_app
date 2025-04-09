def imprimir_comprovante(conteudo, impressora=None):
    """
    Lógica para impressão real ou simulação
    """
    if impressora:
        # Código específico para sua impressora
        pass
    else:
        # Gera arquivo de texto como fallback
        with open("comprovante.txt", "w") as f:
            f.write(conteudo)