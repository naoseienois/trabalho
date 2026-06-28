"""
cardapio.py - Exibição do cardápio e adição ao carrinho
"""
from db import get_connection, fechar
from utils import titulo, aguardar, limpar_tela, formatar_moeda, linha


def _max_porcoes(id_comida: int) -> int:
    """Calcula a quantidade máxima de porções possíveis com o estoque atual."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT r.quantidade AS qtd_receita, i.quantidade AS qtd_estoque
           FROM receita r
           JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
           WHERE r.id_comida = %s""",
        (id_comida,)
    )
    rows = cur.fetchall()
    fechar(conn, cur)
    if not rows:
        return 999
    return int(min(r["qtd_estoque"] / r["qtd_receita"] for r in rows))


def exibir_cardapio(cargo: str):
    """Exibe o cardápio completo. Gerente e cozinheiro veem estoque."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT c.id_comida, c.nome, c.descricao, c.preco, c.disponivel,
                  cat.nome AS categoria
           FROM comidas c
           JOIN categorias cat ON c.id_categoria = cat.id_categoria
           ORDER BY cat.nome, c.nome"""
    )
    comidas = cur.fetchall()
    fechar(conn, cur)

    limpar_tela()
    titulo("CARDÁPIO")
    cat_atual = ""
    for c in comidas:
        if c["categoria"] != cat_atual:
            cat_atual = c["categoria"]
            print(f"\n  [{cat_atual.upper()}]")
        status = "✔ Disponível" if c["disponivel"] else "✗ Indisponível"
        print(f"  ID:{c['id_comida']:>3}  {c['nome']:<30} {formatar_moeda(float(c['preco'])):>10}  {status}")
        if cargo in ("gerente", "cozinheiro"):
            max_p = _max_porcoes(c["id_comida"])
            print(f"         Estoque para {max_p} porção(ões)")


def tela_cardapio(usuario: dict) -> None:
    """Menu de cardápio com opção de adicionar ao carrinho."""
    cargo = usuario["cargo"]
    while True:
        exibir_cardapio(cargo)
        print("\n  Deseja adicionar alguma comida ao carrinho? (sim / não / voltar)")
        resp = input("  > ").strip().lower()
        if resp in ("não", "nao", "voltar", "n"):
            return
        if resp == "sim":
            _adicionar_ao_carrinho(usuario)
        else:
            print("  ⚠  Resposta inválida.")
            aguardar()


def _adicionar_ao_carrinho(usuario: dict):
    """Solicita ID e quantidade e insere no carrinho."""
    id_usuario = usuario["id_usuario"]

    # Garante que o carrinho existe
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_carrinho FROM carrinho WHERE id_usuario=%s", (id_usuario,))
    row = cur.fetchone()
    if row:
        id_carrinho = row[0]
    else:
        cur.execute("INSERT INTO carrinho (id_usuario) VALUES (%s)", (id_usuario,))
        conn.commit()
        id_carrinho = cur.lastrowid
    fechar(conn, cur)

    while True:
        limpar_tela()
        titulo("ADICIONAR AO CARRINHO")
        print("  Digite o ID da comida ou 'voltar'.")
        id_str = input("  ID da comida: ").strip()
        if id_str.lower() == "voltar":
            return

        if not id_str.isdigit():
            print("  ✗  Isso não é um número. Somente aceitamos números.")
            aguardar()
            continue

        id_comida = int(id_str)
        conn2 = get_connection()
        cur2 = conn2.cursor(dictionary=True)
        cur2.execute("SELECT * FROM comidas WHERE id_comida=%s", (id_comida,))
        comida = cur2.fetchone()
        fechar(conn2, cur2)

        if not comida:
            print("  ✗  Esta comida não existe. Tente novamente.")
            aguardar()
            continue
        if not comida["disponivel"]:
            print(f"  ✗  '{comida['nome']}' não está disponível no momento.")
            aguardar()
            continue

        max_p = _max_porcoes(id_comida)
        print(f"  ✔  {comida['nome']} - {formatar_moeda(float(comida['preco']))} por unidade")
        print(f"  Quantidade máxima disponível: {max_p}")
        print("  Digite a quantidade ou 'voltar'.")
        qtd_str = input("  Quantidade: ").strip()
        if qtd_str.lower() == "voltar":
            continue
        if not qtd_str.isdigit():
            print("  ✗  Isso não é um número. Somente aceitamos números.")
            aguardar()
            continue
        qtd = int(qtd_str)
        if qtd <= 0:
            print("  ✗  A quantidade deve ser maior que zero.")
            aguardar()
            continue
        if qtd > max_p:
            print(f"  ✗  Número máximo de pratos disponíveis: {max_p}.")
            aguardar()
            continue

        subtotal = float(comida["preco"]) * qtd
        print(f"\n  Subtotal: {formatar_moeda(subtotal)}")
        print("  Colocar no carrinho? (sim / não)")
        conf = input("  > ").strip().lower()
        if conf == "sim":
            conn3 = get_connection()
            cur3 = conn3.cursor()
            # Se já existe esse item no carrinho, atualiza quantidade
            cur3.execute(
                "SELECT id_item, quantidade FROM itens_carrinho WHERE id_carrinho=%s AND id_comida=%s",
                (id_carrinho, id_comida)
            )
            ex = cur3.fetchone()
            if ex:
                cur3.execute(
                    "UPDATE itens_carrinho SET quantidade=%s WHERE id_item=%s",
                    (ex[1] + qtd, ex[0])
                )
            else:
                cur3.execute(
                    "INSERT INTO itens_carrinho (id_carrinho, id_comida, quantidade, preco_unitario) "
                    "VALUES (%s,%s,%s,%s)",
                    (id_carrinho, id_comida, qtd, comida["preco"])
                )
            conn3.commit()
            fechar(conn3, cur3)
            print(f"  ✔  '{comida['nome']}' adicionado ao carrinho!")
            aguardar()
            return
