# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 19:27:42 2020

@author: missp
"""
import json
from nltk import PorterStemmer
import nltk
import socket
import numpy as np
import re
from nltk.stem import WordNetLemmatizer
from flask import Flask, jsonify, make_response, request
import threading
import pickle
import spacy
import requests
import json

def remover_t(data):
    data = re.sub('\S*@\S*\s?', '', data) 
    data = re.sub('\s+', ' ', data) 
    data = re.sub("\'", "", data)  
    return data

nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
def lemmatizationer(texts, allowed_postags=['NOUN','ADJ']):#, 'ADV',  'VERB'
    """https://spacy.io/api/annotation"""
 
    texts_out = []
    texts=[texts]
    for text in  texts :
      print(text[0])
      doc = nlp(" ".join(text.split())) 
      texts_out.append(" ".join([token.lemma_ for token in doc if token.pos_ in allowed_postags]))
    return texts_out 

app = Flask(__name__)
padding_size = 1000
model = pickle.load(open('finalized_model.pkl', 'rb'))
text_encoder = pickle.load(open('tokenizer.pkl', 'rb'))#tfds.features.text.TokenTextEncoder.load_from_file("/content/drive/My Drive/Colab Notebooks/models/sa_encoder.vocab")
print(text_encoder)
print('Model and Vocabalory loaded.......')

@app.route("/")
def hello():
    return "initilization"

def pad_to_size(vec, size):
    zeros = [0] * (size - len(vec))
    vec.extend(zeros)
    return vec


def predict_fn(predict_text, pad_size):
    corpus = remover_t(predict_text)
    corpus_lemma = lemmatizationer(corpus)
    corpus_lemma=np.array(corpus_lemma)
    encoded_text = text_encoder.transform(corpus_lemma)
    predictions = model.transform( encoded_text )
    return predictions.argmax()+1


@app.route('/seclassifier', methods=['POST'])
def predict_sentiment():
    text = request.get_json()['text']

    predictions = predict_fn(text, padding_size)
    pred=predictions.tolist()
    return jsonify({'predictions':pred})





import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from spacy.matcher import Matcher 
from spacy.tokens import Span 
import en_core_web_lg
nlp_model = en_core_web_lg.load()
import neuralcoref
import json
import os
from tqdm import tqdm

def printGraph(triples):

 
    #prepare graph
    
    #source=[tr[0] for tr in triples ]
    #relations=[tr[1] for tr in triples ]
    #target=[tr[2] for tr in triples ]
    source=[ ]
    relations=[]
    target=[ ]
    for i,triple in enumerate(triples):
        ss=triple[0] 
        rr=triple[1]
        tt=triple[2]
        #G.add_edge(triple[0], triple[1])
        if triple[0]!="":
            source.append(triple[0])
            relations.append("subj=>rel")
            target.append("no."+str(i+1)+": "+triple[1])
        #G.add_edge(triple[1], triple[2])
        if triple[2]!="":
            source.append("no."+str(i+1)+": "+triple[1])
            relations.append("rel=>obj")
            target.append(triple[2])
    kg_df = pd.DataFrame({'source':source, 'target':target, 'edge':relations})
     
    G=nx.from_pandas_edgelist(kg_df,  edge_attr=True, create_using=nx.MultiDiGraph())
 
    
    plt.figure(figsize=(len(triples),len(triples)))
     
    pos =  nx.spring_layout(G, iterations=10)
     
    edge_labels = {(source[i],target[i]):relations[i] for i in range(len(relations))} 
    nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels,font_color='red')




    nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)
    plt.show()

def getSentences(text):
    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    document = nlp(text)
    return [sent.string.strip() for sent in document.sents]

def printToken(token):
    print(token.text, "->", token.dep_)

def appendChunk(original, chunk):
    return original + ' ' + chunk

def isRelationCandidate(token):
    deps = ["aux", "ROOT", "adj", "attr", "agent","acomp"]
    return any(subs in token.dep_ for subs in deps)
 

