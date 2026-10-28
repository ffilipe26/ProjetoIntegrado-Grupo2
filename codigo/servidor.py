# CompartilhaFATEC - servidor de arquivos
# Versão 5: lista, envia (upload) e baixa (download) arquivos pelo navegador
#           e mostra o endereço para acessar de outros dispositivos da rede

import html
import mimetypes
import socket
from pathlib import Path
from urllib.parse import urlparse, parse_qs, quote
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORTA = 8000  # porta onde o servidor fica "escutando" as requisições
LIMITE_MB = 50  # tamanho máximo de arquivo aceito no envio

# Pasta compartilhada (o "armazenamento" do diagrama de blocos).
# Fica ao lado deste arquivo: codigo/arquivos
PASTA_ARQUIVOS = Path(__file__).parent / "arquivos"

# Modelo da página. O trecho {{LISTA}} é trocado pela lista de arquivos.
PAGINA = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CompartilhaFATEC</title>
</head>
<body>
  <h1>CompartilhaFATEC</h1>

  <h2>Enviar arquivo</h2>
  <input type="file" id="arquivo">
  <button onclick="enviar()">Enviar</button>
  <p id="status"></p>

  <h2>Arquivos disponíveis</h2>
  {{LISTA}}

  <script>
    // Roda quando o usuário clica em "Enviar"
    async function enviar() {
      const input = document.getElementById("arquivo");
      const status = document.getElementById("status");

      if (input.files.length === 0) {
        status.textContent = "Escolha um arquivo primeiro.";
        return;
      }

      const arquivo = input.files[0];
      status.textContent = "Enviando...";

      try {
        // Manda o conteúdo do arquivo para o servidor (requisição POST)
        const resposta = await fetch("/enviar?nome=" + encodeURIComponent(arquivo.name), {
          method: "POST",
          body: arquivo
        });
        status.textContent = await resposta.text();
        if (resposta.ok) {
          setTimeout(() => location.reload(), 1000);  // recarrega para mostrar o arquivo na lista
        }
      } catch (erro) {
        // Cai aqui quando o servidor está fora do ar
        status.textContent = "Erro: não foi possível conectar ao servidor.";
      }
    }
  </script>
</body>
</html>"""


def listar_arquivos():
    """Devolve os arquivos da pasta compartilhada, em ordem alfabética."""
    return sorted(p for p in PASTA_ARQUIVOS.iterdir() if p.is_file())


def montar_pagina():
    """Monta a página HTML com a lista de arquivos disponíveis."""
    arquivos = listar_arquivos()

    if arquivos:
        itens = ""
        for arq in arquivos:
            tamanho_kb = arq.stat().st_size / 1024
            # html.escape protege a página caso o nome do arquivo tenha símbolos como < >
            link = "/baixar?nome=" + quote(arq.name)  # endereço de download do arquivo
            itens += f'<li><a href="{link}">{html.escape(arq.name)}</a> ({tamanho_kb:.1f} KB)</li>\n'
        lista = f"<ul>\n{itens}</ul>"
    else:
        lista = "<p>Nenhum arquivo compartilhado ainda.</p>"

    return PAGINA.replace("{{LISTA}}", lista)


def nome_seguro(nome):
    """
    Limpa o nome do arquivo enviado para evitar acesso fora da pasta compartilhada.
    Ex.: "../../Windows/teste.txt" vira só "teste.txt".
    Devolve None se o nome for inválido.
    """
    nome = nome.replace("\\", "/").split("/")[-1].strip()  # fica só com o nome, sem caminho
    for caractere in '<>:"|?*':  # caracteres proibidos em nomes de arquivo no Windows
        nome = nome.replace(caractere, "_")
    if nome in ("", ".", ".."):
        return None
    return nome


def caminho_livre(nome):
    """Se já existir um arquivo com esse nome, cria 'nome (1).ext', 'nome (2).ext'..."""
    caminho = PASTA_ARQUIVOS / nome
    numero = 1
    while caminho.exists():
        caminho = PASTA_ARQUIVOS / f"{Path(nome).stem} ({numero}){Path(nome).suffix}"
        numero += 1
    return caminho


def descobrir_ip_local():
    """
    Descobre o IP deste computador na rede local (ex.: 192.168.0.15).
    Truque: "conecta" um socket UDP a um endereço externo só para o sistema escolher
    a placa de rede certa. Nenhum dado é enviado de verdade.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return None


