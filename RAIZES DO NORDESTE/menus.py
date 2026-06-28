"""
menus.py - Menus por cargo: cliente, atendente, cozinheiro, gerente, totem
"""
from db import get_connection, fechar
from utils import titulo, aguardar, limpar_tela, formatar_moeda, linha
from cardapio import tela_cardapio
from carrinho import tela_carrinho


# ═══════════════════════════════════════════════════════════════════════════════
#  Status do pedido
# ═══════════════════════════════════════════════════════════════════════════════

def tela_status_pedido(usuario: dict):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id_pedido, data_pedido, status, valor_total, forma_pagamento, tipo_entrega "
        "FROM pedidos WHERE id_usuario=%s ORDER BY data_pedido DESC LIMIT 10",
        (usuario["id_usuario"],)
    )
    pedidos = cur.fetchall()
    fechar(conn, cur)

    limpar_tela()
    titulo("STATUS DOS PEDIDOS")
    if not pedidos:
        print("  Nenhum pedido encontrado.")
    for p in pedidos:
        print(f"  Pedido #{p['id_pedido']}  |  {p['status'].upper()}")
        print(f"  Data: {p['data_pedido']}  |  Total: {formatar_moeda(float(p['valor_total']))}")
        print(f"  Entrega: {p['tipo_entrega']}  |  Pagamento: {p['forma_pagamento']}")
        print(linha("·", 50))
    aguardar()


# ═══════════════════════════════════════════════════════════════════════════════
#  Fila de pedidos (cozinheiro)
# ═══════════════════════════════════════════════════════════════════════════════

def tela_fila_pedidos():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT p.id_pedido, u.nome AS cliente, p.data_pedido,
                  p.status, p.valor_total, p.tipo_entrega
           FROM pedidos p JOIN usuarios u ON p.id_usuario=u.id_usuario
           WHERE p.status IN ('enviado','fazendo')
           ORDER BY p.data_pedido ASC"""
    )
    pedidos = cur.fetchall()
    fechar(conn, cur)

    limpar_tela()
    titulo("FILA DE PEDIDOS - COZINHA")
    if not pedidos:
        print("  Nenhum pedido na fila.")
        aguardar()
        return

    for p in pedidos:
        print(f"\n  Pedido #{p['id_pedido']}  |  Cliente: {p['cliente']}  |  {p['status'].upper()}")
        print(f"  Data: {p['data_pedido']}  |  Total: {formatar_moeda(float(p['valor_total']))}")
        print(f"  Entrega: {p['tipo_entrega']}")

        # Itens do pedido
        conn2 = get_connection()
        cur2 = conn2.cursor(dictionary=True)
        cur2.execute(
            """SELECT c.nome, ip.quantidade
               FROM itens_pedido ip JOIN comidas c ON ip.id_comida=c.id_comida
               WHERE ip.id_pedido=%s""",
            (p["id_pedido"],)
        )
        itens = cur2.fetchall()
        fechar(conn2, cur2)
        for i in itens:
            print(f"    - {i['nome']} x{i['quantidade']}")
        print(linha("·", 50))

    print("\n  Opções:")
    print("  [1] Iniciar preparo de pedido (status → fazendo)")
    print("  [2] Marcar pedido como pronto")
    print("  [0] Voltar")
    op = input("  > ").strip()

    if op in ("1", "2"):
        id_str = input("  Número do pedido: ").strip()
        if id_str.isdigit():
            novo_status = "fazendo" if op == "1" else "pronto"
            conn3 = get_connection()
            cur3 = conn3.cursor()
            cur3.execute(
                "UPDATE pedidos SET status=%s WHERE id_pedido=%s",
                (novo_status, int(id_str))
            )
            conn3.commit()
            fechar(conn3, cur3)

            if novo_status == "pronto":
                # Desconta estoque
                _descontar_estoque(int(id_str))

            print(f"  ✔  Pedido #{id_str} → {novo_status.upper()}")
            aguardar()


def _descontar_estoque(id_pedido: int):
    """Desconta os ingredientes do estoque ao marcar pedido como pronto."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id_comida, quantidade FROM itens_pedido WHERE id_pedido=%s",
        (id_pedido,)
    )
    itens = cur.fetchall()
    fechar(conn, cur)

    for item in itens:
        conn2 = get_connection()
        cur2 = conn2.cursor(dictionary=True)
        cur2.execute(
            "SELECT id_ingrediente, quantidade FROM receita WHERE id_comida=%s",
            (item["id_comida"],)
        )
        receitas = cur2.fetchall()
        fechar(conn2, cur2)

        for r in receitas:
            consumo = r["quantidade"] * item["quantidade"]
            conn3 = get_connection()
            cur3 = conn3.cursor()
            cur3.execute(
                "UPDATE ingredientes SET quantidade = GREATEST(0, quantidade - %s) "
                "WHERE id_ingrediente=%s",
                (consumo, r["id_ingrediente"])
            )
            conn3.commit()
            fechar(conn3, cur3)