def isConstructionCandidate(token):
    deps = [ "compound", "poss", "mod"]
    #deps = ["compound",   "mod"]
    return any(subs in token.dep_ for subs in deps)

def processSubjectObjectPairs(sentence,resoning_show=False,mid_show=False,final_show=False):
 
    ## chunk 1
 
    tokens = nlp_model(sentence)
    ent1 = ""
    ent2 = ""
    
    prv_tok_dep = ""    # dependency tag of previous token in the sentence
    prv_tok_text = ""   # previous token in the sentence
    aux_string=""
    prefix = ""
    modifier = ""
    relation = ''
    #############################################################
    once=False
    signal=False
    sentence_words=[word.text for word in tokens]
    for i,tok  in enumerate(tokens):
      ## chunk 2
       
      # if token is a punctuation mark then move on to the next token
      if tok.dep_ != "punct":
        if resoning_show:
          print("SHOW " +tok.text+ " dep: "+str(tok.dep_))
        if isRelationCandidate(tok) and tok.dep_!="ccomp":
            if relation.find(tok.text) <0:
              relation = appendChunk(relation, tok.text)
              if tok.dep_=="ROOT":
                  
                  relation= relation+" "+tokens[i+1].text if i+2<len(sentence_words) and tokens[i+1].dep_=="dobj" and tokens[i+2].dep_=="aux" else relation
                  #if i+2<len(sentence_words) and tokens[i+1].dep_=="dobj" and tokens[i+2].dep_=="aux": 
                  #    print((tokens[i].text,tokens[i+1].text,tokens[i+2].text,sentence))
        if tok.dep_=="aux" or tok.dep_=="auxpass":
            aux_string=tok.text
        if tok.dep_=="ccomp":
            relation =   aux_string+" "+tok.lemma_ if aux_string!="" else tok.lemma_
            aux_string=""
            
        if relation!="" and tok.dep_=="xcomp" and not once:   
            relation =  relation +" "+tok.lemma_
            once=True
        # check: token is a compound word or not
        if tok.dep_ == "compound":
          prefix = tok.text
          # if the previous word was also a 'compound' then add the current word to it
          if prv_tok_dep == "compound":
            prefix = prv_tok_text + " "+ tok.text
            if resoning_show:
                print("form a compound: "+prefix)
                
        # check: token is a modifier or not
        #if tok.dep_.endswith("mod") == True:
        if tok.dep_ ==  "amod" or  tok.dep_ ==  "mod" or tok.dep_ ==  "poss":
          modifier = tok.text
          # if the previous word was also a 'compound' then add the current word to it
          if prv_tok_dep == "compound":
            modifier = prv_tok_text + " "+ tok.text
            if resoning_show:
                print("form a modifier: "+modifier)
                
        ## chunk 3
        if tok.dep_.find("subj") == True:
          ent1 = modifier +" "+ prefix + " "+ tok.text
          if mid_show:
              print("form a "+tok.dep_+": "+ent1)
          prefix = ""
          modifier = ""
          prv_tok_dep = ""
          prv_tok_text = ""      
    
        ## chunk 4
        if tok.dep_.find("obj") == True:
          if  tok.dep_=="pobj" and i+1<len(sentence_words) and tokens[i+1].dep_=="nummod" :
              relation=relation+" "+tok.text+" "+tokens[i+1].text
              continue
          if ent2=='':    
              ent2 =modifier +" "+ prefix +" "+ "("+tok.text+")"
          else:
              
              ent2  = ent2+' '+ modifier if modifier not in ent2 else ent2
              ent2  = ent2+' '+ prefix if prefix not in ent2 else ent2
              ent2  = ent2+' '+ tok.text if tok.text not in ent2 else ent2
          if mid_show:
              print("form a "+tok.dep_+": "+ent2)
 
        ## chunk 5  
        # update variables
        prv_tok_dep = tok.dep_
        prv_tok_text = tok.text
    if ent2=="":
        ent2= "(No_Object)"
 
    return (ent1.strip(), relation.strip(), ent2.strip())  

