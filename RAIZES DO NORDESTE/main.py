"""
main.py - Ponto de entrada do sistema de restaurante
Execução: python main.py
"""
from autenticacao import tela_inicio
from menus import redirecionar_menu
from utils import limpar_tela, titulo


def main():
    limpar_tela()
    while True:
        usuario = tela_inicio()
        if usuario:
            redirecionar_menu(usuario)


if __name__ == "__main__":
    main()
