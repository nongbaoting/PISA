#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File            : structure.py
# @Date            : 2022/01/07 12:45:08
# @Author          : Baoting Nong (nong55@foxmail.com)
# @Link            : https://github.com/nongbaoting
# @Version         : 1.0.0
# @Description     : 


# from pdbecif.mmcif_tools import MMCIF2Dict
import os
import re
import sys

from collections import defaultdict
import gzip 

import fire
import prody
import numpy as np

def select_domain(outname, pdbFi, chain, start, end):
    atoms = prody.parsePDB(pdbFi)
    domain = atoms.select(
        f"chain {chain} resnum {start}to{end}")
    outFi = f"{outname}.{chain}.{start}-{end}"
    if domain:
        writePrody = prody.writePDB(outFi, domain)


def select_domain_mmCIF(outname, pdbFi, chain, start, end):
    atoms = prody.parseMMCIF(pdbFi, chain=chain)
    domain = atoms.select(
        f"chain {chain} resnum {start}to{end}")
    outFi = f"{outname}.{chain}.{start}-{end}"
    if domain:
        writePrody = prody.writePDB(outFi, domain)


def select_domain_pdbtools(outname, pdbFi, chain, start, end):
    cmd = "zcat 3h8d.cif.gz |pdb_fromcif| pdb_selchain -A|pdb_selres -1:10"


def select_chain(outname, pdbFi, chain_letter):
    atoms = prody.parseMMCIF(pdbFi, chain=chain_letter)
    outFi = f"{outname}{chain_letter}"
    if atoms:
        writePrody = prody.writePDB(outFi, atoms)


reg_blank = re.compile(r'\s+')
pattern = re.compile('.pdb$|.pdb.gz$', re.IGNORECASE)
pattern_cif = re.compile('.cif$|cif.gz$', re.IGNORECASE)


def scanAndFind_pattern(mydir, mypattern):
    wantFiles = []
    for entry in os.scandir(mydir):
        if entry.is_file() and mypattern.search(entry.name):
            wantFiles.append(entry)
        elif entry.is_dir():
            wantFiles.extend(scanAndFind_pattern(entry.path, mypattern))
    return wantFiles


reg_chainPos = re.compile(r'^(\w+):(-?\d+)\w*?-(-?\d+)\w*?')


def parse_chain_region(cr):
    match = reg_chainPos.search(cr)

    if match:
        chain, start, end = match.group(1), match.group(2), match.group(3)

        return [chain, start, end]
    else:
        return None


def cal_domain_plDDT(cif_fi, chain, start, end):
    mmcif_dict = MMCIF2Dict()
    cif_dict = mmcif_dict.parse(cif_fi)
    pdb_id = list(cif_dict.keys())[0]
    plDDT = cif_dict[pdb_id]['_ma_qa_metric_local']
    plDDT_arr = [float(i) for i in plDDT['metric_value']]
    label_seq_id = plDDT['label_seq_id']
    label_asym_id = plDDT['label_asym_id']
    start_idx = label_seq_id.index(start)
    end_idx = label_seq_id.index(end)
    domain_metric = plDDT_arr[start_idx:(end_idx + 1)]
    q1 = np.quantile(domain_metric, 0.1)
    q2 = np.quantile(domain_metric, 0.2)
    q25 = np.quantile(domain_metric, 0.25)
    q50 = np.quantile(domain_metric, 0.5)
    # print(q1, q2, q25, q50)
    mn = np.mean(domain_metric)
    return [q1, q2, q25, q50, mn]


class RUN:

    def cal_domain_plDDT(self, pdbDir, info):
        infoDt = defaultdict(list)
        with open(info, 'r') as f:
            for li in f:
                if re.match("#", li):
                    continue
                cell = reg_blank.split(li.strip())
                # chain, start, end, info1,info2
                infoDt[cell[0]].append(
                    ['A', cell[1], cell[2], cell[5], cell[6]])
        res = []
        for entry in scanAndFind_pattern(pdbDir, pattern_cif):
            uniprot_id = entry.name.split('-')[1]
            if uniprot_id in infoDt:
                for item in infoDt[uniprot_id]:
                    # print(uniprot_id)
                    #uniprot_dm = f'f"{outname}.{chain}.{start}-{end}"'
                    uniprot_dm = f"{uniprot_id}.{item[0]}.{item[1]}-{item[2]}"
                    res_ = [uniprot_id, uniprot_dm, entry.name]
                    try:
                        qq = cal_domain_plDDT(
                            entry.path, item[0], item[1], item[2])
                        res_.extend([str(round(i, 2)) for i in qq])
                        res.append(res_)
                    except Exception as e:
                        print(entry.name, e)
        with open("DUF_domain_plDDT.txt", 'w') as fo:
            fo.write('\t'.join(['uniprot_id', 'uniprot_dm', 'pdbFile',
                     'q1', 'q2', 'q25', 'q50', 'mean']) + '\n')
            for arr in res:
                fo.write('\t'.join(arr)+"\n")

    def get_domains(self, pdbDir, info, outdir='./'):
        infoDt = defaultdict(list)
        with open(info, 'r') as f:
            for li in f:
                if re.match("#", li):
                    continue
                cell = reg_blank.split(li.strip())
                # chain, start, end, info1, info2
                infoDt[cell[0]].append(
                    ['A', cell[1], cell[2], cell[5], cell[6]])

        # TODO change to mmcif
        for entry in scanAndFind_pattern(pdbDir, pattern):
            uniprot_id = entry.name.split('-')[1]
            if uniprot_id in infoDt:
                outPrefix = os.path.join(outdir, uniprot_id)
                # print(outPrefix)
                for item in infoDt[uniprot_id]:
                    try:
                        select_domain(outPrefix,
                                      entry.path,
                                      item[0],
                                      item[1],
                                      item[2])
                    except Exception as e:
                        print(e)
                        print(entry.name)

    def get_chain_scope(self, pdbDir, info):
        infoDt = defaultdict(str)
        with open(info, 'r') as f:
            for li in f:
                if re.match("#", li):
                    continue
                cell = reg_blank.split(li.strip())
                chain_letter = cell[2].split(":")[0]
                infoDt[cell[1]] = chain_letter

        for entry in scanAndFind_pattern(pdbDir, pattern_cif):
            pdb_id = entry.name[0:4].upper()
            if pdb_id in infoDt:
                # print(pdb_id)
                try:
                    select_chain(pdb_id, entry.path, infoDt[pdb_id])
                except Exception as e:
                    print(e)
                    print(entry.name)

    def get_domain_scope(self, pdbDir, ScopInfo):
        pdbDt = defaultdict(str)
        for entry in scanAndFind_pattern(pdbDir, pattern_cif):
            pdbid = entry.name[0:4].upper()
            pdbDt[pdbid] = entry.path

        with gzip.open(ScopInfo, 'rt') as f:
            for li in f:
                if re.match("#", li):
                    continue
                cell = li.strip().split()
                # print(cell)
                family, pdbid, chainPos, uniprot_id = cell[0:4]
                # print(chainPos)
                chainPosArr = parse_chain_region(chainPos)
                if chainPosArr:
                    chain, start, end = chainPosArr
                    if pdbid in pdbDt:
                        # print(pdbid, chain, start, end, family, uniprot_id)
                        outname = '.'.join(
                            [family, uniprot_id, pdbid])
                        try:
                            select_domain_mmCIF(
                                outname, pdbDt[pdbid], chain, start, end)
                        except Exception as inst:
                            print(inst)
                            print(pdbid)
                else:
                    print(li.strip())


if __name__ == '__main__':
    fire.Fire(RUN)
