# Implementação do protótipo

Base para a seção "Ferramentas, materiais e procedimentos" do relatório e para a entrega 4.

## Ferramentas

- **Python 3.14** com módulos da biblioteca padrão: `http.server` (servidor HTTP), `pathlib` (pastas e arquivos), `urllib.parse` (endereços), `html` e `mimetypes`, `socket` (descobrir o IP local).
- **Navegador web** como cliente (página HTML com um pequeno JavaScript para o envio).
- **Terminal do Windows** para rodar o servidor e ver os logs.

## O que foi implementado (funcionando)

- **Listar** os arquivos da pasta compartilhada, com tamanho (`GET /`).
- **Enviar** arquivos pelo navegador (`POST /enviar`).
- **Baixar** arquivos pelo navegador (`GET /baixar`).
- **Validação do nome do arquivo:** remove caminhos como `../` e caracteres proibidos, impedindo acesso fora da pasta compartilhada.
- **Nome repetido:** salva como `nome (1).ext` em vez de apagar o arquivo antigo.
- **Limite de tamanho:** 50 MB por arquivo (resposta 413 se passar).
- **Respostas de erro:** 400 (nome inválido), 404 (arquivo ou endereço inexistente), 413 (arquivo grande).
- **Registro (log)** de cada requisição, com linhas `[UPLOAD]` e `[DOWNLOAD]` mostrando arquivo, tamanho e IP do cliente.
- **Atendimento simultâneo** de vários clientes (`ThreadingHTTPServer`).
- O servidor mostra ao iniciar o endereço para acesso pela rede local.

Nada foi simulado: todas as funções acima rodam de verdade.

## O que ficou fora do escopo (possibilidade futura)

- contas de usuário e senha;
- HTTPS (criptografia);
- segundo servidor com cópia dos arquivos (replicação);
- excluir ou renomear arquivos pela página;
- uso pela internet.

## Decisões técnicas

- **Só biblioteca padrão:** basta ter o Python instalado, sem instalar pacotes.
- **Envio com JavaScript (`fetch`), com o arquivo direto no corpo da requisição:** evita o formato multipart, cujo módulo de leitura (`cgi`) foi removido das versões recentes do Python.
- **Arquivos gravados e lidos em partes de 64 KB:** arquivos grandes não ocupam toda a memória.
- **`0.0.0.0` na porta 8000:** o servidor aceita conexões de qualquer dispositivo da rede.

## Dificuldades encontradas

- **Acesso de outro dispositivo bloqueado:** o celular não conseguiu acessar o servidor (erro `ERR_TOO_MANY_RETRIES`), tanto no Wi-Fi de casa quanto no hotspot do celular. Pelo próprio PC, o acesso funcionou por `localhost` e pelo IP da rede. A causa identificada foi o **firewall do Windows**: as regras de entrada do Python estavam desabilitadas para o perfil de rede privada. O teste deve ser repetido em outro equipamento.

## Desenvolvimento por etapas

1. Servidor básico respondendo uma página de teste.
2. Listagem dos arquivos da pasta.
3. Envio (upload) com validação de nome, nome repetido e limite de tamanho.
4. Download com a mesma validação.
5. Exibição do IP local para acesso por outros dispositivos.
