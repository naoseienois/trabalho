"""
db.py - Conexão com o banco de dados MySQL
"""
import mysql.connector
from mysql.connector import Error

# ── Configuração ── altere conforme seu ambiente ──────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "sua_senha_aqui",
    "database": "restaurante",
    "charset":  "utf8mb4",
}
# ─────────────────────────────────────────────────────────────────


def get_connection():
    """Retorna uma conexão aberta com o MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"[ERRO DB] Não foi possível conectar: {e}")
        raise


def fechar(conn, cursor=None):
    """Fecha cursor e conexão com segurança."""
    try:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
    except Error:
        pass
