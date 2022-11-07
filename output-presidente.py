"""
** output-presidente **
monta um arquivo csv com o resultado da votacao para presidente

antes desse programa precisa executar o stage-3.py

OBS: se quiser incluir o modelo da urna usada naquela secao, entao
execute o script Perl 'detecta-modelo-urna.pl' antes desse programa
"""

import os.path
import pickle
import re


def quit_msg(message):
    print("ERROR: " + message)
    quit()


def process_sessao(st, mu_code, mu_name, zon_cd, sec):
    stp = st
    mu_name = re.sub(";", ".", mu_name)
    print(f"{stp};{mu_code};{mu_name};{zon_cd};{sec}", end="")
    fname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.aux.pickle"
    if not os.path.exists(fname):
        print(";OPS: arquivo 'cfg' não encontrado")
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
    print(f";{cfg['st']}", end="")
    print(f";{cfg['dg']}", end="")
    print(f" {cfg['hg']}", end="")
    print(f";{cfg['hashes'][index]['st']}", end="")
    print(f";{cfg['hashes'][index]['dr']}", end="")
    print(f" {cfg['hashes'][index]['hr']}", end="")
    solve_bu_for_president(bu)
    print(";" + hash, end="")
    fname = f"data/{st}/{mu_code}/{zon_cd}_{sec}.modelo"
    try:
        fh = open(fname, "r")
        modelo = fh.readline()
        fh.close()
        modelo = re.sub(" .*", "", modelo).strip()
        if modelo == "":
            modelo = "?"
    except FileNotFoundError:
        modelo = "?"
    print(";" + modelo)


def solve_bu_for_president(bu):
    vote = {
        "12": 0,
        "13": 0,
        "14": 0,
        "15": 0,
        "16": 0,
        "21": 0,
        "22": 0,
        "27": 0,
        "30": 0,
        "44": 0,
        "80": 0
    }
    txt = str(bu, encoding="latin1", errors="ignore").splitlines()
    i = 1
    section = False
    v_apt = -1
    v_bra = -1
    v_nul = -1
    v_nom = -1
    v_apu = -1
    for line in txt:
        if re.search("Verificador:", line):
            section = False
        if section:
            if re.search(" [0-9]{2} +[0-9]+", line):
                v = re.sub("[^0-9 ]", "", line)
                v = re.sub("^ +", "", v)
                v = re.sub(" +$", "", v)
                v = re.sub(" +", " ", v)
                if not re.search("[0-9]{2} [0-9]+$", v):
                    quit_msg("OPS! REGEX ERROR")
                num = re.sub(" .*", "", v)
                val = re.sub(".* 0*", "", v)
                vote[num] = vote[num] + int(val)
            if re.search("^Eleitores Aptos +[0-9]+$", line):
                v_apt = int(re.sub("[^0-9 ]", "", line))
            if re.search("^Brancos +[0-9]+$", line):
                v_bra = int(re.sub("[^0-9 ]", "", line))
            if re.search("^Nulos +[0-9]+$", line):
                v_nul = int(re.sub("[^0-9 ]", "", line))
            if re.search("^Total de votos Nominais +[0-9]+$", line):
                v_nom = int(re.sub("[^0-9 ]", "", line))
            if re.search("^Total Apurado +[0-9]+$", line):
                v_apu = int(re.sub("[^0-9 ]", "", line))
        if re.search("--PRESIDENTE--", line):
            section = True
        i = i + 1
    tot = 0
    for n, v in vote.items():
        print(f";{v}", end="")
        tot = tot + v
    print(f";{tot}", end="")
    if tot == 0:
        quit_msg("OPS! ZEROSUM!")
    if v_apt < 0 or v_bra < 0 or v_nul < 0 or v_nom < 0 or v_apu < 0:
        quit_msg("OPS! FOOTER NOT FOUND!")
    if v_nom != tot:
        quit_msg("OPS! NOMINAL IS NOT SUM!")
    print(f";{v_apt};{v_bra};{v_nul};{v_apu}", end="")


def process_zona(st, mu_name, mu_code, zon_cd, zon_sec):
    for i in zon_sec:
        if i['ns'] != i['nsp']:
            quit_msg(f"ns!=nsp for {state} {mu_code} {zon_cd} {i['ns']}")
        sec = i['ns']
        process_sessao(st, mu_code, mu_name, zon_cd, sec)


def process_municipio(st, mu):
    for zon in mu['zon']:
        process_zona(st, mu['nm'], mu['cd'], zon['cd'], zon['sec'])


fh = open("data/00/states.pickle", "rb")
states = pickle.load(fh)
fh.close()

print("ESTADO;COD_MUNIC;NOME_MUNIC;ZONA;SECAO;SITUACAO PROC;DATAHORA PROC;" +
      "SITUACAO ARQ;DATAHORA ARQ;12CIRO;13LULA;14KELMON;15SIMONE;16VERA;" +
      "21SOFIA;22JAIR;27EYMAEL;30FELIPE;44SORAYA;80LEO;TOTAL;APTOS;" +
      "BRANCOS;NULOS;APURADOS;HASHDOWNLOAD;MODELO")

for state in states:
    fh = open(f"data/00/{state}.cfg.pickle", "rb")
    d = pickle.load(fh)
    fh.close()
    for mu in d['abr'][0]['mu']:
        process_municipio(state, mu)
