# Git, GitHub e tudo mais — explicado pra quem não é programador

> Leitura: 10 minutos. Releia quando esquecer.

## O problema que tudo isso resolve

Você trabalha em algo importante. Salva num arquivo. Apaga sem querer. Perdeu.
Ou: o Claude "melhorou" o arquivo e você quer voltar. Não consegue.
Ou: você tem 3 versões do mesmo script em 3 pastas. Qual é a boa?

Git resolve tudo isso. Mas pelo nome assustador, parece coisa de programador. Não é. **Git é Ctrl+Z vitaminado.**

## Git em 1 parágrafo

Imagine uma **câmera fotográfica** que, toda vez que você aperta um botão, tira foto do estado EXATO de todos os seus arquivos naquele instante. Essas fotos ficam numa pasta invisível chamada `.git`. Se daqui a 3 semanas você precisar voltar, Git mostra todas as fotos e você pode voltar pra qualquer uma delas. **Ele nunca apaga uma foto.** Só acrescenta novas.

Cada foto se chama **commit**.

## GitHub em 1 parágrafo

Seu álbum de fotos (Git) fica no seu Mac. Se o Mac queimar, perdeu tudo. **GitHub é o backup online** desse álbum. Você tem uma cópia local (no Mac) e outra no GitHub (na internet, grátis pra contas privadas). Toda vez que você quer sincronizar, você **"empurra" (push)** as fotos novas pro GitHub. Quando você trabalha em outro computador, você **"puxa" (pull)** as fotos de lá.

## As 5 palavras que importam

| Palavra | O que é em português de verdade |
|---|---|
| **commit** | tirar uma foto do estado atual dos arquivos |
| **push** | enviar as fotos novas pro GitHub (backup online) |
| **pull** | baixar as fotos novas do GitHub (pra trabalhar aqui) |
| **branch** | uma linha do tempo paralela — você pode experimentar mudanças sem mexer na principal |
| **merge** | juntar uma linha paralela de volta na principal |

**Pull request (PR)** é diferente: é um "**posso juntar esta linha paralela na principal?**" — o sistema revisa e só deixa juntar se estiver tudo OK.

## Como isso protege você

Você hoje: `arquivo_final_v7_NOVO_ESTE.md`, `arquivo_final_v7_NOVO_ESTE_ok.md`, `arquivo_final_v8.md`...

Você com Git: `arquivo.md` + histórico de TODAS as versões com data, hora e mensagem explicando o que mudou. Sempre 1 arquivo. Histórico automático.

Exemplo real:
```
a3f8c21 chore(bootstrap): estrutura Maestro          (há 10 min)
9b31de2 feat(peticao): verificador de gênero do juiz (ontem)
bf50771 Initial commit                                (2 dias)
```

Cada linha é uma foto. A qualquer momento, você volta pra qualquer uma.

## Pull Request — o guarda da porta

Imagine um porteiro na entrada do prédio. Pra entrar modificação nova no código principal, o porteiro pede:
1. A pessoa trouxe prova de que testou? (output colado)
2. A pessoa atualizou o livro de registros? (CHANGELOG.md)
3. A mudança está ligada a uma tarefa autorizada? (`Closes #N`)
4. Tem 5 itens da checklist marcados? (Definition of Done)

Se faltar qualquer item, **porta fechada** (merge bloqueado). É isso que as GitHub Actions fazem no seu Maestro. **Você não precisa lembrar dos itens — o porteiro lembra.**

## Por que isso é ESSENCIAL pra você

- Você tem TEA+TDAH e perde contexto entre sessões
- O Claude esquece tudo a cada conversa
- Sozinho, nem você nem o Claude são confiáveis em "lembrar o que ficou pronto"
- Git + GitHub + regras em arquivo = **memória externa compartilhada**

Você NÃO precisa confiar na sua memória nem na do Claude. Confia no arquivo versionado. O arquivo não mente, não esquece, não motiva.

## O único medo legítimo: "vou quebrar algo"

**Não vai.** Git só acrescenta. Pra "quebrar", você precisaria digitar comandos destrutivos muito específicos (`git reset --hard`, `git push --force`). Nenhum é usado no fluxo normal. E o hook anti-limpeza do seu sistema bloqueia `rm -rf` automaticamente.

Pra usar seu Maestro, você precisa saber 4 comandos:

```bash
git status       # "o que mudou desde a última foto?"
git add -A       # "incluir tudo que mudou na próxima foto"
git commit -m "mensagem"  # "bateu a foto com esta legenda"
git push         # "enviar ao GitHub"
```

**Só isso.** O resto, o Claude faz.

## E se der errado?

Fim de mundo nenhum. Você escreve na conversa:
```
Algo deu errado. Rode git status e me mostre. Não mexa em mais nada.
```

O Claude vai mostrar. Você cola aqui, eu destravo.

---

**Próximo arquivo:** `02-COMO-SALVAR.md` — o passo-a-passo literal de cada salvamento.