def test(sentence,resoning_show=False):
    
    tokens = nlp_model(sentence)
    for i,tok  in enumerate(tokens):
            print("test SHOW " +tok.text+ " dep: "+str(tok.dep_))
            
def pride_if_line(sentence,resoning_show=False,mid_show=False,final_show=False):
 
    # 'that'-clause pattern matching rule
    
    ## chunk 1
 
    tokens = nlp_model(sentence)
    ent1 = ""
    ent2 = ""
    
    prv_tok_dep = ""    # dependency tag of previous token in the sentence
    prv_tok_text = ""   # previous token in the sentence
    aux_string=""
    prefix = ""
    modifier = ""
    relation = ''
    #############################################################
    sentence_words=[word.text for word in tokens]
    for i,tok  in enumerate(tokens):
      ## chunk 2
       
      # if token is a punctuation mark then move on to the next token
      if tok.dep_ != "punct":

        if tok.dep_=="ROOT":            
            relation=tok.text+" that(assumption_sentence)" if i+1<len(sentence_words) and sentence_words[i+1]=="that" else tok.text
            
            break


        # check: token is a compound word or not
        if tok.dep_ == "compound":
          prefix = tok.text
          # if the previous word was also a 'compound' then add the current word to it
          if prv_tok_dep == "compound":
            prefix = prv_tok_text + " "+ tok.text

                
        # check: token is a modifier or not
        #if tok.dep_.endswith("mod") == True:
        if tok.dep_ ==  "mod" or tok.dep_ ==  "poss":
          modifier = tok.text
          # if the previous word was also a 'compound' then add the current word to it
          if prv_tok_dep == "compound":
            modifier = prv_tok_text + " "+ tok.text
                
        ## chunk 3
        if tok.dep_.find("subj") == True:
          ent1 = modifier +" "+ prefix + " "+ tok.text

          prefix = ""
          modifier = ""
          prv_tok_dep = ""
          prv_tok_text = ""      
 

        ## chunk 5  
        # update variables
        prv_tok_dep = tok.dep_
        prv_tok_text = tok.text
    if i+1<len(sentence_words):
        subsetence_tri= processSubjectObjectPairs(" ".join(sentence_words[i+1:]),resoning_show,mid_show,final_show) 
    else:
        subsetence_tri= processSubjectObjectPairs(" ".join(sentence_words[i:]),resoning_show,mid_show,final_show) 
    if any([tri=="" for tri in  subsetence_tri]):
        return (ent1.strip(), relation.strip(),"") 
    return (ent1.strip(), relation.strip()," ".join(subsetence_tri) ) 


 

def greedy_if_line(sentence,resoning_show=False):
    # participial construction restoration
    tokens = nlp_model(sentence)
    ent1 = ""
    ent2 = ""
    
    prv_tok_dep = ""    # dependency tag of previous token in the sentence
    prv_tok_text = ""   # previous token in the sentence
 
    prefix = ""
    modifier = ""
 
    #############################################################
    sentence_restore=[]
    pair=[]
    if any([tk.dep_=="advcl"   for tk in tokens]):
 
        for i,tok  in enumerate(tokens):
            #print("test SHOW " +tok.text+ " dep: "+str(tok.dep_))
            if tok.dep_=="advcl"  :
                if tok.lemma_.endswith("s") or tok.lemma_.endswith("ch") or tok.lemma_.endswith("sh") or tok.lemma_.endswith("x"):
                    pair+=[tok.text,tok.lemma_+'es']
                else:
                    pair+=[tok.text,tok.lemma_+'s']
                #if resoning_show:
                #print("分分合合 SHOW " +pair[1])
 
            # check: token is a compound word or not
            if tok.dep_ == "compound":
              prefix = tok.text
              # if the previous word was also a 'compound' then add the current word to it
              if prv_tok_dep == "compound":
                prefix = prv_tok_text + " "+ tok.text
            
                    
            # check: token is a modifier or not
            #if tok.dep_.endswith("mod") == True:
            if tok.dep_ ==  "mod" or tok.dep_ ==  "poss":
              modifier = tok.text
              # if the previous word was also a 'compound' then add the current word to it
              if prv_tok_dep == "compound":
                modifier = prv_tok_text + " "+ tok.text
                    
            ## chunk 3
            if ent1=="" and tok.dep_.find("subj") == True:
              ent1 = modifier +" "+ prefix + " "+ tok.text
 
        return sentence.replace(pair[0],ent1+' '+pair[1])  
        
    else:
        return sentence

