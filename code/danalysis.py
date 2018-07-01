#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os.path
import pandas as pd
from piecash import open_book 

if __name__=='__main__':
    this_folder = '/home/guilherme/Dropbox/Docs/gnuCash/'
    s = open_book(os.path.join(this_folder, "gtm-controle.gnucash"), open_if_lock=True)
else:
    s = open_book(os.path.join("gtm-controle.gnucash"), open_if_lock=True)

transactions = [tr for tr in s.transactions  # query all transactions in the book/session and filter them on
                if (tr.post_date.date() >= datetime.date(2017,  6, 1)) & 
                   (tr.post_date.date() < datetime.date(2017, 11, 26))] 
rows_list=[]
for tr in transactions:
    for spl in tr.splits:
        dict1={
            'Date':pd.to_datetime(tr.post_date.date()),
            'Value':spl.value,
            'Type':spl.account.type,
            'Parent':spl.account,
            'Description':tr.description,
        }
        rows_list.append(dict1)
  
df = pd.DataFrame(rows_list)

# Ajustes no dataframe
df.Value = df.Value.astype(float)
df['Month']=pd.to_datetime(df.Date).dt.month
df['Year']=pd.to_datetime(df.Date).dt.year
df['Parent']=df.Parent.astype('string').str.replace('Account<|\[BRL\]>','')
# Filtrar Orphan-BRl e Imbalance-BRL
# df.Parent.str.contains('Imbalance-BRL|Orphan-BRL')
# df = df.drop(df[<some boolean condition>].index)
df = df.drop(df[df.Parent.str.contains('Imbalance-BRL|Orphan-BRL|template')].index)
df['Sublevel'] = [el[1] for el in df.Parent.str.split(':')] #list comprehention

# Analise de Despesas
# Total de Despesas
totalByTypeMonth=df[['Date','Month','Value','Type']].groupby(['Type','Month']).sum()
    
# Despesas Fixas e Variaveis
# pd.options.mode.chained_assignment = None > Disable SettingWithCopyWarning
despesas = df[df['Type']=='EXPENSE'].copy()
# Despesas por subclassificacao
despesas['Sublevel2']=[el[2] for el in despesas.Parent.str.split(':')] 
         # Despesas por subclassificação
despesas[['Month','Value','Sublevel2']].groupby(['Month','Sublevel2']).sum().\
unstack().Value.plot(kind='bar')
# Média de gastos por subclassificação
despesas[['Month','Value','Sublevel2']].groupby(['Sublevel2','Month']).sum().unstack().mean(axis=1)
aux = despesas[['Month','Value','Sublevel2']].groupby(['Sublevel2','Month']).sum().unstack()
aux.fillna(0,inplace=True)
aux.mean(axis=1) # Médias considerando todos os meses


# Complementar de df despesas
outros = df[df['Type']!='EXPENSE'].copy()

# Todos os registros com sublevel2 presentes para despesas apenas
allrecords = pd.concat([outros,despesas],axis=0,ignore_index = True,join='outer')

#json_despesas = pd.json.dumps(despesas.to_dict('records'))
#http://pandas.pydata.org/pandas-docs/stable/io.html#json
json_despesas = despesas.to_json(orient='records',date_format='iso')

# Teste com lean analytics
teste = despesas[['Date','Description','Value','Sublevel']].copy()
teste.columns=['t','name','value','category']
teste_json = teste.to_json(orient='records',date_format='iso')
import json
with open('despesas.txt', 'w') as outfile:
    json.dump(teste_json, outfile)
json_allrecords = allrecords.to_json(orient='records',date_format='iso')
#json_df = df.to_json(orient='records',date_format='iso')
s.close()
    
