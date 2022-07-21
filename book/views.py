from django.shortcuts import render
import random
import string
import datetime
import pandas as pd
import numpy as np
import sqlite3
from django_pandas.io import read_frame

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auctum.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django
django.setup()

from book.models import transactions, balances

def pushPair(ccy1,ccy2):
    pair = pd.DataFrame(index=[0],columns=['pair_id','ccy1','ccy2'])
    pair.pair_id[0] = ccy1 + ccy2
    pair.ccy1[0] = ccy1
    pair.ccy2[0] = ccy2   
    sqlConn = sqlite3.connect('C:\\Users\\pbr\\auctum\\db.sqlite3')
    pair.to_sql('pairs',sqlConn, if_exists='append', index=False)
    sqlConn.close()

def cleanSQL():
    sqlConn = sqlite3.connect('C:\\Users\\pbr\\auctum\\db.sqlite3')
    sqlCursor = sqlConn.cursor()
    sqlCursor.execute('DELETE FROM transactions')
    sqlConn.commit()
    
    senders = ['0x_Pierre','0x_Sarah','0x_Lea']
    tokens = ['eth','crv','usdc']
    balances = pd.DataFrame(columns=tokens)
    balances['sender'] = senders    
    balances.eth = 2
    balances.crv = 2500
    balances.usdc = 5000
    balances.to_sql('balances',sqlConn, if_exists='replace', index=False)    
  
    sqlConn.close()
    
def bookAggregateor(pair):
        
    tx = transactions.objects.all().filter(pair=pair).filter(matched='Pending')
    tx = read_frame(tx)  
    
    BID_tx = tx[tx.side == 'Buy']
    BID_price = np.sort(BID_tx.price.unique())
    BID_book = pd.DataFrame(index=BID_price,columns=['qty_bid'])
    for price in BID_book.index:
        BID_book.qty_bid[price] = BID_tx.qty_side[BID_tx.price == price].sum()
    BID_book = BID_book.sort_index(ascending=False)
    BID_book = BID_book.reset_index().rename(columns={'index':'price_bid'})

    ASK_tx = tx[tx.side == 'Sell']
    ASK_price = np.sort(ASK_tx.price.unique())
    ASK_book = pd.DataFrame(index=ASK_price,columns=['qty_ask'])
    for price in ASK_book.index:
        ASK_book.qty_ask[price] = ASK_tx.qty_side[ASK_tx.price == price].sum()
    ASK_book = ASK_book.reset_index().rename(columns={'index':'price_ask'})
    
    book = pd.concat([BID_book, ASK_book], axis=1, join="outer")
    book = book.fillna('')    
    
    return book 

