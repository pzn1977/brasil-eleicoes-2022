"""
** stage-1 **
faz download da lista de cidades zonas e secoes

OBS: se quiser testar esse programa mais rapidamente, deixe apenas o estado
de Roraima ativo, pois ele tem o menor numero de urnas. Veja na variavel
"states" abaixo.
Neste caso, apos testar, apague o arquivo data/00/states.pickle e rode
novamente este programa para ele processar com todos os estados
"""

import json
import os.path
import pickle
import pprint

import urllib3


def quit_msg(message):
    print("ERROR: " + message)
    quit()


def mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        if not os.path.isdir(path):
            quit_msg(f"failed to create directory '{path}'")


def json_try2load(maybejson):
    try:
        ret = json.loads(maybejson)
    except ValueError:
        return None
    return ret


def get_config(state):
    print(f"get config for '{state}': ", end='')
    fname = "data/00/" + str(state) + ".cfg.pickle"
    if os.path.exists(fname):
        print("OK from cache")
        return
    url = "https://resultados.tse.jus.br/oficial/ele2022/arquivo-urna/" + \
        f"{ecod}/config/{state}/{state}-p000{ecod}-cs.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) " + \
            "Gecko/20100101 Firefox/105.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://resultados.tse.jus.br/oficial/app/index.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'trailers',
    }
    http = urllib3.PoolManager()
    response = http.request(
        method='GET',
        url=url,
        headers=headers,
        timeout=20.0)
    if response.status != 200:
        quit_msg("got response status " + str(response.status) + " @ " + state)
    if not hasattr(response, 'headers'):
        quit_msg("no response headers @ " + state)
    if not hasattr(response, '_body'):
        quit_msg("no response body @ " + state)
    d = json_try2load(response._body)
    if d is None:
        print("** BODY **")
        pprint.pprint(response._body)
        quit_msg("response body is not JSON @ " + state)
    c = 0
    for name, value in d.items():
        if name in ["dg", "hg", "f", "cdp", "abr"]:
            c = c + 1
    if c != 5:
        quit_msg("JSON does not have 5 elements@ " + state)
    fh = open(fname + ".tmp", "wb")
    pickle.dump(d, fh, protocol=pickle.HIGHEST_PROTOCOL)
    fh.close()
    os.rename(fname + ".tmp", fname)
    print("OK from network")
    return


mkdir("data")
mkdir("data/00")

ecod_fname = "data/00/codigo_eleicao.txt"
try:
    ecod_fh = open(ecod_fname, "r")
    ecod = int(ecod_fh.read())
    ecod_fh.close()
except FileNotFoundError:
    ecod = 0
if ecod < 1:
    quit_msg(f"Por favor crie o arquivo '{ecod_fname}'\n" +
             "Dentro dele coloque apenas um numero, que deve ser 406 " +
             "(para primeiro turno) ou 407 (para segundo turno)")

# estado 'zz' corresponde a urnas do exterior
states = sorted(["ac", "al", "ap", "am", "ba", "ce", "df",
                 "es", "zz", "go", "ma", "mt", "ms", "mg",
                 "pr", "pb", "pa", "pe", "pi", "rj", "rn",
                 "rs", "ro", "rr", "sc", "se", "sp", "to"])

# rodar apenas o estado de Roraima (para testes, pois ele tem menos urnas)
# lembre-se de remover o data/00/states.pickle quando alterar essa variavel
#    states = ["rr"]

for state in states:
    mkdir("data/" + state)
    get_config(state)

fname = "data/00/states.pickle"
if not os.path.exists(fname):
    fh = open(fname + ".tmp", "wb")
    pickle.dump(states, fh, protocol=pickle.HIGHEST_PROTOCOL)
    fh.close()
    os.rename(fname + ".tmp", fname)
    print("wrote states config file")