# ═══════════════════════════════════════════════════════════════════════════════
#  Gerente - Relatórios e Gestão
# ═══════════════════════════════════════════════════════════════════════════════

def tela_relatorio_financeiro():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT
            SUM(CASE WHEN DATE(data_pedido)=CURDATE() THEN 1 ELSE 0 END)          AS qtd_dia,
            SUM(CASE WHEN MONTH(data_pedido)=MONTH(NOW()) THEN 1 ELSE 0 END)       AS qtd_mes,
            SUM(CASE WHEN DATE(data_pedido)=CURDATE() THEN valor_total ELSE 0 END) AS val_dia,
            SUM(CASE WHEN MONTH(data_pedido)=MONTH(NOW()) THEN valor_total ELSE 0 END) AS val_mes
           FROM pedidos WHERE status != 'cancelado'"""
    )
    totais = cur.fetchone()

    cur.execute(
        "SELECT forma_pagamento, COUNT(*) AS cnt FROM pedidos "
        "GROUP BY forma_pagamento ORDER BY cnt DESC LIMIT 1"
    )
    top_pgto = cur.fetchone()

    cur.execute(
        """SELECT c.nome, SUM(ip.quantidade) AS total_vendido
           FROM itens_pedido ip JOIN comidas c ON ip.id_comida=c.id_comida
           GROUP BY ip.id_comida ORDER BY total_vendido DESC LIMIT 1"""
    )
    top_comida = cur.fetchone()
    fechar(conn, cur)

    limpar_tela()
    titulo("RELATÓRIO FINANCEIRO")
    print(f"  Pedidos hoje:      {totais['qtd_dia'] or 0}")
    print(f"  Pedidos no mês:    {totais['qtd_mes'] or 0}")
    print(f"  Arrecadado hoje:   {formatar_moeda(float(totais['val_dia'] or 0))}")
    print(f"  Arrecadado no mês: {formatar_moeda(float(totais['val_mes'] or 0))}")
    if top_pgto:
        print(f"  Método mais usado: {top_pgto['forma_pagamento'].upper()}")
    if top_comida:
        print(f"  Comida mais vendida: {top_comida['nome']} ({top_comida['total_vendido']} unid.)")
    aguardar()


def tela_relatorio_estoque():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT nome, quantidade, unidade, quantidade_minima FROM ingredientes ORDER BY nome"
    )
    ing = cur.fetchall()
    fechar(conn, cur)

    limpar_tela()
    titulo("RELATÓRIO DE ESTOQUE")
    print(f"  {'Ingrediente':<25} {'Qtd':>10}  {'Unidade':<10}  {'Mínimo':>8}")
    print(linha())
    for i in ing:
        alerta = " ⚠ BAIXO" if float(i["quantidade"]) <= float(i["quantidade_minima"]) else ""
        print(f"  {i['nome']:<25} {float(i['quantidade']):>10.2f}  {i['unidade']:<10}  "
              f"{float(i['quantidade_minima']):>8.2f}{alerta}")
    aguardar()


# ═══════════════════════════════════════════════════════════════════════════════
#  Menus por cargo
# ═══════════════════════════════════════════════════════════════════════════════

def menu_cliente(usuario: dict) -> bool:
    """Retorna False quando o usuário faz logout."""
    while True:
        limpar_tela()
        titulo(f"MENU CLIENTE  |  {usuario['nome']}")
        print("  [1] Cardápio")
        print("  [2] Carrinho")
        print("  [3] Status do pedido")
        print("  [9] Sair (logout)")
        op = input("  > ").strip()
        if op == "1":
            tela_cardapio(usuario)
        elif op == "2":
            tela_carrinho(usuario)
        elif op == "3":
            tela_status_pedido(usuario)
        elif op == "9":
            return False
        else:
            print("  ⚠  Opção inválida.")
            aguardar()


def menu_atendente(usuario: dict) -> bool:
    while True:
        limpar_tela()
        titulo(f"MENU ATENDENTE  |  {usuario['nome']}")
        print("  [1] Cardápio")
        print("  [2] Carrinho (aceita dinheiro)")
        print("  [3] Status do pedido")
        print("  [9] Sair (logout)")
        op = input("  > ").strip()
        if op == "1":
            tela_cardapio(usuario)
        elif op == "2":
            tela_carrinho(usuario)
        elif op == "3":
            tela_status_pedido(usuario)
        elif op == "9":
            return False
        else:
            print("  ⚠  Opção inválida.")
            aguardar()


def menu_cozinheiro(usuario: dict) -> bool:
    while True:
        limpar_tela()
        titulo(f"MENU COZINHEIRO  |  {usuario['nome']}")
        print("  [1] Fila de pedidos")
        print("  [9] Sair (logout)")
        op = input("  > ").strip()
        if op == "1":
            tela_fila_pedidos()
        elif op == "9":
            return False
        else:
            print("  ⚠  Opção inválida.")
            aguardar()


def menu_gerente(usuario: dict) -> bool:
    while True:
        limpar_tela()
        titulo(f"MENU GERENTE  |  {usuario['nome']}")
        print("  [1] Cardápio")
        print("  [2] Fila de pedidos")
        print("  [3] Relatório financeiro")
        print("  [4] Relatório de estoque")
        print("  [9] Sair (logout)")
        op = input("  > ").strip()
        if op == "1":
            tela_cardapio(usuario)
        elif op == "2":
            tela_fila_pedidos()
        elif op == "3":
            tela_relatorio_financeiro()
        elif op == "4":
            tela_relatorio_estoque()
        elif op == "9":
            return False
        else:
            print("  ⚠  Opção inválida.")
            aguardar()


def menu_totem(usuario: dict) -> bool:
    while True:
        limpar_tela()
        titulo(f"MENU TOTEM  |  {usuario['nome']}")
        print("  [1] Cardápio")
        print("  [2] Carrinho")
        print("  [3] Status do pedido")
        print("  [9] Sair")
        op = input("  > ").strip()
        if op == "1":
            tela_cardapio(usuario)
        elif op == "2":
            tela_carrinho(usuario)
        elif op == "3":
            tela_status_pedido(usuario)
        elif op == "9":
            print("  Tem certeza que deseja sair? (ok / não)")
            if input("  > ").strip().lower() == "ok":
                return False
        else:
            print("  ⚠  Opção inválida.")
            aguardar()


def redirecionar_menu(usuario: dict) -> bool:
    cargo = usuario["cargo"]
    rotas = {
        "cliente":     menu_cliente,
        "atendente":   menu_atendente,
        "cozinheiro":  menu_cozinheiro,
        "gerente":     menu_gerente,
        "totem":       menu_totem,
    }
    func = rotas.get(cargo)
    if func:
        return func(usuario)
    print(f"  ✗  Cargo desconhecido: {cargo}")
    aguardar()
    return False
