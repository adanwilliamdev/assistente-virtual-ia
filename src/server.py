"""
Servidor web do LivroCerto (apenas biblioteca padrão do Python).

    python src/server.py            # http://127.0.0.1:8000
    PORT=5000 python src/server.py

Endpoints:  GET /  |  GET /api/status  |  GET /api/livros?genero=&nivel=  |  POST /api/chat
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import app as core
import knowledge_base as kb
import llm_client

PAGINA = Path(__file__).resolve().parent.parent / "web" / "index.html"
LIVROS = kb.carregar_livros()
MAX_BODY = 10_000


class Handler(BaseHTTPRequestHandler):
    def _enviar(self, status: int, corpo: bytes, tipo: str):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, dados, status: int = 200):
        self._enviar(status, json.dumps(dados, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            self._enviar(200, PAGINA.read_bytes(), "text/html; charset=utf-8")
        elif url.path == "/api/status":
            self._json({"modo": "ia" if llm_client.modo_ia_disponivel() else "local", "total_livros": len(LIVROS)})
        elif url.path == "/api/livros":
            q = parse_qs(url.query)
            livros = kb.listar(LIVROS, q.get("genero", [""])[0], q.get("nivel", [""])[0])
            self._json({
                "livros": livros,
                "generos": sorted({l["genero"] for l in LIVROS}),
                "niveis": sorted({l["nivel"] for l in LIVROS}),
            })
        else:
            self._json({"erro": "não encontrado"}, 404)

    def do_POST(self):
        if urlparse(self.path).path != "/api/chat":
            return self._json({"erro": "não encontrado"}, 404)
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            if not 0 < tamanho <= MAX_BODY:
                raise ValueError
            dados = json.loads(self.rfile.read(tamanho))
            pergunta = str(dados.get("mensagem", "")).strip()[:500]
            if not pergunta:
                raise ValueError
            historico = [str(m)[:500] for m in dados.get("historico", [])][-4:]
            excluir = dados.get("excluir_id")
            excluir = excluir if isinstance(excluir, int) else None
        except (ValueError, TypeError, AttributeError, json.JSONDecodeError):
            return self._json({"erro": "requisição inválida"}, 400)
        self._json(core.responder_estruturado(pergunta, LIVROS, historico, excluir))


def main():
    porta = int(os.environ.get("PORT", 8000))
    servidor = ThreadingHTTPServer((os.environ.get("HOST", "127.0.0.1"), porta), Handler)
    modo = "IA (Claude)" if llm_client.modo_ia_disponivel() else "local"
    print(f"LivroCerto no ar em http://127.0.0.1:{porta}  (modo {modo}) — Ctrl+C para sair")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nAté a próxima leitura!")


if __name__ == "__main__":
    main()