def tx_id_generator(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    numbers = string.digits
    result_str = '0x' + ''.join(random.choice(letters+numbers) for i in range(length))
    return(result_str)

def tx_matcher():
    
    tx = transactions.objects.all().filter(matched='Pending')
    tx = read_frame(tx)
    tx = tx.set_index('id')
    tx.index.names = ['tx_id']  
    
    balance = balances.objects.all()
    balance = read_frame(balance)
    balance = balance.set_index('id')
    balance.index.names = ['sender']  
    
    for tx_id in tx.index:
        opposite_side = 'Sell' if tx.side[tx_id] == 'Buy' else 'Buy'
        opposite_matching_id = f"{opposite_side}_{tx.pair[tx_id]}_{tx.qty_side[tx_id]}_{tx.qty_other_side[tx_id]}"
        matching_tx = tx[(tx.matching_id == opposite_matching_id) & (tx.matched == 'Pending')]
        if len(matching_tx) > 0:
            #Match "Resting" Tx
            tx_id_matched = matching_tx.index[0]
            ccy1 = tx.token_receive[tx_id_matched].lower()
            qty1 = tx.qty_receive[tx_id_matched]
            sender1 = tx.sender[tx_id_matched]
            balance[ccy1][sender1] = balance[ccy1][sender1] + qty1
            tx.matched[tx_id_matched] = 'Matched'
            #Match "Hitting" Tx
            ccy2 = tx.token_receive[tx_id].lower()
            qty2 = tx.qty_receive[tx_id]
            sender2 = tx.sender[tx_id]            
            balance[ccy2][sender2] = balance[ccy2][sender2] + qty2            
            tx.matched[tx_id] = 'Matched'
            
            sqlConn = sqlite3.connect('C:\\Users\\pbr\\auctum\\db.sqlite3') 
            balance.to_sql('balances',sqlConn, if_exists='replace') 
            tx.to_sql('transactions',sqlConn, if_exists='replace')

def order_generator(request):
    
    sender = request.POST.get('sender','')
    pair = request.POST.get('pair','')
    side = request.POST.get('side','')
    qty_side = float(request.POST.get('qty_side',0))
    price = float(request.POST.get('price',0))
    orderSummary = ''
    orderExplanation = ''   
    sqlConn = sqlite3.connect('C:\\Users\\pbr\\auctum\\db.sqlite3')      
    sqlCurs = sqlConn.cursor()
            
    if qty_side <= 0 or price <= 0 :
        orderSummary = 'Submit a valid order / Only positive values are allowed.'
        transactions = 0
        
    elif sender != '':
                  
        pairDetails = pd.read_sql('SELECT * FROM pairs', sqlConn,index_col='pair_id')
        qty_other_side = round(qty_side*price,3)
        
        orderSummary = f'Order submitted! {sender} {side} {qty_side} {pair} @ {price}' if sender != '' else ''
        pushDB = pd.DataFrame(index=[0],columns=['tx_id','sender','pair','side','qty_side','qty_other_side','timestamp','matched','token_send','token_receive','qty_send','qty_receive'])
    
        pushDB['token_send'][0] = pairDetails.ccy2[pair] if side == 'Buy' else pairDetails.ccy1[pair]
        pushDB['qty_send'][0] = qty_other_side if side == 'Buy' else qty_side
        pushDB['token_receive'][0] = pairDetails.ccy1[pair] if side == 'Buy' else pairDetails.ccy2[pair]
        pushDB['qty_receive'][0] = qty_side if side == 'Buy' else qty_other_side
 
        balance = balances.objects.all().filter(id=sender)
        balance = read_frame(balance)
        tokenSend = pushDB['token_send'][0].lower()
        balance_token = balance[tokenSend][0]

        if pushDB['qty_send'][0] > balance_token:
            orderSummary = f"Balance not sufficient. Order requires: {pushDB['qty_send'][0]} {pushDB['token_send'][0]} - vs. Balance: {balance_token} {pushDB['token_send'][0]}."
        else:
            orderExplanation = f"{sender} send {pushDB['qty_send'][0]} {pushDB['token_send'][0]} to the Platform - Will be unlocked against {pushDB['qty_receive'][0]} {pushDB['token_receive'][0]} (Price of {price})" if sender != '' else ''
            newBalance = balance_token - pushDB['qty_send'][0]
            sql = f"UPDATE balances SET {tokenSend} = {newBalance} WHERE sender = '{sender}'"
            sqlCurs.execute(f'{sql}')
            sqlConn.commit()
            
            pushDB['tx_id'] = tx_id_generator(10)
            pushDB['sender'] = sender
            pushDB['pair'] = pair
            pushDB['side'] = side
            pushDB['qty_side'] = qty_side
            pushDB['qty_other_side'] = qty_other_side
            pushDB['price'] = price
            pushDB['timestamp'] = datetime.datetime.now()    
            pushDB['matched'] = 'Pending'
            pushDB['matching_id'] = f"{pushDB['side'][0]}_{pushDB['pair'][0]}_{pushDB['qty_side'][0]}_{pushDB['qty_other_side'][0]}"
            pushDB.to_sql('transactions',sqlConn, if_exists='append', index=False)
            tx_matcher()
            
    else:
        orderSummary = 'Submit a valid order / Select Address - Only positive values are allowed.'
                   
    transactions = pd.read_sql('SELECT * FROM transactions', sqlConn)
    transactions = transactions.sort_values('timestamp',ascending=False)
    
    return render(request,'book/order_generator.html', {
            
            'sender':sender,
            'pair':pair,
            'side':side,
            'qty_side':qty_side,
            'price':price,
            'orderSummary':orderSummary,
            'orderExplanation':orderExplanation,
            'transactions':transactions,
            
                                                    })

def ethusdc(request):
        
    book = bookAggregateor(pair='ETHUSDC')

    return render(request,'book/ethusdc.html', {
            
            'book':book,
            
                                                    })

def pools(request):
        
    book_ETHUSDC = bookAggregateor(pair='ETHUSDC')
    book_CRVUSDC = bookAggregateor(pair='CRVUSDC')
    book_ETHCRV = bookAggregateor(pair='ETHCRV')

    return render(request,'book/pools.html', {
            
            'book_ETHUSDC':book_ETHUSDC,
            'book_CRVUSDC':book_CRVUSDC,
            'book_ETHCRV':book_ETHCRV,
            
                                                    })

def sender_balances(request):
    
    query_balances = balances.objects.all()
    query_balances = read_frame(query_balances)
    query_balances = query_balances.set_index('id')
    query_balances.loc['0x_Book'] = 0
    
    tx = transactions.objects.all().filter(matched='Pending')
    tx = read_frame(tx)
    
    for token in query_balances.columns:
        query_balances[token]['0x_Book'] = tx.qty_send[tx.token_send == token.upper()].sum()

    return render(request,'book/sender_balances.html', {
            
            'query_balances':query_balances,
            
                                                    })