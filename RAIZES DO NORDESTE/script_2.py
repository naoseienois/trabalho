
proj = '/home/user/restaurante'

readme = """# 🌽 Sistema de Restaurante — Cuscuz Nordestino

Sistema completo de gerenciamento de restaurante desenvolvido em **Python 3** com banco de dados **MySQL**.  
Inclui cadastro de usuários, cardápio, carrinho, simulação de pagamentos (PIX, Cartão e Dinheiro) e fila de cozinha.

---

## 📁 Estrutura do Projeto

```
restaurante/
├── main.py              → Ponto de entrada — execute este arquivo
├── autenticacao.py      → Login, Cadastro e Redefinição de Senha
├── cardapio.py          → Exibição do cardápio e adição ao carrinho
├── carrinho.py          → Gerenciamento do carrinho de compras
├── pagamento.py         → Simulador de pagamentos (PIX / Cartão / Dinheiro)
├── menus.py             → Menus separados por cargo
├── db.py                → Conexão com o MySQL
├── utils.py             → Funções utilitárias compartilhadas
├── banco_de_dados.sql   → Script SQL completo (tabelas + dados iniciais)
├── requirements.txt     → Dependências Python
└── README.md            → Este arquivo
```

---

## ⚙️ Pré-requisitos

- Python 3.10 ou superior
- MySQL 8.0 ou superior
- pip (gerenciador de pacotes Python)

---

## 🗄️ Como Importar o Banco de Dados

### Passo 1 — Abrir o terminal do MySQL

**Windows (Prompt de Comando):**
```bash
mysql -u root -p
```

**Linux / Mac:**
```bash
sudo mysql -u root -p
```
Digite sua senha do MySQL quando solicitado.

---

### Passo 2 — Importar o arquivo SQL

**Opção A — Direto no terminal (mais fácil):**

No terminal (fora do MySQL), navegue até a pasta do projeto e execute:
```bash
mysql -u root -p < banco_de_dados.sql
```

**Opção B — Dentro do MySQL:**
```sql
SOURCE /caminho/completo/para/banco_de_dados.sql;
```
Exemplo no Windows:
```sql
SOURCE C:/Users/SeuNome/restaurante/banco_de_dados.sql;
```

---

### Passo 3 — Verificar se foi importado corretamente
```sql
USE restaurante;
SHOW TABLES;
SELECT nome, preco FROM comidas;
```

Você deve ver as 4 comidas do cardápio:
```
+-----------------------------------+-------+
| nome                              | preco |
+-----------------------------------+-------+
| Cuscuz Nordestino Tradicional     | 18.90 |
| Cuscuz com Frango Cremoso         | 22.50 |
| Cuscuz Doce com Leite Condensado  | 14.90 |
| Cuscuz Calabresa Especial         | 24.90 |
+-----------------------------------+-------+
```

---

## 🔧 Configuração do Projeto

### Passo 1 — Instalar dependências Python
```bash
pip install -r requirements.txt
```

### Passo 2 — Configurar a conexão em `db.py`

Abra o arquivo `db.py` e altere as credenciais:
```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "SUA_SENHA_MYSQL",   # ← coloque sua senha aqui
    "database": "restaurante",
}
```

### Passo 3 — Executar o sistema
```bash
python main.py
```

---

## 👤 Conta Gerente (criada automaticamente)

O banco de dados já cria uma conta gerente padrão para acesso imediato:

| Campo  | Valor                     |
|--------|---------------------------|
| Usuário | `gerente`                |
| E-mail  | `gerente@restaurante.com`|
| Senha   | `admin1234`              |
| Cargo   | `gerente`                |

> ⚠️ Recomenda-se alterar a senha após o primeiro acesso.

---

## 👥 Cargos e Permissões

| Cargo      | Cardápio | Carrinho | Dinheiro | Cozinha | Relatórios |
|------------|:--------:|:--------:|:--------:|:-------:|:----------:|
| cliente    | ✔        | ✔        | ✗        | ✗       | ✗          |
| atendente  | ✔        | ✔        | ✔        | ✗       | ✗          |
| cozinheiro | ✔        | ✗        | ✗        | ✔       | ✗          |
| gerente    | ✔        | ✔        | ✗        | ✔       | ✔          |
| totem      | ✔        | ✔        | ✗        | ✗       | ✗          |

---

## 🍽️ Cardápio

| ID | Nome                              | Preço    | Categoria      |
|----|-----------------------------------|----------|----------------|
| 1  | Cuscuz Nordestino Tradicional     | R$ 18,90 | Cuscuz Salgado |
| 2  | Cuscuz com Frango Cremoso         | R$ 22,50 | Cuscuz Salgado |
| 3  | Cuscuz Doce com Leite Condensado  | R$ 14,90 | Cuscuz Doce    |
| 4  | Cuscuz Calabresa Especial         | R$ 24,90 | Cuscuz Salgado |

---

## 💳 Métodos de Pagamento (Simulação Acadêmica)

- **PIX** → Gera código PIX fictício + QR Code ASCII. Botões: Confirmar / Cancelar.
- **Cartão** → Solicita dados do cartão *(não armazenados)*. Botões: Aprovar / Recusar.
- **Dinheiro** *(somente atendente)* → Calcula troco automaticamente.

Após pagamento aprovado o sistema:
1. Registra o pedido no banco de dados
2. Envia para a fila da cozinha
3. Esvazia o carrinho automaticamente

---

## 🔒 Segurança

- Senhas armazenadas como **hash SHA-256 com salt** *(produção: usar bcrypt)*
- Bloqueio de conta após **5 tentativas** erradas de login (15 min)
- Código de verificação por e-mail com **validade de 5 minutos** e **5 tentativas**
- Validação de formato de e-mail por expressão regular

---

## 🗃️ Tabelas do Banco de Dados

| Tabela            | Descrição                                       |
|-------------------|-------------------------------------------------|
| `usuarios`        | Contas de usuário com cargos                    |
| `codigos_email`   | Códigos temporários de verificação              |
| `categorias`      | Categorias do cardápio                          |
| `comidas`         | Itens do cardápio                               |
| `ingredientes`    | Estoque de ingredientes                         |
| `receita`         | Relação N:N entre comidas e ingredientes        |
| `carrinho`        | Carrinho ativo por usuário                      |
| `itens_carrinho`  | Itens dentro do carrinho                        |
| `pedidos`         | Pedidos realizados                              |
| `itens_pedido`    | Itens de cada pedido                            |
| `enderecos`       | Endereços de entrega                            |
| `pagamentos`      | Registros de pagamentos                         |

---

## 📝 Observações

> Projeto desenvolvido para fins **acadêmicos e educacionais**.  
> O envio de e-mail é **simulado no terminal** — o código aparece em destaque na tela.  
> Os dados de cartão **não são armazenados** no banco de dados.

---

*Desenvolvido para o Sistema Municipal de Educação de Uauá — BA*
"""

with open(f'{proj}/README.md', 'w', encoding='utf-8') as f:
    f.write(readme)
print("README.md criado!")

# Verificar todos os arquivos do projeto
import os
print("\nArquivos do projeto:")
for arq in sorted(os.listdir(proj)):
    size = os.path.getsize(f"{proj}/{arq}")
    print(f"  {arq:<30} {size:>7} bytes")
