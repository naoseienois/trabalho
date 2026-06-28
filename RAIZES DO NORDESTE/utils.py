"""
utils.py - Funções utilitárias compartilhadas
"""
import os
import hashlib
import random
import string
from datetime import datetime


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def hash_senha(senha: str) -> str:
    """Gera hash bcrypt-compatível via hashlib (SHA-256 + salt fixo para demo).
    Em produção, use bcrypt: pip install bcrypt."""
    salt = "RESTAURANTE_SALT_2024"
    return hashlib.sha256((senha + salt).encode()).hexdigest()


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    return hash_senha(senha) == hash_armazenado


def gerar_codigo_8_digitos() -> str:
    return "".join(random.choices(string.digits, k=8))


def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def linha(char="─", tamanho=50) -> str:
    return char * tamanho


def titulo(texto: str):
    print()
    print(linha())
    print(f"  {texto}")
    print(linha())


def aguardar():
    input("\n  Pressione ENTER para continuar...")
