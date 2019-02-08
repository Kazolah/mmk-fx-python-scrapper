import os
import json
from flask import jsonify
from google.cloud import datastore

DS_KIND = 'FX'
DS_CLIENT = datastore.Client()
API_TOKEN = ''

def main(request):
    response = {}
    if not request.args and 'currency' not in request.args:
        return jsonify({'error': 'Bad request. Missing required parameters.'}), 400
    
    if 'api-token' not in request.args:
        return jsonify({'error': 'Bad request'}), 400

    if request.args['api-token'] != API_TOKEN:
        return jsonify({'error': 'Bad request'}), 400

    print(request.args)
    currency = request.args['currency']
    print(currency)
    response['BUY'] = get_best_buy(currency)
    response['SELL'] = get_best_sell(currency)
    response['rates'] = get_currency_columns(currency)
    response['updated_at'] = get_updated_at()
    response = jsonify(response)
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Methods', 'GET')
    return response

def get_best_sell(currency):
    best_rate = {}
    column = "%s_%s" % (currency, 'SELL')
    response = get_ordered_column(column, limit=2)
    response = response[1] if (response[0].key.name=='Central Bank') else response[0]
    best_rate = {
        "bank" : response.key.name,
        column : response[column] 
    }
    return best_rate

def get_best_buy(currency):
    best_rate = {}
    column = "%s_%s" % (currency, 'BUY')
    # Reverse order is -Column
    response = get_ordered_column("-" + column, limit=2)
    response = response[1] if (response[0].key.name=='Central Bank') else response[0]
    best_rate = {
        "bank" : response.key.name,
        column : response[column] 
    }
    return best_rate

def get_ordered_column(column, limit=10):
    response = {}
    query = DS_CLIENT.query(kind=DS_KIND)
    query.order = [column]
    query.projection = [column.replace('-', '')]
    return list(query.fetch(limit=limit))

def get_updated_at():
    query = DS_CLIENT.query(kind=DS_KIND)
    query.projection = ['updated_at']
    response = list(query.fetch(limit=1))
    return response[0]['updated_at']

def get_currency_columns(currency):
    response = []
    rates = {}
    buy_col = currency + '_BUY'
    sell_col = currency + '_SELL'

    query = DS_CLIENT.query(kind=DS_KIND)
    query.projection = [buy_col]
    buy_list = list(query.fetch())
    for x in range(0, len(buy_list)):
        rates[buy_list[x].key.name] = {
            buy_col : buy_list[x][buy_col]
        }

    query.projection = [sell_col]
    sell_list = list(query.fetch())    
    for x in range(0, len(sell_list)):
        rates[sell_list[x].key.name][sell_col] = sell_list[x][sell_col]

    for rate, value in rates.items():
        response.append({
            buy_col : value[buy_col],
            sell_col: value[sell_col],
            'bank' : rate
        })
    return response

def get_ds_entity():
    fx_rates = {}
    query = DS_CLIENT.query(kind=DS_KIND)
    response = list(query.fetch())
    for x in range(0, len(response)):
        fx_rates[response[x].key.name] = response[x]
    
    return fx_rates
