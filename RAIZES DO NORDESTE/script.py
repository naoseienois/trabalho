
import os, shutil

proj = '/home/user/restaurante'
os.makedirs(proj, exist_ok=True)

# Mapa: arquivo anexado → nome correto para o projeto
mapa = {
    'file:20': ('autenticacao.py',   '/home/user/autenticacao.py'),
    'file:19': ('cardapio.py',       None),  # será lido dos anexos
    'file:22': ('carrinho.py',       None),
    'file:21': ('db.py',             None),
    'file:24': ('main.py',           None),
    'file:23': ('menus.py',          None),
    'file:25': ('pagamento.py',      None),
    'file:30': ('utils.py',          None),
    'file:31': ('requirements.txt',  None),
}

# Arquivos já existentes no sandbox (versão mais recente)
existentes = {
    'autenticacao.py': '/home/user/autenticacao.py',
    'cardapio.py':     '/home/user/cardapio.py',
    'carrinho.py':     '/home/user/carrinho.py',
    'db.py':           '/home/user/db.py',
    'main.py':         '/home/user/main.py',
    'menus.py':        '/home/user/menus.py',
    'pagamento.py':    '/home/user/pagamento.py',
    'utils.py':        '/home/user/utils.py',
    'requirements.txt': '/home/user/requirements.txt',
}

for nome, origem in existentes.items():
    shutil.copy2(origem, f'{proj}/{nome}')
    print(f"  ✔  {nome}")
