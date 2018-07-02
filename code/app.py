#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
import datetime
import os.path
import pandas as pd
from piecash import open_book
#from nocache import nocache
from flask.ext.cache import Cache   

app = Flask(__name__)

# defina a configuração do cache (isso pode ser feito em um arquivo de settings)
app.config['CACHE_TYPE'] = 'null'

# instancie o cache e atribua a sua aplicação
app.cache = Cache(app)  


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/table")
def table():
    if __name__=='__main__':
        this_folder = '/home/guilherme/Dropbox/Docs/gnuCash/'
        s = open_book(os.path.join(this_folder, "gtm-controle.gnucash"), open_if_lock=True)
    else:
        s = open_book(os.path.join("gtm-controle.gnucash"), open_if_lock=True)

    today = datetime.datetime.today()
    transactions = [tr for tr in s.transactions  # query all transactions in the book/session and filter them on
                    if (tr.post_date.date() >= datetime.date(2016,  1, 1)) & 
                       (tr.post_date.date() <= datetime.date(today.year, today.month, today.day))] 
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
    df = df.drop(df[df.Parent.str.contains('Imbalance-BRL|Orphan-BRL|template')].index)
    df['Sublevel'] = [el[1] for el in df.Parent.str.split(':')] #list comprehention

    # Analise de Despesas
    # Total de Despesas
    totalByTypeMonth=df[['Date','Month','Value','Type']].groupby(['Type','Month']).sum()
        
    # Despesas Fixas e Variaveis
    # pd.options.mode.chained_assignment = None > Disable SettingWithCopyWarning
    despesas = df[df['Type']=='EXPENSE'].copy()
    return render_template("nav.html",expenses = despesas)

@app.route("/cashDash/despesas")
#@nocache
#https://arusahni.net/blog/2014/03/flask-nocache.html
def cashDash_despesas():
    if __name__=='__main__':
        this_folder = '/home/guilherme/Dropbox/Docs/gnuCash/'
        s = open_book(os.path.join(this_folder, "gtm-controle.gnucash"), open_if_lock=True)
    else:
        s = open_book(os.path.join("gtm-controle.gnucash"), open_if_lock=True)

    today = datetime.datetime.today()
    transactions = [tr for tr in s.transactions  # query all transactions in the book/session and filter them on
                    if (tr.post_date.date() >= datetime.date(2016,  1, 1)) & 
                       (tr.post_date.date() <= datetime.date(today.year, today.month, today.day))] 
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

    # Complementar de df despesas
    outros = df[df['Type']!='EXPENSE'].copy()

    # Todos os registros com sublevel2 presentes para despesas apenas
    allrecords = pd.concat([outros,despesas],axis=0,ignore_index = True,join='outer')

    #json_despesas = pd.json.dumps(despesas.to_dict('records'))
    #http://pandas.pydata.org/pandas-docs/stable/io.html#json
    json_despesas = despesas.to_json(orient='records',date_format='iso')
    json_allrecords = allrecords.to_json(orient='records',date_format='iso')
    #json_df = df.to_json(orient='records',date_format='iso')
    s.close()    
    return json_allrecords

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
