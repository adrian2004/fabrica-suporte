"""Aplica a marca Fabrica Suporte e os dados do servidor no codigo-fonte do RustDesk.

Uso (a partir da raiz do repositorio, com submodulos baixados):
    FS_SERVER=meu.dominio.com FS_KEY=chave_publica python fabrica/apply_branding.py

FS_SERVER: IP ou dominio do servidor hbbs (ID server). O relay e descoberto pelo hbbs (-r).
FS_KEY:    conteudo do arquivo id_ed25519.pub do servidor.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = "FabricaSuporte"
SERVER = os.environ.get("FS_SERVER", "").strip()
KEY = os.environ.get("FS_KEY", "").strip()

if not SERVER or not KEY:
    sys.exit("FS_SERVER e FS_KEY sao obrigatorios")
if not re.fullmatch(r"[A-Za-z0-9.\-:]+", SERVER) or not re.fullmatch(r"[A-Za-z0-9+/=]+", KEY):
    sys.exit("FS_SERVER/FS_KEY com caracteres invalidos")


def patch(rel, pattern, repl, count=1, flags=0):
    path = os.path.join(ROOT, *rel.split("/"))
    with open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    new, n = re.subn(pattern, repl, text, flags=flags)
    if n < count:
        sys.exit(f"ERRO: padrao nao encontrado em {rel}: {pattern} ({n} ocorrencias)")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print(f"ok {rel}: {n} alteracao(oes)")


CFG = "libs/hbb_common/src/config.rs"
patch(CFG, r'RwLock::new\("RustDesk"\.to_owned\(\)\)', f'RwLock::new("{APP_NAME}".to_owned())')
patch(CFG, r'pub const RENDEZVOUS_SERVERS: &\[&str\]\s*=\s*&\[[^\]]*\];',
      f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{SERVER}"];')
patch(CFG, r'pub const RS_PUB_KEY: &str\s*=\s*"[^"]*";', f'pub const RS_PUB_KEY: &str = "{KEY}";')

# Cores da marca (verde #B2D444 e cinza-azulado #3B4A5A)
COM = "flutter/lib/common.dart"
patch(COM, r"static const Color accent = Color\(0xFF0071FF\);", "static const Color accent = Color(0xFF3B4A5A);")
patch(COM, r"static const Color accent50 = Color\(0x770071FF\);", "static const Color accent50 = Color(0x773B4A5A);")
patch(COM, r"static const Color accent80 = Color\(0xAA0071FF\);", "static const Color accent80 = Color(0xAA3B4A5A);")
patch(COM, r"static const Color button = Color\(0xFF2C8CFF\);", "static const Color button = Color(0xFF3B4A5A);")
patch(COM, r"static const Color idColor = Color\(0xFF00B6F0\);", "static const Color idColor = Color(0xFF8FB32E);")
patch(COM, r"(return )Color\(0xFF2C8CFF\);", r"\1Color(0xFF3B4A5A);")

# Metadados do executavel Windows
patch("Cargo.toml", r'ProductName = "RustDesk"', 'ProductName = "Fabrica Suporte"')
patch("Cargo.toml", r'FileDescription = "RustDesk Remote Desktop"', 'FileDescription = "Fabrica Suporte - Acesso Remoto"')
patch("Cargo.toml", r'LegalCopyright = "[^"]*"', 'LegalCopyright = "Fabrica de Codigos. Baseado no RustDesk (AGPL-3.0)."')
print("Branding aplicado.")
