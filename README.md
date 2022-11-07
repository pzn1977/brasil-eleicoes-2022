# brasil-eleicoes-2022

Conjunto de programas para fazer download dos dados oficiais das eleições direto do site do TSE. E disponibilizar os arquivos de boletim de urnas e logs para possibilitar analises diversas.

NOTA: esta versão gerencia APENAS UM TURNO da eleição (qualquer um dos turnos, mas APENAS um deles). Para poder trabalhar com dados de dois turnos, você deve instalar os programas em duas pastas diferentes e executar cada turno de uma pasta.

Informações de como o programa coleta os dados do website do TSE podem ser encontradas no arquivo: estrutura-download-tse.txt

## Instalação das dependências

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install urllib3
```

## Uso dos programas

```
$ python stage-1.py
    ERROR: Por favor crie o arquivo 'data/00/codigo_eleicao.txt'
    Dentro dele coloque apenas um numero, que deve ser 406 (para primeiro turno) ou 407 (para segundo turno)
$ echo 406 > data/00/codigo_eleicao.txt
$ python stage-1.py
$ python stage-2.py
...
```

IMPORTANTE: para testar em apenas um estado (e não demorar dias para baixar tudo), recomendo usar o estado de Roraima, instruções de como fazer isso estão dentro do stage-1.py

O que cada programa faz (**veja maiores detalhes na descrição/comentários dentro de cada programa**)

* **stage-1.py:** download da lista de estados, cidades, zonas, seções
* **stage-2.py:** download do arquivo 'aux' que contém informação da localização dos demais arquivos
* **stage-3.py:** download dos boletins de urna e logs de urna
* **output-boletim.py:** converte todos os boletins de urna para formato 'txt'
* **output-presidente.py:** gera um arquivo de planilha (csv) com todos os votos a presidente
* **detecta-modelo-urna.pl:** abre os logs de urna e detecta qual o modelo dela
