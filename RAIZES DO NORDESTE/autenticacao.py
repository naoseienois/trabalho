"""
autenticacao.py - Login, Cadastro e Redefinição de Senha
"""
import re
import time
from datetime import datetime, timedelta

from db import get_connection, fechar
from utils import (hash_senha, verificar_senha, gerar_codigo_8_digitos,
                   titulo, aguardar, limpar_tela, linha)


# ── helpers internos ──────────────────────────────────────────────────────────

def _validar_email(email: str) -> bool:
    return bool(re.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", email))


def _email_simular_envio(email: str, codigo: str, tipo: str):
    """Simula envio de e-mail (em produção integre SMTP)."""
    print(f"\n  [SIMULAÇÃO E-MAIL] Para: {email}")
    print(f"  Tipo: {tipo}  |  Código: {codigo}  (válido por 60s)")


def _salvar_codigo(id_usuario: int, codigo: str, tipo: str):
    conn = get_connection()
    cur = conn.cursor()
    validade = datetime.now() + timedelta(seconds=60)
    cur.execute(
        "DELETE FROM codigos_email WHERE id_usuario=%s AND tipo=%s",
        (id_usuario, tipo)
    )
    cur.execute(
        "INSERT INTO codigos_email (id_usuario, codigo, tipo, validade, tentativas) "
        "VALUES (%s, %s, %s, %s, 0)",
        (id_usuario, codigo, tipo, validade)
    )
    conn.commit()
    fechar(conn, cur)


def _verificar_codigo(id_usuario: int, codigo_digitado: str, tipo: str) -> str:
    """
    Retorna 'ok', 'expirado', 'errado', 'bloqueado' ou 'nao_encontrado'.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM codigos_email WHERE id_usuario=%s AND tipo=%s",
        (id_usuario, tipo)
    )
    reg = cur.fetchone()
    fechar(conn, cur)

    if not reg:
        return "nao_encontrado"
    if reg["tentativas"] >= 5:
        return "bloqueado"
    if datetime.now() > reg["validade"]:
        return "expirado"

    # Incrementa tentativas
    conn2 = get_connection()
    cur2 = conn2.cursor()
    cur2.execute(
        "UPDATE codigos_email SET tentativas=tentativas+1 WHERE id_codigo=%s",
        (reg["id_codigo"],)
    )
    conn2.commit()
    fechar(conn2, cur2)

    if codigo_digitado.strip() == reg["codigo"]:
        return "ok"
    return "errado"


# ── Fluxo principal ───────────────────────────────────────────────────────────

def tela_inicio() -> dict | None:
    """Ponto de entrada. Retorna dados do usuário logado ou None."""
    while True:
        limpar_tela()
        titulo("SISTEMA DE RESTAURANTE")
        print("  Você possui cadastro?  (sim / não)")
        resp = input("  > ").strip().lower()

        if resp == "sim":
            usuario = tela_login()
            if usuario:
                return usuario
        elif resp == "não" or resp == "nao":
            tela_cadastro()
        else:
            print("  ⚠  Resposta inválida. Esta é uma pergunta de sim ou não.")
            aguardar()


def tela_login() -> dict | None:
    """Retorna dict do usuário logado ou None (para voltar)."""
    while True:
        limpar_tela()
        titulo("LOGIN")
        print("  Digite 'voltar' a qualquer momento para retornar.")
        identificador = input("  Nome ou E-mail: ").strip()
        if identificador.lower() == "voltar":
            return None

        senha = input("  Senha: ").strip()
        if senha.lower() == "voltar":
            return None

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM usuarios WHERE (nome=%s OR email=%s)",
            (identificador, identificador)
        )
        usuario = cur.fetchone()
        fechar(conn, cur)

        if not usuario:
            print("  ✗  Conta não encontrada. Tente novamente.")
            aguardar()
            continue

        if usuario["bloqueado"]:
            print("  ✗  Conta bloqueada. Aguarde 15 minutos ou contate o gerente.")
            aguardar()
            continue

        if not verificar_senha(senha, usuario["senha_hash"]):
            # Incrementa tentativas
            novas = usuario["tentativas_login"] + 1
            bloquear = novas >= 5
            conn2 = get_connection()
            cur2 = conn2.cursor()
            cur2.execute(
                "UPDATE usuarios SET tentativas_login=%s, bloqueado=%s WHERE id_usuario=%s",
                (novas, bloquear, usuario["id_usuario"])
            )
            conn2.commit()
            fechar(conn2, cur2)
            msg = f"  ✗  Senha incorreta. Tentativa {novas}/5."
            if bloquear:
                msg += "\n  ⚠  Conta bloqueada por 15 minutos."
            print(msg)
            aguardar()
            continue

        # Login bem-sucedido: zera tentativas e registra último login
        conn3 = get_connection()
        cur3 = conn3.cursor()
        cur3.execute(
            "UPDATE usuarios SET tentativas_login=0, ultimo_login=%s WHERE id_usuario=%s",
            (datetime.now(), usuario["id_usuario"])
        )
        conn3.commit()
        fechar(conn3, cur3)

        print(f"\n  ✔  Bem-vindo, {usuario['nome']}! ({usuario['cargo']})")
        aguardar()
        return usuario

    # Opção redefinir senha (acessada quando digitada como comando)


def tela_redefinir_senha():
    """Fluxo completo de redefinição de senha via código por e-mail."""
    while True:
        limpar_tela()
        titulo("REDEFINIR SENHA - Informe o E-mail")
        email = input("  E-mail: ").strip()
        if email.lower() == "voltar":
            return

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        usuario = cur.fetchone()
        fechar(conn, cur)

        if not usuario:
            print("  ✗  Nenhuma conta encontrada com esse e-mail.")
            aguardar()
            continue

        codigo = gerar_codigo_8_digitos()
        _salvar_codigo(usuario["id_usuario"], codigo, "redefinir")
        _email_simular_envio(email, codigo, "Redefinição de senha")

        # Verificar código
        for _ in range(5):
            limpar_tela()
            titulo("REDEFINIR SENHA - Código de Verificação")
            print(f"  Um código de 8 dígitos foi enviado para {email}.")
            print("  Digite 'voltar' para cancelar.")
            digitado = input("  Código: ").strip()
            if digitado.lower() == "voltar":
                return

            resultado = _verificar_codigo(usuario["id_usuario"], digitado, "redefinir")
            if resultado == "ok":
                # Solicitar nova senha
                while True:
                    limpar_tela()
                    titulo("REDEFINIR SENHA - Nova Senha")
                    nova = input("  Nova senha (mín. 8 caracteres): ").strip()
                    if nova.lower() == "voltar":
                        return
                    if len(nova) < 8:
                        print("  ✗  A senha deve ter no mínimo 8 caracteres.")
                        aguardar()
                        continue
                    conn4 = get_connection()
                    cur4 = conn4.cursor()
                    cur4.execute(
                        "UPDATE usuarios SET senha_hash=%s WHERE id_usuario=%s",
                        (hash_senha(nova), usuario["id_usuario"])
                    )
                    conn4.commit()
                    fechar(conn4, cur4)
                    print("  ✔  Senha redefinida com sucesso!")
                    aguardar()
                    return
            elif resultado == "expirado":
                print("  ✗  Código expirado. Solicite um novo.")
                aguardar()
                return
            elif resultado == "bloqueado":
                print("  ✗  Muitas tentativas. Tente novamente em 15 minutos.")
                aguardar()
                return
            else:
                print("  ✗  Código incorreto. Tente novamente.")
                aguardar()

        print("  ✗  Todas as tentativas esgotadas.")
        aguardar()


def tela_cadastro():
    """Cadastro de novo usuário com validação e confirmação por e-mail."""
    while True:
        limpar_tela()
        titulo("CADASTRO")
        print("  Digite 'voltar' para retornar.")

        nome = input("  Nome de usuário: ").strip()
        if nome.lower() == "voltar":
            return

        email = input("  E-mail: ").strip()
        if email.lower() == "voltar":
            return

        if not _validar_email(email):
            print("  ✗  Formato de e-mail inválido.")
            aguardar()
            continue

        # Verificar duplicatas
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_usuario FROM usuarios WHERE email=%s", (email,))
        if cur.fetchone():
            fechar(conn, cur)
            print("  ✗  E-mail já cadastrado. Tente outro.")
            aguardar()
            continue
        cur.execute("SELECT id_usuario FROM usuarios WHERE nome=%s", (nome,))
        if cur.fetchone():
            fechar(conn, cur)
            print("  ✗  Nome já cadastrado. Tente outro.")
            aguardar()
            continue
        fechar(conn, cur)

        senha = input("  Senha (mín. 8 caracteres): ").strip()
        if senha.lower() == "voltar":
            return
        if len(senha) < 8:
            print("  ✗  A senha deve ter no mínimo 8 caracteres.")
            aguardar()
            continue

        # Inserir temporariamente para gerar ID e enviar código
        conn2 = get_connection()
        cur2 = conn2.cursor()
        cur2.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, cargo) VALUES (%s,%s,%s,'cliente')",
            (nome, email, hash_senha(senha))
        )
        conn2.commit()
        id_novo = cur2.lastrowid
        fechar(conn2, cur2)

        codigo = gerar_codigo_8_digitos()
        _salvar_codigo(id_novo, codigo, "cadastro")
        _email_simular_envio(email, codigo, "Confirmação de cadastro")

        validado = False
        for _ in range(5):
            limpar_tela()
            titulo("CADASTRO - Confirmação de E-mail")
            print(f"  Código enviado para {email}. Válido por 60 segundos.")
            digitado = input("  Código: ").strip()
            resultado = _verificar_codigo(id_novo, digitado, "cadastro")
            if resultado == "ok":
                validado = True
                break
            elif resultado in ("expirado", "bloqueado"):
                print(f"  ✗  {resultado.replace('_',' ').capitalize()}. Conta removida.")
                aguardar()
                break
            else:
                print("  ✗  Código incorreto.")
                aguardar()

        if not validado:
            # Remove conta não confirmada
            conn3 = get_connection()
            cur3 = conn3.cursor()
            cur3.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_novo,))
            conn3.commit()
            fechar(conn3, cur3)
            return

        print("  ✔  Conta criada com sucesso! Faça login.")
        aguardar()
        return
