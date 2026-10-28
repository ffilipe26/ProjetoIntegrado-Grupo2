# 03 – Arquitetura do sistema distribuído (04 e 05/11)

## O que a entrega pede

- desenho ou descrição da divisão do sistema em componentes;
- função de cada componente e quais informações recebe ou envia;
- como os componentes se comunicam (requisições, mensagens...);
- a sequência de **pelo menos uma operação completa**, da origem dos dados até a resposta ao usuário;
- uma dependência ou falha possível e como ela afeta o serviço.

O plano de projeto já tem um diagrama de blocos e uma tabela de componentes, que servem de base.

## Componentes (dados reais do protótipo)

| Componente | Função | Recebe | Envia |
|---|---|---|---|
| Cliente (navegador) | Interface do usuário | Página HTML, lista de arquivos, arquivos baixados, mensagens | Pedidos HTTP (GET e POST) |
| Servidor (`servidor.py`) | Recebe os pedidos, valida e acessa a pasta | Pedidos HTTP e conteúdo dos arquivos enviados | Respostas HTTP (página, arquivo, mensagens e códigos 200/400/404/413) |
| Armazenamento (pasta `arquivos`) | Guarda os arquivos no disco | Arquivos gravados pelo servidor | Arquivos lidos pelo servidor |

Comunicação: **requisição e resposta HTTP** (modelo cliente-servidor). O servidor atende vários pedidos ao mesmo tempo (`ThreadingHTTPServer`).

## Sequência 1: enviar um arquivo (upload)

1. O usuário escolhe um arquivo na página e clica em **Enviar**.
2. O navegador manda `POST /enviar?nome=arquivo.pdf` com o conteúdo do arquivo.
3. O servidor limpa o nome (impede caminhos como `../`) e confere o tamanho (limite de 50 MB).
4. Se já existir um arquivo com esse nome, o servidor usa `arquivo (1).pdf`.
5. O servidor grava o arquivo na pasta `arquivos`.
6. O servidor responde **200** com a mensagem "Arquivo enviado com sucesso" e registra `[UPLOAD]` no log.
7. O navegador recarrega a página (`GET /`) e o arquivo aparece na lista.

## Sequência 2: baixar um arquivo (download)

1. O usuário clica no nome de um arquivo da lista.
2. O navegador manda `GET /baixar?nome=arquivo.pdf`.
3. O servidor limpa o nome e confere se o arquivo existe na pasta.
4. Se existir, responde **200** com o arquivo (o navegador baixa) e registra `[DOWNLOAD]` no log.
5. Se não existir, responde **404** "Arquivo não encontrado".

## Falha e dependência

- **Servidor parado:** nenhum cliente consegue listar, enviar ou baixar. O navegador mostra "Erro: não foi possível conectar ao servidor". O servidor é um **ponto único de falha**.
- **Recuperação:** ao reiniciar o servidor, os arquivos continuam disponíveis, porque ficam gravados no disco.
- **Rede/firewall:** se o firewall bloquear a porta 8000, clientes de outros dispositivos não alcançam o servidor (aconteceu durante o desenvolvimento).
- **Melhoria possível (não implementada):** um segundo servidor com cópia dos arquivos, para o serviço continuar quando o primeiro cair.
