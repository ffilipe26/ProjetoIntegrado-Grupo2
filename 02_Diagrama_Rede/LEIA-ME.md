# 02 – Diagrama da rede (04 e 05/11)

## O que a entrega pede

O diagrama deve permitir que outra pessoa entenda como os dispositivos e serviços se conectam:

- identificar os dispositivos (servidor, clientes, roteador);
- mostrar as conexões e o caminho percorrido pelos dados;
- indicar IPs, sub-rede, portas e protocolos;
- incluir **legenda** para símbolos e siglas;
- se for simulado, dizer qual simulador foi usado.

Nome do arquivo final: `Grupo02_Diagrama.pdf`

Ferramentas sugeridas: **draw.io** (diagrams.net, gratuito, no navegador) ou o **Cisco Packet Tracer**.

## Ficha técnica (dados reais do protótipo)

**Ambiente de teste:** rede local doméstica (Wi-Fi), padrão 192.168.x.0/24.

| Dispositivo | Papel | Endereço | Observação |
|---|---|---|---|
| Roteador Wi-Fi | Gateway da rede local | ex.: 192.168.0.1 | Liga os dispositivos da rede |
| PC servidor | Roda o `servidor.py` | ex.: 192.168.0.15, porta **8000** | O próprio servidor mostra o IP ao iniciar |
| Navegador no PC servidor | Cliente local | 127.0.0.1 (localhost) | Teste local, sem sair do computador |
| Celular / outro PC | Cliente remoto | ex.: 192.168.0.20 | Acessa `http://IP-DO-SERVIDOR:8000` |

> Os IPs com "ex.:" são exemplos. Podem ser usados no diagrama como endereços do ambiente de teste.

**Protocolos (de cima para baixo):**

- Aplicação: **HTTP** (navegador ↔ servidor)
- Transporte: **TCP**, porta **8000** no servidor
- Rede: **IP** (IPv4, rede /24)
- Enlace/físico: **Wi-Fi** (ou Ethernet, se o PC for no cabo)

**Caminho dos dados:**

Cliente (navegador) → Roteador Wi-Fi → PC servidor (porta 8000) → pasta `arquivos` no disco, e a resposta faz o caminho inverso.

**Operações que passam pela rede:**

| Operação | Requisição HTTP |
|---|---|
| Abrir a página e ver a lista | `GET /` |
| Enviar um arquivo | `POST /enviar?nome=...` |
| Baixar um arquivo | `GET /baixar?nome=...` |

## Observação importante para o relatório

O acesso a partir de outro dispositivo (celular) foi **bloqueado pelo firewall do Windows** no computador usado no desenvolvimento: as regras de entrada do Python estavam desabilitadas para o perfil de rede privada. Foi testado na rede Wi-Fi de casa e no hotspot do celular, com o mesmo resultado. Pelo próprio computador, o acesso funcionou tanto por `localhost` quanto pelo IP da rede local. O teste com outro dispositivo deve ser repetido em outro equipamento.