class Servidor(BaseHTTPRequestHandler):
    # Roda toda vez que o navegador faz uma requisição GET (pedir uma página)
    def do_GET(self):
        endereco = urlparse(self.path)
        if endereco.path == "/":
            # Página principal: formulário de envio + lista de arquivos
            self.responder(montar_pagina(), tipo="text/html")
        elif endereco.path == "/baixar":
            # Download de um arquivo da pasta compartilhada
            self.baixar(parse_qs(endereco.query).get("nome", [""])[0])
        else:
            self.send_error(404)

    def baixar(self, nome_pedido):
        """Envia para o navegador o arquivo pedido, se ele existir na pasta compartilhada."""
        nome = nome_seguro(nome_pedido)
        caminho = PASTA_ARQUIVOS / nome if nome else None
        if caminho is None or not caminho.is_file():
            self.responder("Arquivo não encontrado.", status=404)
            return

        tamanho = caminho.stat().st_size
        tipo = mimetypes.guess_type(caminho.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(tamanho))
        # "attachment" faz o navegador baixar o arquivo em vez de abrir na tela
        self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(caminho.name)}")
        self.end_headers()

        # Envia o arquivo em partes, para não carregar tudo na memória de uma vez
        with open(caminho, "rb") as entrada:
            while pedaco := entrada.read(65536):
                self.wfile.write(pedaco)

        print(f"[DOWNLOAD] {caminho.name} ({tamanho} bytes) enviado para {self.client_address[0]}")

    # Roda toda vez que o navegador faz uma requisição POST (enviar dados)
    def do_POST(self):
        endereco = urlparse(self.path)
        if endereco.path != "/enviar":
            self.send_error(404)
            return

        # Pega o nome do arquivo que veio no endereço (?nome=...)
        nome = nome_seguro(parse_qs(endereco.query).get("nome", [""])[0])
        if nome is None:
            self.responder("Nome de arquivo inválido.", status=400)
            return

        # Confere o tamanho antes de receber
        tamanho = int(self.headers.get("Content-Length", 0))
        if tamanho > LIMITE_MB * 1024 * 1024:
            self.responder(f"Arquivo muito grande (limite: {LIMITE_MB} MB).", status=413)
            return

        # Recebe o conteúdo em partes e grava na pasta compartilhada
        destino = caminho_livre(nome)
        restante = tamanho
        with open(destino, "wb") as saida:
            while restante > 0:
                pedaco = self.rfile.read(min(65536, restante))
                if not pedaco:
                    break
                saida.write(pedaco)
                restante -= len(pedaco)

        print(f"[UPLOAD] {destino.name} ({tamanho} bytes) recebido de {self.client_address[0]}")
        self.responder(f"Arquivo '{destino.name}' enviado com sucesso!")

    def responder(self, texto, status=200, tipo="text/plain"):
        """Envia uma resposta (página ou mensagem) para o navegador."""
        corpo = texto.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{tipo}; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)


if __name__ == "__main__":
    PASTA_ARQUIVOS.mkdir(exist_ok=True)  # cria a pasta "arquivos" se ainda não existir

    # "0.0.0.0" = aceita conexões de qualquer dispositivo da rede (PC, celular...)
    servidor = ThreadingHTTPServer(("0.0.0.0", PORTA), Servidor)
    ip_local = descobrir_ip_local()
    print(f"Servidor rodando em http://localhost:{PORTA}  (neste computador)")
    if ip_local:
        print(f"Outros dispositivos da mesma rede: http://{ip_local}:{PORTA}")
    print(f"Pasta compartilhada: {PASTA_ARQUIVOS}")
    print("Para parar, aperte Ctrl+C")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
