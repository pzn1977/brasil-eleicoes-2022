"""
** stage-2 **
faz download do arquivo "aux" que contem informacoes dos hashes que indicam
a localizacao dos arquivos de boletim de urna e de log no site do TSE

antes desse programa precisa executar o stage-1.py

OBS: voce pode executar 3 ou 4 copias do programa em paralelo para melhorar
o tempo de download, elas usam lockfile e gerenciam a concorrencia entre si
"""

import json
import os.path
import pickle
import pprint

import urllib3


def quit_msg(message):
    print("ERROR: " + message)
    quit()


def json_try2load(maybejson):
    try:
        ret = json.loads(maybejson)
    except ValueError:
        return None
    return ret


def mkdir_check(dir):
    try:
        os.mkdir(dir)
    except FileExistsError:
        return


def stop_check():
    global stop_cnt
    stop_cnt = stop_cnt - 1
    if (stop_cnt <= 0):
        if os.path.exists("stop"):
            print("*** STOP FILE FOUND ***")
            quit()
        stop_cnt = 100


def get_config(st, mu_code, zon_cd, sec):
    stop_check()
    mkdir_check(f"data/{st}")
    mkdir_check(f"data/{st}/{mu_code}")
    fname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.aux.pickle"
    if os.path.exists(fname):
        print("cached")
        return
    try:
        fhlock = open(fname + ".lock", "x")
    except FileExistsError:
        print("LOCKED")
        return
    fhlock.close()
    url = "https://resultados.tse.jus.br/oficial/ele2022/arquivo-urna/" + \
        f"{ecod}/dados/{st}/{mu_code}/{zon_cd}/{sec}/p000{ecod}-{state}-" + \
        f"m{mu_code}-z{zon_cd}-s{sec}-aux.json"
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
        quit_msg("got response status " +
                 str(response.status) + " @ " + state)
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
        if name in ["dg", "ds", "f", "hashes", "hg", "st"]:
            c = c + 1
    if c != 6:
        pprint.pprint(d)
        quit_msg("JSON does not have 6 elements")
    fh = open(fname + ".tmp", "wb")
    pickle.dump(d, fh, protocol=pickle.HIGHEST_PROTOCOL)
    fh.close()
    os.rename(fname + ".tmp", fname)
    print("OK from network")
    os.remove(fname + ".lock")


def process_zona(st, mu_name, mu_code, zon_cd, zon_sec):
    for i in zon_sec:
        if i['ns'] != i['nsp']:
            quit_msg(f"ns!=nsp for {state} {mu_code} {zon_cd} {i['ns']}")
        sec = i['ns']
        print(f"{st} {mu_code} {zon_cd} {sec} {mu_name}: ", end="")
        get_config(st, mu_code, zon_cd, sec)


def process_municipio(st, mu):
    for zon in mu['zon']:
        process_zona(st, mu['nm'], mu['cd'], zon['cd'], zon['sec'])


fh = open("data/00/states.pickle", "rb")
states = pickle.load(fh)
fh.close()

fh_ecod = open("data/00/codigo_eleicao.txt", "r")
ecod = int(fh_ecod.read())
fh_ecod.close()

stop_cnt = 0

for state in states:
    fh = open(f"data/00/{state}.cfg.pickle", "rb")
    d = pickle.load(fh)
    fh.close()
    for mu in d['abr'][0]['mu']:
        process_municipio(state, mu)
