
proj = '/home/user/restaurante'

# ─── banco_de_dados.sql ATUALIZADO com comidas de cuscuz ─────────────────────
sql = """-- ============================================================
--  BANCO DE DADOS - SISTEMA DE RESTAURANTE (Cuscuz Nordestino)
--  Arquivo: banco_de_dados.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS restaurante CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE restaurante;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario       INT AUTO_INCREMENT PRIMARY KEY,
    nome             VARCHAR(100) NOT NULL UNIQUE,
    email            VARCHAR(150) NOT NULL UNIQUE,
    senha_hash       VARCHAR(255) NOT NULL,
    cargo            ENUM('cliente','atendente','cozinheiro','gerente','totem') DEFAULT 'cliente',
    bloqueado        BOOLEAN DEFAULT FALSE,
    tentativas_login INT DEFAULT 0,
    ultimo_login     DATETIME,
    criado_em        DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS codigos_email (
    id_codigo    INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario   INT NOT NULL,
    codigo       CHAR(8) NOT NULL,
    tipo         ENUM('cadastro','redefinir','alterar_email') NOT NULL,
    validade     DATETIME NOT NULL,
    tentativas   INT DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS comidas (
    id_comida    INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nome         VARCHAR(120) NOT NULL UNIQUE,
    descricao    TEXT,
    preco        DECIMAL(10,2) NOT NULL,
    disponivel   BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);

CREATE TABLE IF NOT EXISTS ingredientes (
    id_ingrediente    INT AUTO_INCREMENT PRIMARY KEY,
    nome              VARCHAR(80) NOT NULL UNIQUE,
    quantidade        DECIMAL(10,2) DEFAULT 0,
    unidade           VARCHAR(20),
    quantidade_minima DECIMAL(10,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS receita (
    id_receita       INT AUTO_INCREMENT PRIMARY KEY,
    id_comida        INT NOT NULL,
    id_ingrediente   INT NOT NULL,
    quantidade       DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_comida)      REFERENCES comidas(id_comida) ON DELETE CASCADE,
    FOREIGN KEY (id_ingrediente) REFERENCES ingredientes(id_ingrediente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS carrinho (
    id_carrinho INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario  INT NOT NULL UNIQUE,
    criado_em   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS itens_carrinho (
    id_item          INT AUTO_INCREMENT PRIMARY KEY,
    id_carrinho      INT NOT NULL,
    id_comida        INT NOT NULL,
    quantidade       INT NOT NULL DEFAULT 1,
    preco_unitario   DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_carrinho) REFERENCES carrinho(id_carrinho) ON DELETE CASCADE,
    FOREIGN KEY (id_comida)   REFERENCES comidas(id_comida)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido       INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario      INT NOT NULL,
    data_pedido     DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_entrega    ENUM('retirada','entrega') NOT NULL,
    status          ENUM('enviado','fazendo','pronto','entregando','entregue','cancelado') DEFAULT 'enviado',
    valor_total     DECIMAL(10,2) NOT NULL,
    forma_pagamento ENUM('pix','cartao','dinheiro') NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id_item          INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido        INT NOT NULL,
    id_comida        INT NOT NULL,
    quantidade       INT NOT NULL DEFAULT 1,
    preco_unitario   DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_comida) REFERENCES comidas(id_comida)
);

CREATE TABLE IF NOT EXISTS enderecos (
    id_endereco   INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido     INT NOT NULL UNIQUE,
    bairro        VARCHAR(100),
    rua           VARCHAR(100),
    numero        VARCHAR(20),
    complemento   VARCHAR(100),
    valor_entrega DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pagamentos (
    id_pagamento   INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido      INT NOT NULL,
    metodo         ENUM('pix','cartao','dinheiro') NOT NULL,
    valor          DECIMAL(10,2) NOT NULL,
    status         ENUM('pendente','aprovado','recusado') DEFAULT 'pendente',
    data_pagamento DATETIME,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE
);

-- ============================================================
--  DADOS INICIAIS
-- ============================================================

INSERT IGNORE INTO categorias (nome) VALUES ('Cuscuz Salgado'), ('Cuscuz Doce');

-- ── Ingredientes ──────────────────────────────────────────────────────────────
INSERT IGNORE INTO ingredientes (nome, quantidade, unidade, quantidade_minima) VALUES
    ('Flocão de milho',        50.0,  'kg',     5.0),
    ('Manteiga',               20.0,  'kg',     2.0),
    ('Queijo coalho',          15.0,  'kg',     2.0),
    ('Ovo',                   200.0,  'unidade',20.0),
    ('Carne de sol desfiada',  20.0,  'kg',     3.0),
    ('Frango desfiado',        20.0,  'kg',     3.0),
    ('Requeijão',              10.0,  'kg',     1.0),
    ('Mussarela',              15.0,  'kg',     2.0),
    ('Milho verde',            10.0,  'kg',     1.0),
    ('Orégano',                 2.0,  'kg',     0.2),
    ('Leite condensado',       20.0,  'lata',   3.0),
    ('Coco ralado',            10.0,  'kg',     1.0),
    ('Calabresa',              15.0,  'kg',     2.0),
    ('Cebola',                 10.0,  'kg',     1.0),
    ('Tomate',                 10.0,  'kg',     1.0);

-- ── Comidas ───────────────────────────────────────────────────────────────────
-- Categoria 1 = Cuscuz Salgado  |  Categoria 2 = Cuscuz Doce
INSERT IGNORE INTO comidas (id_categoria, nome, descricao, preco, disponivel) VALUES
    (1, 'Cuscuz Nordestino Tradicional',
        'Flocão de milho, manteiga, queijo coalho, ovo e carne de sol desfiada',
        18.90, TRUE),
    (1, 'Cuscuz com Frango Cremoso',
        'Flocão de milho, frango desfiado, requeijão, mussarela, milho e orégano',
        22.50, TRUE),
    (2, 'Cuscuz Doce com Leite Condensado',
        'Flocão de milho, leite condensado, coco ralado e manteiga',
        14.90, TRUE),
    (1, 'Cuscuz Calabresa Especial',
        'Flocão de milho, calabresa, cebola, tomate, queijo mussarela e manteiga',
        24.90, TRUE);

-- ── Receitas (ingredientes por comida) ───────────────────────────────────────
-- id_comida 1: Cuscuz Nordestino Tradicional
INSERT IGNORE INTO receita (id_comida, id_ingrediente, quantidade) VALUES
    (1, 1, 0.25),  -- Flocão de milho  250g
    (1, 2, 0.02),  -- Manteiga          20g
    (1, 3, 0.05),  -- Queijo coalho     50g
    (1, 4, 1.0),   -- Ovo               1 unidade
    (1, 5, 0.1);   -- Carne de sol     100g

-- id_comida 2: Cuscuz com Frango Cremoso
INSERT IGNORE INTO receita (id_comida, id_ingrediente, quantidade) VALUES
    (2, 1, 0.25),  -- Flocão de milho  250g
    (2, 6, 0.1),   -- Frango desfiado  100g
    (2, 7, 0.05),  -- Requeijão         50g
    (2, 8, 0.05),  -- Mussarela         50g
    (2, 9, 0.05),  -- Milho verde       50g
    (2, 10, 0.005);-- Orégano            5g

-- id_comida 3: Cuscuz Doce com Leite Condensado
INSERT IGNORE INTO receita (id_comida, id_ingrediente, quantidade) VALUES
    (3, 1, 0.25),  -- Flocão de milho  250g
    (3, 11, 0.1),  -- Leite condensado 100g
    (3, 12, 0.05), -- Coco ralado       50g
    (3, 2, 0.02);  -- Manteiga          20g

-- id_comida 4: Cuscuz Calabresa Especial
INSERT IGNORE INTO receita (id_comida, id_ingrediente, quantidade) VALUES
    (4, 1, 0.25),  -- Flocão de milho  250g
    (4, 13, 0.1),  -- Calabresa        100g
    (4, 14, 0.05), -- Cebola            50g
    (4, 15, 0.05), -- Tomate            50g
    (4, 8, 0.05),  -- Mussarela         50g
    (4, 2, 0.02);  -- Manteiga          20g

-- ============================================================
--  CONTA GERENTE PADRÃO
--  Usuário : gerente
--  Senha   : admin1234
-- ============================================================
INSERT IGNORE INTO usuarios (nome, email, senha_hash, cargo)
VALUES (
    'gerente',
    'gerente@restaurante.com',
    SHA2(CONCAT('admin1234', 'RESTAURANTE_SALT_2024'), 256),
    'gerente'
);
"""

with open(f'{proj}/banco_de_dados.sql', 'w', encoding='utf-8') as f:
    f.write(sql)
print("banco_de_dados.sql atualizado com as 4 comidas de cuscuz!")