def anger_if_line(sentence,resoning_show=False,mid_show=False,final_show=False):
    #description 'that'-clause pattern matching 
    tokens = nlp_model(sentence)
    ent1 = ""
    ent2 = ""
    
    prv_tok_dep = ""    # dependency tag of previous token in the sentence
    prv_tok_text = ""   # previous token in the sentence
    aux_string=""
    prefix = ""
    modifier = ""
    relation = ''
    signal=False
    #############################################################
    sentence_words=[word.text for word in tokens]
    k=0
    for i,tok  in enumerate(tokens):
      ## chunk 2
       
      # if token is a punctuation mark then move on to the next token
      if tok.dep_ != "punct":

        if tok.dep_=="ROOT" and i+1<len(sentence_words) and any([tk.dep_=="mark" for tk in tokens]):
            signal=True            
            relation=tok.text+" that(description_sentence)" 
            for p,tk in enumerate(tokens):
                if tk.dep_=="mark":
                    k=p
                    break
            if k!=0:
                break

        # check: token is a compound word or not
        if tok.dep_ == "compound":
          prefix = tok.text
          # if the previous word was also a 'compound' then add the current word to it
          if prv_tok_dep == "compound":
            prefix = prv_tok_text + " "+ tok.text

                
        # check: token is a modifier or not
        #if tok.dep_.endswith("mod") == True:
        if tok.dep_ ==  "mod" or tok.dep_ ==  "poss":
          modifier = tok.text
          # if the previous word was also a 'compound' then add the current word to it
          if prv_tok_dep == "compound":
            modifier = prv_tok_text + " "+ tok.text
                
        ## chunk 3
        if tok.dep_.find("subj") == True:
          ent1 = modifier +" "+ prefix + " "+ tok.text

          prefix = ""
          modifier = ""
          prv_tok_dep = ""
          prv_tok_text = ""      
 

        ## chunk 5  
        # update variables
        prv_tok_dep = tok.dep_
        prv_tok_text = tok.text
    if signal:
        if k+1<len(sentence_words):
            temp_sentence=" ".join(sentence_words[k+1:]).replace('“',"").replace('”',"")
            temp_sentence=sloth_if_line(temp_sentence)
        else:
            temp_sentence=" ".join(sentence_words[k:])
            temp_sentence=sloth_if_line(temp_sentence)
            
        if isinstance(temp_sentence, str):
            subsetence_tri= processSubjectObjectPairs(temp_sentence,resoning_show,mid_show,final_show)
        
        
            if any([tri=="" for tri in  subsetence_tri]):
                return (ent1.strip(), relation.strip(),"") 
            
            return (ent1.strip(), relation.strip()," ".join(subsetence_tri) )
        else:
            sentence_list=sentence
            collection_list=[]
            for branch_sentence in sentence_list:
                branch_sentencet_tri=processSubjectObjectPairs(branch_sentence)
                if any([tri=="" for tri in  branch_sentencet_tri]):
                    collection_list.append( (ent1.strip(), relation.strip()," ".join(branch_sentencet_tri) )  )
                else:
                    collection_list.append( (ent1.strip(), relation.strip()," ".join(branch_sentencet_tri) )  )
    
            return collection_list
    
    else:
        sentence =sloth_if_line(sentence)
        ## chunk 1
        if isinstance(sentence, str):
            return processSubjectObjectPairs(sentence)
        else:
            sentence_list=sentence
            return  [processSubjectObjectPairs(branch_sentence) for branch_sentence in sentence_list]
    
 


