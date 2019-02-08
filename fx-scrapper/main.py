import re
import os
import json
import base64
import requests
import pandas as pd

from datetime import datetime
from bs4 import BeautifulSoup
from google.cloud import datastore

# Constants
DS_KIND = 'FX'
CF_SCRAPPER_CF = "https://us-central1-shwecity-203616.cloudfunctions.net/cf-scrapper"

def main(event, context):
    response = {}    
    response['KBZ'] = get_kbz_ex_rate()
    print('Fetched KBZ')

    response['AYA'] = get_aya_ex_rate()
    print('Fetched AYA')
    
    response['CB'] = get_cb_ex_rate()
    print('Fetched CB')
    
    response['Central Bank'] = get_central_bank_ex_rate()
    print('Fetched Central Bank')
    
    response['MAB'] = get_mab_ex_rate()
    print('Fetched MAB')
    
    response['AGD'] = get_agd_ex_rate()
    print('Fetched AGD')
    
    response['UAB'] = get_uab_ex_rate()
    print('Fetched UAB')
    
    # Update GCP Data Store
    print('Updating FX Data Store')
    update_FX_DS_Entity(response)
    print('Updated FX Data Store')
    
    print(json.dumps(response))

def update_FX_DS_Entity(rates):
    ds_client = datastore.Client()
    for bank in rates:
        key = ds_client.key(DS_KIND, bank)
        fx = ds_client.get(key)
        fx = datastore.Entity(key=key) if fx is None else fx
        new_fx_rates = {}
        for currency in rates[bank]:
            for action in rates[bank][currency]:
                cur_index = 'EUR' if 'EURO' == currency else currency
                new_fx_rates[cur_index + '_' + action] = rates[bank][currency][action]
        new_fx_rates['updated_at'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') 
        fx.update(new_fx_rates)
        ds_client.put(fx)

def get_central_bank_ex_rate():
    response = {}
    url = "https://forex.cbm.gov.mm/api/latest"
    r = requests.get(url)
    rates = json.loads(r.text)['rates']
    currencies = ['USD', 'EUR', 'SGD', 'THB', 'MYR']
    for c in currencies:
        response[c] = {
            'BUY' : float(rates[c].replace(',','')),
            'SELL' : float(rates[c].replace(',',''))
        }
    return response

def get_uab_ex_rate():
    response = {}
    url = CF_SCRAPPER_CF + "?url=http://www.unitedamarabank.com/"
    r = requests.get(url)
    page = r.text
    soup = BeautifulSoup(page, 'lxml')
    soup = soup.find('div', {"class": "ex_rate"})
    rates = soup.findAll('li')
    rates = [rate.text.strip() for rate in rates][3:]
    length = int(len(rates)/3)
    for x in range(0, length):
        response[rates[x*3]] = {
            'BUY' : float(rates[(x*3)+1]),
            'SELL' : float(rates[(x*3)+2])
        }
    return response

def get_agd_ex_rate():
    response = {}
    url = "https://ccapi.agdbank.com:8080/ExchangeRate/index?callback=?"
    r = requests.get(url)
    page = r.text
    rates = json.loads(re.search(r'\(([^\)]+)\)', str(page)).group(1))

    for rate in rates['ExchangeRates']:
        if (rate['From'] == 'KYT'):
            response[rate['To']] = {
                'SELL' : float(rate['Rate'])
            }
        else:
            response[rate['From']]['BUY'] = float(rate['Rate'])

    return response    
   
def get_mab_ex_rate():
    response = {}
    url = CF_SCRAPPER_CF + "?url=https://www.mabbank.com/"
    r = requests.get(url)
    page = r.text
    soup = BeautifulSoup(page, 'lxml')
    soup = soup.find('div', {"class": "exchange-box"})
    rates = soup.findAll('p')[3:]
    
    currencies = []
    [currencies.append(rates[x].text) for x in range(0, len(rates)) if (x%3==0)]    
    
    for x in range(0, len(currencies)):
        response[currencies[x]] = {
            'BUY' : float(rates[(x*3)+1].text),
            'SELL' : float(rates[(x*3)+2].text)
        }
    return response
    
def get_cb_ex_rate():
    response = {}
    url = "https://www.cbbank.com.mm/admin/api.xml"
    r = requests.get(url)
    page = r.text
    soup = BeautifulSoup(page,'lxml')
    rates = soup.findAll('cbrate')
    for rate in rates:
        response[rate.find('currency').text] = {
            'BUY' : float(rate.find('buy').text),
            'SELL': float(rate.find('sell').text)
        }
    return response


def get_aya_ex_rate():
    response = {}
    url = "https://www.ayabank.com/en_US/"
    r = requests.get(url)
    page = r.text
    page = BeautifulSoup(page,'lxml')
    exchange_rate_detail = page.find("table", {"class": "tablepress tablepress-id-1"})
    table_df = pd.read_html(str(exchange_rate_detail))[0]
    for i in range(1,4):
        response[table_df[0][i]] = {
            'BUY' : float(table_df[1][i]),
            'SELL' : float(table_df[2][i])
        }
    return response

def get_kbz_ex_rate():
    response = {}
    url = "https://www.kbzbank.com/en/"
    r = requests.get(url)
    page = r.text
    page = BeautifulSoup(page,'lxml')
    exchange_rate_detail = page.find("div", {"class": "row exchange-rate"})
    er = exchange_rate_detail.findAll("div")[-4:]
    er = [e.text.replace('\n', '') for e in er]
    
    for e in er:
        response[e[0:3]] = {
            'BUY' : float(re.search(r'BUY (.*?) ', e).group(1)),
            'SELL' : float(re.search(r'SELL (.*?)$', e).group(1))
        }
    return response