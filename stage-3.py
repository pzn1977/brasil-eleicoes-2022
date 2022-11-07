"""
** stage-3 **
faz download dos boletins de urna (imgbu) e log (logjez) de cada urna

antes desse programa precisa executar o stage-2.py

OBS: voce pode executar 3 ou 4 copias do programa em paralelo para melhorar
o tempo de download, elas usam lockfile e gerenciam a concorrencia entre si
"""

import json
import os.path
import pickle
import re
import time

import urllib3


def quit_msg(message):
    print("ERROR: " + message)
    quit()


def stop_check():
    global stop_cnt
    stop_cnt = stop_cnt - 1
    if (stop_cnt <= 0):
        if os.path.exists("stop"):
            print("*** STOP FILE FOUND ***")
            quit()
        stop_cnt = 100


def json_try2load(maybejson):
    try:
        ret = json.loads(maybejson)
    except ValueError:
        return None
    return ret


def get_file(st, mu_code, zon_cd, sec, hash, fname):
    ext = re.sub("^.*[.]", "", fname)
    # imgbu logjez bu rdv vscmr        # maioria dos modelos de urna
    # imgbusa logsajez busa rdv vscsa  # poucos modelos, maioria no exterior
    if ext not in ["imgbu", "imgbusa", "logjez", "logsajez"]:
        return False
    pfname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.{ext}.pickle"
    print(ext, end="")
    if os.path.exists(pfname):
        print("[CACHE] ", end="")
        return False
    url = "https://resultados.tse.jus.br/oficial/ele2022/arquivo-urna/" + \
        f"{ecod}/dados/{st}/{mu_code}/{zon_cd}/{sec}/{hash}/{fname}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) " + \
        "Gecko/20100101 Firefox/105.0',
        'Accept': '*/*',
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
        print(url)
        quit_msg("got response status " + str(response.status))
    if not hasattr(response, 'headers'):
        quit_msg("no response headers")
    if not hasattr(response, '_body'):
        quit_msg("no response body")
    rsize = int(response.headers['Content-Length'])
    if rsize < 500:
        quit_msg("content-length too small " + str(rsize))
    if len(response._body) != rsize:
        quit_msg("content-length mismatch " + str(rsize) +
                 " " + str(len(response._body)))
    fh = open(pfname + ".tmp", "wb")
    pickle.dump(response._body, fh, protocol=pickle.HIGHEST_PROTOCOL)
    fh.close()
    os.rename(pfname + ".tmp", pfname)
    print("[DOWNLOAD] ", end="")
    h = {'hash': hash, 'url': url, 'ts': int(os.path.getmtime(pfname))}
    hfname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.{ext}_hash.pickle"
    fh = open(hfname + ".tmp", "wb")
    pickle.dump(h, fh, protocol=pickle.HIGHEST_PROTOCOL)
    fh.close()
    os.rename(hfname + ".tmp", hfname)
    return True


def process_sessao(st, mu_code, zon_cd, sec):
    stop_check()
    fname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.aux.pickle"
    retry = 10
    while not os.path.exists(fname):
        print(f"waiting for {fname}")
        time.sleep(10)
        retry = retry - 1
        if retry == 0:
            print(f"giveup for {fname}")
            return
    if not os.path.exists(fname):
        quit_msg(f"Ops... didn't find {fname}")
    print(f"{st} M={mu_code} Z={zon_cd} S={sec}: ", end="")

    try:
        fhlock = open(fname + ".lock", "x")
    except FileExistsError:
        print("LOCKED")
        return
    fhlock.close()

    fh = open(fname, "rb")
    d = pickle.load(fh)
    fh.close()
    index = 0
    if len(d['hashes']) > 1:
        # try to find only one st==Totalizado
        c = 0
        for i in range(0, len(d['hashes'])):
            if d['hashes'][i]['st'] == 'Totalizado':
                c = c + 1
                index = i
        if c > 1:
            os.remove(fname + ".lock")
            print(f"skip_too_many_st==Totalizado cnt={c}")
            return
        if c == 0:
            # if Totalizado is not found, try to find st==Recebido
            for i in range(0, len(d['hashes'])):
                if d['hashes'][i]['st'] == 'Recebido':
                    c = c + 1
                    index = i
            if c > 1:
                os.remove(fname + ".lock")
                print(f"skip_too_many_st==Recebido cnt={c}")
                return
    c = 0
    for name, value in d['hashes'][index].items():
        if name in ["dr", "ds", "hash", "hr", "nmarq", "st"]:
            c = c + 1
    if c != 6:
        os.remove(fname + ".lock")
        print("skip_hash_element_missing")
        return
    if d['hashes'][index]['st'] not in ['Totalizado', 'Recebido']:
        print(f"skip_st_is_{d['hashes'][index]['st']} ")
        os.remove(fname + ".lock")
        return

    if (type(d['hashes'][index]['nmarq'])) != list:
        print("skip_hash_nmarq_element_is_not_list")
        os.remove(fname + ".lock")
        return
    c = 0
    for i in d['hashes'][index]['nmarq']:
        get_file(st, mu_code, zon_cd, sec, d['hashes'][index]['hash'], i)
    print()
    os.remove(fname + ".lock")


def process_zona(st, mu_name, mu_code, zon_cd, zon_sec):
    for i in zon_sec:
        if i['ns'] != i['nsp']:
            quit_msg(f"ns!=nsp for {state} {mu_code} {zon_cd} {i['ns']}")
        sec = i['ns']
        print(f"{st} {mu_code} {zon_cd} {sec} {mu_name}: ", end="")
        process_sessao(st, mu_code, zon_cd, sec)


def process_municipio(st, mu):
    # print(f"process: {st} {mu['nm']} {mu['cd']}")
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