def sloth_if_line(sentence):
    # coordinate conjunction branching
    tokens = nlp_model(sentence)
    ent1 = ""
    ent2 = ""
    
    prv_tok_dep = ""    # dependency tag of previous token in the sentence
    prv_tok_text = ""   # previous token in the sentence
 
    prefix = ""
    modifier = ""
 
    #############################################################
    sentence_restore=[]
    pair=[]
    ROOT_signal=False
    ROOT_pos=0
    split_pos=0
    if sentence.find(" and "):
        #this case handle 'and'==cc after ROOT (brachinng sentences)
        for i,tok  in enumerate(tokens):
            #print("test SHOW " +tok.text+ " dep: "+str(tok.dep_))
            if ROOT_signal and tok.dep_=="ROOT": 
                #print('many ROOTs')
                return " ".join([t.text for t in tokens[:i]]) if i <len(tokens) else sentence
                
            if ROOT_signal and tok.dep_=="cc" and tok.text=="and": 
                split_pos=i
                return [" ".join([t.text for t in tokens[:split_pos+1]])," ".join([t.text for t in tokens[:ROOT_pos]])+' '+" ".join([t.text for t in tokens[ split_pos+1:]])] #if split_pos+1<len(tokens)
                #V+O1 and O2
                #V1+O1 and V2+O2
            if tok.dep_=="ROOT": 
                ROOT_signal=True
                ROOT_pos=i
        return sentence  
        
    else:
        #this case handle many ROOTs (abnormal cases)
        for i,tok  in enumerate(tokens):
            #print("test SHOW " +tok.text+ " dep: "+str(tok.dep_))
            if ROOT_signal and tok.dep_=="ROOT": 
                print('many ROOTs')
                return " ".join([t.text for t in tokens[:i]]) if i <len(tokens) else sentence             
            if tok.dep_=="ROOT": 
                ROOT_signal=True
        return sentence
def envy_if_line(sentence,resoning_show=False):
    
    tokens = nlp_model(sentence)
    comma_ps=[i  for i,tok  in enumerate(tokens) if tok.text==',']
    sentence_words=[word.text for word in tokens]
    for ncp,cps  in enumerate(comma_ps):
        if cps+3< len(tokens) and ncp+1 <len(comma_ps) and tokens[cps+1].dep_=="nsubjpass" and tokens[cps+2].dep_=="auxpass" and tokens[cps+3].dep_=="relcl":
            
            return " ".join(sentence_words[:cps])+' '+" ".join(sentence_words[comma_ps[ncp+1]:]),False
    return sentence,True

