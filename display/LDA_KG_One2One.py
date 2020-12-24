# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 03:02:47 2020

@author: missp
"""
import json

with open('file_topic_1120.json') as f:
  LDA = json.load(f)

with open('all_files_triples_sentence.json') as f:
  KG = json.load(f)

PLDA={}
i=[0,0,0,0]
for ld in LDA:
    if ld in KG:
        PLDA[ld]=LDA[ld]
        i[LDA[ld][0]]+=1
    elif ld.replace('_LDA.txt','.txt') in KG :
        PLDA[ld.replace('_LDA.txt','.txt')]=LDA[ld]
        i[LDA[ld][0]]+=1
    elif ld.replace('_LDA.txt','_KG.txt') in KG:
        PLDA[ld.replace('_LDA.txt','_KG.txt')]=LDA[ld]
        i[LDA[ld][0]]+=1
print(len(PLDA),len(LDA))
print(i)
with open('file_topic_pruning.json', 'w') as output_file:
  json.dump(PLDA, output_file, indent=4, sort_keys=True)