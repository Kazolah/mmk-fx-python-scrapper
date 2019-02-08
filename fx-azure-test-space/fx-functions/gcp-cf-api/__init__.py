import logging
import os
import json
import azure.functions as func

from google.cloud import datastore
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.dirname(os.path.realpath(__file__)) + '/SC-credentials.json'
DS_KIND = 'FX'
DS_CLIENT = datastore.Client()

def main(req: func.HttpRequest) -> func.HttpResponse:
    response = {}
    currency = req.params.get('currency')
    currency = currency if currency else 'USD'
    response['BUY'] = get_best_buy(currency)
    response['SELL'] = get_best_sell(currency)
    response['rates'] = get_currency_columns(currency)
    response['updated_at'] = get_updated_at()
    return func.HttpResponse(json.dumps(response))

def get_best_sell(currency):
    best_rate = {}
    column = "%s_%s" % (currency, 'SELL')
    response = get_ordered_column(column, limit=2)
    logging.info(response)
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
    logging.info(response)
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