def KG_terminator(title, text,create_graph=False):
    text=text.replace(u'\xa0', u' ')
    text=text.replace("\n\n"," ")
    sentences = getSentences(text)
    #nlp_model = spacy.load('en_core_web_sm')
    
    
    triples = []
    #print (text)
    triples_sentence = []
    judge=["if","will","would"]
    no_include=["despite","although"]
    prev_triple_len=0
    for sen_id,main_sentence in tqdm(enumerate(sentences)):
        show_sentence=main_sentence
        main_sentence=main_sentence.split(':')[0]
        main_sentence=main_sentence.replace(' we ',' court ')
        doc = nlp_model(main_sentence)
        main_sentence=doc._.coref_resolved
        main_sentence=greedy_if_line(main_sentence)
        main_sentence=main_sentence.split('—')[0]
        main_sentence, envy=envy_if_line( main_sentence)
        #print("")
        #if main_sentence.find('Specifically')>=0:
        #    test(main_sentence)
        if main_sentence.find(", and")<0 and main_sentence.find(", but")<0:
    
            for sentence  in main_sentence.split(","):

                if any([ key in sentence.lower() for key in no_include]):
                    continue
                if any([ key in sentence.lower() for key in judge]):
                    
                    
                    #print("")
                    tri=pride_if_line(sentence,resoning_show=False)
                    #we do not let sloth and pride work together
                    if tri[0]!='' and tri[2]!='' and tri[2]!="that" and tri not in triples:
                        triples.append(tri)
                        triples_sentence.append((tri,show_sentence,sen_id))
                else:
                    tri=anger_if_line(sentence)
                    if isinstance(tri, tuple):
                        if tri[0]!='' and tri[2]!='' and tri[2]!="that" and tri[2].find('(No_Object)')<0 and tri not in triples:
                            triples.append(tri)
                            triples_sentence.append((tri,show_sentence,sen_id))
                    else:
                        tri_list=tri
                        for tri in tri_list:
                            if tri[0]!='' and tri[2]!='' and tri[2]!="that"and tri[2].find('(No_Object)')<0 and tri not in triples:
                                triples.append(tri)
                                triples_sentence.append((tri,show_sentence,sen_id))


        else:
            #show_sentence=main_sentence 
            main_sentence_later=''
            if main_sentence.find(", and")>0:
                
                if len(main_sentence.split(', and'))>=2:
                    main_sentence_later=main_sentence.split(', and')[1]
                    
                main_sentence=main_sentence.split(', and')[0]#+main_sentence.split(',')[-1]#.replace(' and','')#.replace(' that','') #if 'and' not in main_sentence.split(',')[-1] else main_sentence.split(', and')[0]
            if main_sentence.find(", but")>0:
                main_sentence=main_sentence.split(', but')[0]
            #test(main_sentence)
            #print("")
            tri=anger_if_line(main_sentence)
            #print(type(tri))
            if isinstance(tri, tuple):
                
                if tri[0]!='' and tri[2]!='' and tri[2].find('(No_Object)')<0 and tri not in triples:
                    triples.append(tri)
                    triples_sentence.append((tri,show_sentence,sen_id))
 
            else:
                tri_list=tri
                for tri in tri_list:
                    if tri[0]!='' and tri[2]!='' and tri[2].find('(No_Object)')<0 and tri not in triples:
                        triples.append(tri)
                        triples_sentence.append((tri,show_sentence,sen_id))
            if main_sentence_later!='':
                if main_sentence_later.startswith(' that'):
                    print('wow')
                    subsetence_tri= processSubjectObjectPairs(main_sentence_later[5:])
                    that_tri=(tri[0],tri[1],' '.join(subsetence_tri))
                    if subsetence_tri[0]!='' and subsetence_tri[2]!='' and subsetence_tri[2].find('(No_Object)')<0 and that_tri not in triples:
                        
                        triples.append(that_tri)
                        triples_sentence.append((that_tri,show_sentence,sen_id))
                else:
                    main_sentence= main_sentence_later   
                    tri=anger_if_line(main_sentence)
                    #print(type(tri))
                    if isinstance(tri, tuple):
                        
                        if tri[0]!='' and tri[2]!='' and tri[2].find('(No_Object)')<0 and tri not in triples:
                            triples.append(tri)
                            triples_sentence.append((tri,show_sentence,sen_id))
 
                    else:
                        tri_list=tri
                        for tri in tri_list:
                            if tri[0]!='' and tri[2]!='' and tri[2].find('(No_Object)')<0 and tri not in triples:
                                triples.append(tri)
                                triples_sentence.append((tri,show_sentence,sen_id))
        # this part is for final d3 can show where we do and not do relation extraction
        #if prev_triple_len==len(triples):
        #    triples_sentence.append((('','NO RELATION AVALIBLE',''),show_sentence))
        #else:
        #    prev_triple_len=len(triples)
    if len(triples_sentence)==0:
        print(title,'WARNING for no triple')
        print('')
    else:
        print(title,len(triples_sentence))
        print('')
    if create_graph:
      printGraph(triples)
      for i,triple in enumerate(triples_sentence):
          print("sen"+str(i+1),triple,sentences[triple[2]])

    #with open('output_files/'+title+'triples_sentence.json', 'w') as outfile:
    #    json.dump([triples_sentence,sentences], outfile, indent=4)
    return [triples_sentence,sentences]

