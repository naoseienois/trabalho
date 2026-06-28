"""
pagamento.py - Simulador completo de pagamentos (PIX, Cartão, Dinheiro)
"""
import random
import string
from datetime import datetime

from db import get_connection, fechar
from utils import titulo, aguardar, limpar_tela, formatar_moeda, linha


# ═══════════════════════════════════════════════════════════════════════════════
#  Funções auxiliares de geração
# ═══════════════════════════════════════════════════════════════════════════════

def _gerar_codigo_pix() -> str:
    chars = string.ascii_uppercase + string.digits
    return "PIX-" + "".join(random.choices(chars, k=20))


def _gerar_qrcode_ascii() -> str:
    """QR Code fictício em ASCII para fins de demonstração."""
    linhas = [
        "  ┌──────────────────────┐",
        "  │ ██  ██ ████ ██  ██  │",
        "  │ ██████ ░░░░ ██████  │",
        "  │ ██  ██ ████ ██  ██  │",
        "  │  QR CODE FICTÍCIO   │",
        "  │   (Apenas Demo)     │",
        "  │ ██  ██ ░░░░ ██  ██  │",
        "  │ ██████ ████ ██████  │",
        "  │ ██  ██ ░░░░ ██  ██  │",
        "  └──────────────────────┘",
    ]
    return "\n".join(linhas)


def _registrar_pagamento(id_pedido: int, metodo: str, valor: float, status: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO pagamentos (id_pedido, metodo, valor, status, data_pagamento) "
        "VALUES (%s, %s, %s, %s, %s)",
        (id_pedido, metodo, valor, status, datetime.now() if status == "aprovado" else None)
    )
    conn.commit()
    fechar(conn, cur)


