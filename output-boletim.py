"""
** output-boletim **

gera os boletins de urna em formato TXT
os boletins poderam ser encontrados na pasta data/ESTADO/COD_CIDADE/*.txt

antes desse programa precisa executar o stage-3.py
"""

import os.path
import pickle
import pprint
import re


def quit_msg(message):
    print("ERROR: " + message)
    quit()


def get_file(st, mu_code, zon_cd, sec, hash, fname):
    print(f"fname={fname} ", end="")


def process_sessao(st, mu_code, mu_name, zon_cd, sec):
    stp = st
    mu_name = re.sub(";", ".", mu_name)
    print(f"S={stp} M={mu_code} Z={zon_cd} S={sec} ", end="")
    fname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.aux.pickle"
    if not os.path.exists(fname):
        print("OPS: arquivo 'cfg' não encontrado")
        return
    fh = open(fname, "rb")
    cfg = pickle.load(fh)
    fh.close()
    fname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.imgbu.pickle"
    hname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.imgbu_hash.pickle"
    if not os.path.exists(fname):
        fname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.imgbusa.pickle"
        hname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.imgbusa_hash.pickle"
    if not os.path.exists(fname):
        print(";OPS: arquivo 'imgbu' não encontrado")
        return
    if not os.path.exists(hname):
        print(";OPS: arquivo 'hash' não encontrado")
        return
    fh = open(fname, "rb")
    bu = pickle.load(fh)
    fh.close()
    fh = open(hname, "rb")
    bu_hash = pickle.load(fh)
    fh.close()
    hash = bu_hash['hash']
    index = None
    for i in range(0, len(cfg['hashes'])):
        if hash == cfg['hashes'][i]['hash']:
            index = i
    if index is None:
        print(";OPS: config não encontrado")
        return
    write_bu(bu, stp, mu_code, mu_name, zon_cd, sec)
    print()


def write_bu(bu, st, mu_code, mu_name, zon_cd, sec):
    fname = f"data/{st}/{mu_code}/{st}_{mu_code}_{zon_cd}_{sec}.txt"
    if os.path.exists(fname):
        print("[SKIP]", end="")
        return
    txt = str(bu, encoding="latin1", errors="ignore").splitlines()
    bol = ""
    section = False
    section_pres = False
    for line in txt:
        if re.search("Boletim de Urna", line):
            section = True
        if re.search("---------- 1 de .* ----------", line):
            section = False
        if re.search("----PRESIDENTE----", line):
            section_pres = True
        if re.search("ASSINATURA QR CODE", line):
            section = False
        if section:
            bol = bol + "".join([c for c in line if ord(c) >= 32]) + "\n"
        if section_pres and re.search("========================", line):
            section = False
    if bol == "" or section is True:
        print()
        pprint.pprint(txt)
        quit_msg("ERROR: check bol regex rules!!!")
    else:
        fh = open(fname, "w")
        fh.write(bol)
        fh.close()
        print("[TXT]", end="")


def process_zona(st, mu_name, mu_code, zon_cd, zon_sec):
    for i in zon_sec:
        if i['ns'] != i['nsp']:
            quit_msg(f"ns!=nsp for {state} {mu_code} {zon_cd} {i['ns']}")
        sec = i['ns']
        # print(f"{st} {mu_code} {zon_cd} {sec} {mu_name}: ", end="")
        process_sessao(st, mu_code, mu_name, zon_cd, sec)


def process_municipio(st, mu):
    # print(f"process: {st} {mu['nm']} {mu['cd']}")
    for zon in mu['zon']:
        process_zona(st, mu['nm'], mu['cd'], zon['cd'], zon['sec'])


fh = open("data/00/states.pickle", "rb")
states = pickle.load(fh)
fh.close()

for state in states:
    fh = open(f"data/00/{state}.cfg.pickle", "rb")
    d = pickle.load(fh)
    fh.close()
    for mu in d['abr'][0]['mu']:
        process_municipio(state, mu)
