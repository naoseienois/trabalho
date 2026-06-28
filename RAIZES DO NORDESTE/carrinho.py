"""
carrinho.py - Visualização e gerenciamento do carrinho de compras
"""
from db import get_connection, fechar
from utils import titulo, aguardar, limpar_tela, formatar_moeda, linha
from pagamento import tela_comprar


def _obter_itens(id_usuario: int) -> tuple[list, float]:
    """Retorna (lista_de_itens, subtotal)."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_carrinho FROM carrinho WHERE id_usuario=%s", (id_usuario,))
    row = cur.fetchone()
    if not row:
        fechar(conn, cur)
        return [], 0.0
    id_carrinho = row["id_carrinho"]
    cur.execute(
        """SELECT ic.id_item, ic.id_comida, c.nome, ic.quantidade, ic.preco_unitario
           FROM itens_carrinho ic
           JOIN comidas c ON ic.id_comida = c.id_comida
           WHERE ic.id_carrinho = %s""",
        (id_carrinho,)
    )
    itens = cur.fetchall()
    fechar(conn, cur)
    subtotal = sum(float(i["preco_unitario"]) * i["quantidade"] for i in itens)
    return itens, subtotal


def _max_porcoes(id_comida: int) -> int:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT r.quantidade AS qtd_receita, i.quantidade AS qtd_estoque
           FROM receita r JOIN ingredientes i ON r.id_ingrediente=i.id_ingrediente
           WHERE r.id_comida=%s""",
        (id_comida,)
    )
    rows = cur.fetchall()
    fechar(conn, cur)
    if not rows:
        return 999
    return int(min(r["qtd_estoque"] / r["qtd_receita"] for r in rows))


def tela_carrinho(usuario: dict):
    """Menu principal do carrinho."""
    while True:
        itens, subtotal = _obter_itens(usuario["id_usuario"])
        limpar_tela()
        titulo("CARRINHO")

        if not itens:
            print("  Seu carrinho está vazio.")
            print("  [0] Voltar")
            if input("  > ").strip() == "0":
                return
            continue

        for item in itens:
            sub = float(item["preco_unitario"]) * item["quantidade"]
            print(f"  ID:{item['id_comida']:>3}  {item['nome']:<30} "
                  f"x{item['quantidade']:>3}  {formatar_moeda(sub):>10}")
        print(linha())
        print(f"  {'SUBTOTAL':<38} {formatar_moeda(subtotal):>10}")
        print()
        print("  [1] Comprar")
        print("  [2] Remover item")
        print("  [3] Mudar quantidade")
        print("  [0] Voltar ao menu")
        op = input("  > ").strip()

        if op == "0":
            return
        elif op == "1":
            sucesso = tela_comprar(usuario, itens, subtotal)
            if sucesso:
                return  # Carrinho esvaziado, volta ao menu
        elif op == "2":
            _remover_item(usuario["id_usuario"])
        elif op == "3":
            _mudar_quantidade(usuario["id_usuario"])
        else:
            print("  ⚠  Opção inválida.")
            aguardar()


def _remover_item(id_usuario: int):
    limpar_tela()
    titulo("REMOVER ITEM")
    id_str = input("  ID da comida a remover (ou 'voltar'): ").strip()
    if id_str.lower() == "voltar":
        return
    if not id_str.isdigit():
        print("  ✗  Isso não é um número.")
        aguardar()
        return

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_carrinho FROM carrinho WHERE id_usuario=%s", (id_usuario,))
    row = cur.fetchone()
    if not row:
        fechar(conn, cur)
        return
    id_carrinho = row["id_carrinho"]
    cur.execute(
        "SELECT id_item, id_comida FROM itens_carrinho "
        "WHERE id_carrinho=%s AND id_comida=%s",
        (id_carrinho, int(id_str))
    )
    item = cur.fetchone()
    fechar(conn, cur)

    if not item:
        print("  ✗  ID não encontrado no carrinho.")
        aguardar()
        return

    print("  Deseja remover este item? (sim / não)")
    if input("  > ").strip().lower() == "sim":
        conn2 = get_connection()
        cur2 = conn2.cursor()
        cur2.execute("DELETE FROM itens_carrinho WHERE id_item=%s", (item["id_item"],))
        conn2.commit()
        fechar(conn2, cur2)
        print("  ✔  Item removido.")
        aguardar()


def _mudar_quantidade(id_usuario: int):
    limpar_tela()
    titulo("MUDAR QUANTIDADE")
    id_str = input("  ID da comida (ou 'voltar'): ").strip()
    if id_str.lower() == "voltar":
        return
    if not id_str.isdigit():
        print("  ✗  Isso não é um número.")
        aguardar()
        return

    id_comida = int(id_str)
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_carrinho FROM carrinho WHERE id_usuario=%s", (id_usuario,))
    row = cur.fetchone()
    if not row:
        fechar(conn, cur)
        return
    id_carrinho = row["id_carrinho"]
    cur.execute(
        "SELECT ic.id_item, ic.quantidade, c.nome, ic.preco_unitario "
        "FROM itens_carrinho ic JOIN comidas c ON ic.id_comida=c.id_comida "
        "WHERE ic.id_carrinho=%s AND ic.id_comida=%s",
        (id_carrinho, id_comida)
    )
    item = cur.fetchone()
    fechar(conn, cur)

    if not item:
        print("  ✗  ID não encontrado no carrinho.")
        aguardar()
        return

    max_p = _max_porcoes(id_comida)
    print(f"  {item['nome']} - Quantidade atual: {item['quantidade']}")
    print(f"  Quantidade máxima disponível: {max_p}")
    qtd_str = input("  Nova quantidade (ou 'voltar'): ").strip()
    if qtd_str.lower() == "voltar":
        return
    if not qtd_str.isdigit():
        print("  ✗  Isso não é um número.")
        aguardar()
        return
    qtd = int(qtd_str)
    if qtd <= 0:
        print("  ✗  A quantidade deve ser maior que zero.")
        aguardar()
        return
    if qtd > max_p:
        print(f"  ✗  Número máximo de pratos: {max_p}.")
        aguardar()
        return

    subtotal = float(item["preco_unitario"]) * qtd
    print(f"  Novo subtotal: {formatar_moeda(subtotal)}")
    print("  Confirmar mudança? (sim / não)")
    if input("  > ").strip().lower() == "sim":
        conn2 = get_connection()
        cur2 = conn2.cursor()
        cur2.execute(
            "UPDATE itens_carrinho SET quantidade=%s WHERE id_item=%s",
            (qtd, item["id_item"])
        )
        conn2.commit()
        fechar(conn2, cur2)
        print("  ✔  Quantidade atualizada.")
        aguardar()