def txt_list(files):
  vector_list=[]
  for name in files:
    #print(name)
 
    with open(name, encoding="utf-8") as f:
        vector_list.append(f.read())
  return vector_list
 




if __name__ == "__main__":
    print(socket.gethostbyname(socket.gethostname()))
 
    threading.Thread(target=app.run, kwargs={'host':'0.0.0.0','port':4444}).start()

    req = requests.get("http://192.168.56.1:4444/")
    print(req.status_code)
    print(req.text)
 
    #tt=
    '''
    As more than three thousand docket entry filings, two jury trials, and several appeals have already taken place in this case, a brief recitation of the relevant facts is helpful to understand the procedural context in which the parties' motions are made. Apple and Samsung sell competing smartphones and tablets. On April 15, 2011, Apple filed suit against Samsung, asserting numerous intellectual property and antitrust claims. See ECF No. 1. In July and August 2012, after pretrial case narrowing, Apple tried to a jury claims as to three utility patents, four design patents, one registered trade dress, and three unregistered trade dresses against 28 accused Samsung products. See ECF No. 1931. The jury found that 26 of the 28 accused products infringed or diluted one or more of Apple's asserted intellectual property rights and awarded Apple $1,049,343,540 in damages. Id. at 15. Following a multitude of post-trial orders, the Court held a partial damages retrial in November 2013. See ECF No. 2822. The total damages award against Samsung ultimately amounted to $929,780,039. ECF No. 3017.
    Samsung filed a Notice of Appeal to the Federal Circuit in March 2014. ECF No. 3018. On May 18, 2015, the Federal Circuit affirmed-in-part, reversed-in-part, vacated-in-part, and remanded this Court's judgment. ECF No. 3271. The Federal Circuit affirmed the validity and infringement judgments with respect to Apple's design and utility patents, and "the damages awarded for the design and utility patent infringements appealed by Samsung." Id., at 4. However, the Federal Circuit reversed "the jury's findings that the asserted trade dresses are protectable" and vacated the damages awards against the Samsung products that were found liable for trade dress dilution. Id. The Federal Circuit remanded "for immediate entry of final judgment on all damages awards not predicated on Apple's trade dress claims and for any further proceedings necessitated by our decision to vacate the jury's verdicts on the unregistered and registered trade dress claims." Id., at 33.
    The Federal Circuit's vacatur of the jury's verdicts on trade tress claims required retrial of damages for five Samsung products on remand. Upon receipt of the Federal Circuit's mandate on September 1, 2015, ECF No. 3273, the Court issued a Case Management Order setting retrial for Spring 2016. ECF No. 3272, at 3 ("September 1, 2015 Order"). As it did in connection with the retrial of damages in November 2013, see ECF No. 2316, at 2-3, the Court again ordered that the parties would not be permitted to expand the scope of the damages remand trial:
    Pursuant to the Federal Circuit's mandate, on September 18, 2015, this Court also entered partial final judgment against Samsung and in favor of Apple in the amount of $548,176,477 according to the affirmed damages awards for 18 Samsung products. ECF No. 3290. Samsung appealed the Court's entry of partial final judgment to the Federal Circuit on September 21, 2015. ECF No. 3292. The Federal Circuit summarily affirmed this Court's entry of partial final judgment. ECF No. 3319. This Court again received the mandate from the Federal Circuit on December 1, 2015. ECF No. 3321. That partial final judgment has been paid and is not at issue here. ECF No. 3332.
    The instant retrial on damages will be the parties' fourth jury trial before this Court, third jury trial in the instant case, and second damages retrial in the instant case. The sole purpose of the instant damages retrial is to determine the amount of damages for the infringement of Apple's '163, '381, '915, D'305, D'677 and/or D'087 Patents by five Samsung products: the Fascinate, Galaxy S4G, Galaxy S Showcase, Mesmerize, and Vibrant.
    The Court will not allow substitution of damages experts absent extraordinary circumstances such as Mr. Musika's death after the 2012 jury trial. The Court will not allow supplemental fact discovery. The Court will not permit the parties to expand the scope of the damages retrial and will not allow the parties to rely on new sales data, new products, new methodologies or new theories. . . .
    The Court's prior rulings on the parties' Daubert motions, motions in limine, discovery disputes, and evidentiary objections will main in effect as law of the case. The parties may not relitigate these issues.
    Each side is limited to one motion to strike, which may not exceed five pages. Each side's opposition shall not exceed five pages. Each side's reply shall not exceed three pages.
    Id. at 2-3. Following a case management conference on September 18, 2015, the Court set a final pretrial and trial schedule in a further Case Management Order. ECF No. 3289. The parties' instant Motions to Strike followed.
    Apple moves to strike portions of Wagner's November 2015 Report, and Samsung moves to strike portions of Davis's November 2015 Report. In addition to its Motion, Apple filed both an opposition (ECF No. 3345-3, "Apple Opp.") to Samsung's Motion and a Reply (ECF No. 3359-3, "Apple Reply") in support of Apple's Motion. Samsung has similarly filed an opposition (ECF No. 3347-3, "Samsung Opp.") to Apple's Motion and a Reply (ECF No. 3361-3, "Samsung Reply") in support of Samsung's Motion. Additionally, full copies of Wagner's Corrected Expert Report of April 20, 2012 ("Wagner's April 2012 Report"); Wagner's Supplement Expert Report of May 11, 2012 ("Wagner's May 2012 Report"); Wagner's Updated Rebuttal Report of August 26, 2013 ("Wagner's August 2013 Report"); Wagner's Rebuttal Expert Report for Third Trial on Damages of November 6, 2015 ("Wagner's November 2015 Report"); Musika's Expert Report of March 22, 2012 ("Musika's March 2012 Report"); Musika's Supplemental Expert Report of May 8, 2012 ("Musika's May 2012 Report"); Davis's Expert Report of August 23, 2013 ("Davis's August 2013 Report"); and Davis's Updated Expert Report of November 6, 2015 ("Davis's November 2015 Report") are on file with the Court.
    '''
    
    
    
    #please input ./new_file.txt
    print("please input new_file.txt (you can create one txt and rename it into new unique one)")
    file_name = input()
    with open(file_name, encoding="utf-8") as f:
        tt=f.read()
    tt=tt.replace('\n',' ')
    
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {"text":tt}
    req = requests.post("http://192.168.56.1:4444/seclassifier",  data=json.dumps(data), headers=headers)
    
    print(req.status_code)
    ans=json.loads(req.text)
    print(ans['predictions'])
    
    
    with open('file_topic.json') as f:
      file_topic_and_topicsdict = json.load(f)
    print('load lda file complete')
    
    file_topic_and_topicsdict[file_name]=[ans['predictions'],1.0]
    print('add lda_complete')
    
    with open('file_topic.json', 'w') as output_file:
      json.dump(file_topic_and_topicsdict, output_file, indent=4, sort_keys=True)
      
    neuralcoref.add_to_pipe(nlp_model,greedyness=0.5,store_scores=True)


    with open('all_files_triples_sentence.json') as f:
      file_triple_sentence = json.load(f)
      print('load kg file complete')
    file_triple_sentence[file_name]=KG_terminator(file_name, tt)
    print('create kg complete')

    with open('all_files_triples_sentence.json', 'w') as outfile:
        json.dump(file_triple_sentence, outfile, indent=4)
    print('add kg_complete') 
 
    print("The new file is processed by KG and LDA")
    print("The processed data is appended into all_files_triples_sentence.json and file_topic.json")
    print("Enjoy our service~")
      