def _criar_pedido(id_usuario: int, itens: list, valor_total: float,
                  tipo_entrega: str, forma_pagamento: str,
                  endereco: dict | None = None) -> int:
    """
    Insere pedido, itens_pedido, endereço (se houver) e limpa o carrinho.
    Retorna o id_pedido criado.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO pedidos (id_usuario, tipo_entrega, status, valor_total, forma_pagamento) "
        "VALUES (%s, %s, 'enviado', %s, %s)",
        (id_usuario, tipo_entrega, valor_total, forma_pagamento)
    )
    id_pedido = cur.lastrowid

    for item in itens:
        cur.execute(
            "INSERT INTO itens_pedido (id_pedido, id_comida, quantidade, preco_unitario) "
            "VALUES (%s, %s, %s, %s)",
            (id_pedido, item["id_comida"], item["quantidade"], item["preco_unitario"])
        )

    if endereco:
        cur.execute(
            "INSERT INTO enderecos (id_pedido, bairro, rua, numero, complemento, valor_entrega) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (id_pedido, endereco["bairro"], endereco["rua"],
             endereco["numero"], endereco.get("complemento", ""), endereco["valor_entrega"])
        )

    # Esvazia o carrinho
    cur.execute("SELECT id_carrinho FROM carrinho WHERE id_usuario=%s", (id_usuario,))
    row = cur.fetchone()
    if row:
        cur.execute("DELETE FROM itens_carrinho WHERE id_carrinho=%s", (row[0],))

    conn.commit()
    fechar(conn, cur)
    return id_pedido


# ═══════════════════════════════════════════════════════════════════════════════
#  Métodos de pagamento
# ═══════════════════════════════════════════════════════════════════════════════

def _pagamento_pix(valor_total: float) -> bool:
    """Simula pagamento via PIX. Retorna True se aprovado."""
    codigo_pix = _gerar_codigo_pix()
    limpar_tela()
    titulo("PAGAMENTO VIA PIX")
    print(f"  Valor a pagar: {formatar_moeda(valor_total)}")
    print()
    print(_gerar_qrcode_ascii())
    print()
    print(f"  Código PIX (Copia e Cola):")
    print(f"  {codigo_pix}")
    print()
    print(linha())
    print("  ⚠  SIMULAÇÃO ACADÊMICA - Escolha uma opção:")
    print("  [1] Confirmar pagamento")
    print("  [2] Cancelar pagamento")
    escolha = input("  > ").strip()
    return escolha == "1"


def _pagamento_cartao(valor_total: float) -> bool:
    """Simula pagamento via cartão. Retorna True se aprovado."""
    limpar_tela()
    titulo("PAGAMENTO VIA CARTÃO")
    print(f"  Valor a pagar: {formatar_moeda(valor_total)}")
    print()
    print("  Informe os dados do cartão (apenas simulação - não armazenados):")
    nome_cartao = input("  Nome no cartão: ").strip()
    numero      = input("  Número do cartão: ").strip()
    validade    = input("  Validade (MM/AA): ").strip()
    cvv         = input("  CVV: ").strip()
    print()
    print(linha())
    print("  ⚠  SIMULAÇÃO ACADÊMICA - Escolha uma opção:")
    print("  [1] Aprovar pagamento")
    print("  [2] Recusar pagamento")
    escolha = input("  > ").strip()
    if escolha == "1":
        print("\n  ✔  Pagamento aprovado!")
        aguardar()
        return True
    else:
        print("\n  ✗  Pagamento recusado. Tente novamente ou escolha outro método.")
        aguardar()
        return False


def _pagamento_dinheiro(valor_total: float) -> bool:
    """Simula pagamento em dinheiro (somente atendente). Retorna True se aprovado."""
    limpar_tela()
    titulo("PAGAMENTO EM DINHEIRO")
    print(f"  Valor total: {formatar_moeda(valor_total)}")
    print()
    while True:
        val_str = input("  Valor recebido do cliente (R$): ").strip().replace(",", ".")
        try:
            recebido = float(val_str)
        except ValueError:
            print("  ✗  Valor inválido. Digite um número.")
            continue
        if recebido < valor_total:
            print(f"  ✗  Valor insuficiente. Faltam {formatar_moeda(valor_total - recebido)}.")
            continue
        troco = recebido - valor_total
        if troco > 0:
            print(f"  ✔  Troco a devolver: {formatar_moeda(troco)}")
        else:
            print("  ✔  Valor exato. Sem troco.")
        aguardar()
        return True


# ═══════════════════════════════════════════════════════════════════════════════
#  Fluxo principal de compra
# ═══════════════════════════════════════════════════════════════════════════════

def _obter_endereco() -> dict:
    """Coleta endereço e calcula taxa de entrega (simulado)."""
    limpar_tela()
    titulo("ENDEREÇO DE ENTREGA")
    bairro      = input("  Bairro: ").strip()
    rua         = input("  Rua: ").strip()
    numero      = input("  Número: ").strip()
    complemento = input("  Complemento (opcional): ").strip()
    # Taxa simulada: fixa em R$ 5,00 para demonstração
    taxa = 5.00
    print(f"\n  Taxa de entrega calculada: {formatar_moeda(taxa)}")
    aguardar()
    return {"bairro": bairro, "rua": rua, "numero": numero,
            "complemento": complemento, "valor_entrega": taxa}


def tela_comprar(usuario: dict, itens_carrinho: list, subtotal: float) -> bool:
    """
    Fluxo completo de finalização de compra.
    Retorna True se o pedido foi criado com sucesso.
    """
    cargo = usuario["cargo"]
    id_usuario = usuario["id_usuario"]

    # ── Tipo de entrega ──────────────────────────────────────────────────────
    limpar_tela()
    titulo("FINALIZAR PEDIDO - Tipo de Entrega")
    print("  [1] Retirada no balcão")
    print("  [2] Entrega no endereço")
    print("  [0] Voltar ao carrinho")
    op = input("  > ").strip()
    if op == "0":
        return False

    endereco = None
    taxa_entrega = 0.0
    if op == "2":
        endereco = _obter_endereco()
        taxa_entrega = endereco["valor_entrega"]
        tipo_entrega = "entrega"
    elif op == "1":
        tipo_entrega = "retirada"
    else:
        print("  ⚠  Opção inválida.")
        aguardar()
        return False

    valor_total = subtotal + taxa_entrega

    # ── Resumo ───────────────────────────────────────────────────────────────
    limpar_tela()
    titulo("RESUMO DO PEDIDO")
    for item in itens_carrinho:
        sub = float(item["preco_unitario"]) * item["quantidade"]
        print(f"  {item['nome']:<30} x{item['quantidade']:>3}  {formatar_moeda(sub):>10}")
    print(linha("─", 50))
    print(f"  {'Subtotal':<34} {formatar_moeda(subtotal):>10}")
    if taxa_entrega:
        print(f"  {'Taxa de entrega':<34} {formatar_moeda(taxa_entrega):>10}")
    print(f"  {'TOTAL':<34} {formatar_moeda(valor_total):>10}")
    print()

    # ── Método de pagamento ──────────────────────────────────────────────────
    titulo("MÉTODO DE PAGAMENTO")
    print("  [1] PIX")
    print("  [2] Cartão")
    if cargo == "atendente":
        print("  [3] Dinheiro (somente atendente)")
    print("  [0] Voltar ao carrinho")
    metodo_op = input("  > ").strip()

    if metodo_op == "0":
        return False

    aprovado = False
    metodo_str = ""

    if metodo_op == "1":
        metodo_str = "pix"
        aprovado = _pagamento_pix(valor_total)
    elif metodo_op == "2":
        metodo_str = "cartao"
        while True:
            aprovado = _pagamento_cartao(valor_total)
            if aprovado:
                break
            limpar_tela()
            print("  Deseja tentar novamente ou escolher outro método?")
            print("  [1] Tentar novamente  [2] Outro método  [0] Cancelar")
            r = input("  > ").strip()
            if r == "1":
                continue
            elif r == "2":
                return tela_comprar(usuario, itens_carrinho, subtotal)
            else:
                return False
    elif metodo_op == "3" and cargo == "atendente":
        metodo_str = "dinheiro"
        aprovado = _pagamento_dinheiro(valor_total)
    else:
        print("  ⚠  Opção inválida.")
        aguardar()
        return False

    # ── Registrar pedido ─────────────────────────────────────────────────────
    if aprovado:
        try:
            id_pedido = _criar_pedido(
                id_usuario, itens_carrinho, valor_total,
                tipo_entrega, metodo_str, endereco
            )
            _registrar_pagamento(id_pedido, metodo_str, valor_total, "aprovado")

            limpar_tela()
            titulo("✔ PEDIDO CONFIRMADO!")
            print(f"  Nº do Pedido: #{id_pedido}")
            print(f"  Total pago:   {formatar_moeda(valor_total)}")
            print(f"  Método:       {metodo_str.upper()}")
            print(f"  Entrega:      {tipo_entrega.capitalize()}")
            if endereco:
                print(f"  Endereço:     {endereco['rua']}, {endereco['numero']} - {endereco['bairro']}")
            print()
            print("  Seu pedido foi enviado para a cozinha!")
            aguardar()
            return True
        except Exception as e:
            print(f"  ✗  Erro ao registrar pedido: {e}")
            print("  O carrinho foi mantido.")
            aguardar()
            return False
    else:
        limpar_tela()
        print("  Pagamento não confirmado. O carrinho foi mantido.")
        aguardar()
        return False
