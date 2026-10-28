# 05 – Plano e resultados dos testes (11 e 12/11)

## O que a entrega pede

Tabela com: **identificação do teste, condição inicial, ação realizada, resultado esperado, resultado observado e evidência**.

- pelo menos **1 teste normal** (comunicação entre os componentes);
- pelo menos **1 teste de falha** (ex.: servidor parado);
- quando possível, **métricas** (tempo de resposta, disponibilidade);
- **prints legíveis**, cada um dizendo a qual teste pertence.

Os prints vão na pasta `Grupo02_Evidencias` (ex.: `T1.png`, `T7a.png`).

Para rodar o servidor, veja `codigo/COMO_RODAR.md`. Funciona em qualquer PC com Python.

## Testes sugeridos

| ID | Tipo | Condição inicial | Ação | Resultado esperado |
|---|---|---|---|---|
| T1 | Normal | Servidor rodando | Abrir `http://localhost:8000` | Página com formulário e lista de arquivos |
| T2 | Normal | Servidor rodando | Enviar um arquivo pela página | Mensagem de sucesso, arquivo na lista e `[UPLOAD]` no log |
| T3 | Normal | Arquivo na lista | Clicar no nome do arquivo | Download do arquivo, mesmo tamanho do original, `[DOWNLOAD]` no log |
| T4 | Normal | Arquivo já enviado | Enviar o mesmo arquivo de novo | Salvo como `nome (1).ext`, sem apagar o primeiro |
| T5 | Segurança | Servidor rodando | Enviar com nome malicioso (comando abaixo) | Arquivo salvo dentro da pasta `arquivos`, nunca fora dela |
| T6 | Segurança | Servidor rodando | Tentar baixar o próprio código (comando abaixo) | Resposta 404 |
| T7 | **Falha** | Página aberta | Parar o servidor (Ctrl+C) e tentar enviar | "Erro: não foi possível conectar ao servidor" |
| T8 | Recuperação | Servidor parado | Rodar o servidor de novo e atualizar a página | Arquivos continuam na lista |
| T9 | Rede | Servidor rodando | Acessar de outro dispositivo da mesma rede | Página abre e o log mostra o IP do outro dispositivo (depende do firewall) |

Deixem a coluna "resultado observado" para preencher **depois** de executar cada teste.

## Comandos úteis (terminal do Windows, com o servidor rodando)

Crie antes um arquivo `teste.txt` qualquer na pasta onde vai rodar os comandos.

**T5 – nome malicioso:**
```
curl -X POST --data-binary @teste.txt "http://localhost:8000/enviar?nome=..%2F..%2Fteste.txt"
```

**T6 – tentar baixar o código do servidor:**
```
curl -i "http://localhost:8000/baixar?nome=..%2Fservidor.py"
```

**Métrica – tempo de resposta (rodar umas 10 vezes e tirar a média):**
```
curl -o NUL -s -w "%{time_total}\n" http://localhost:8000/
```
O resultado sai em segundos (ex.: `0.004` = 4 ms).

**Métrica – disponibilidade:** em um período de teste, contar quantas requisições deram certo e calcular a porcentagem (ex.: 10 de 10 = 100%; com o servidor parado, 0%).
