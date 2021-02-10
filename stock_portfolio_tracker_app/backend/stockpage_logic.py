from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from yahoofinancials import YahooFinancials

from ..models import Currency, Stocks, ProfitAdjustment

import requests
import json
import datetime

API_KEY = "QW5STDSFU45AUKEU"
DEFAULT_CURRENCY_ID = 8

def logout_user(request):
    logout(request)
    return True

#True for valid stock, false for invalid stock
def finance_api_get_stock_validator(stock_ticker):
    request = YahooFinancials(stock_ticker)
    data = request.get_summary_data()[stock_ticker_uppercase]

    if data == None:
        return False
    else:
        return True

def is_integer(num):
    try:
        int(num)
    except ValueError:
        return False
    else:
        return True

def is_float(num):
    try:
        float(num)
    except ValueError:
        return False
    else:
        return True

def is_correct_date_format(date_purchased):
    try:
        datetime.datetime.strptime(date_purchased, '%d/%m/%Y')
    except ValueError:
        return False
    else:
        return True

#True for valid, False for invalid
def stock_details_validator(user_id, currency_id, stock_ticker, average_price, quantity, date_purchased):
    if not User.objects.filter(pk=user_id).exists():
        print("USER")
        return False

    if not Currency.objects.filter(pk=currency_id).exists():
        print("CURRENCY")
        return False

    if finance_api_get_stock_validator(stock_ticker) == False:
        print("STOCKTICKER")
        return False

    if not is_float(average_price):
        print("AVGPRICE")
        return False

    if not is_integer(quantity):
        print("QUANTITY")
        return False

    if not is_correct_date_format(date_purchased):
        print("DATE")
        return False

    return True

def create_stock_entry(request):
    post_request = request.POST
    user_id = request.user.id
    currency_id = int(post_request["stockpage-addcurrency-2"])
    stock_ticker = post_request["stockpage-addstockticker-2"]
    average_price = float(post_request["stockpage-addaverageprice-2"])
    quantity = int(post_request["stockpage-addquantity-2"])
    date_purchased = post_request["stockpage-adddatepurchased-2"]

    user = User.objects.get(pk=user_id)
    currency = Currency.objects.get(pk=currency_id)

    stock = Stocks(user_id=user, currency_id=currency, stock_ticker=stock_ticker, average_price=average_price, quantity=quantity, date_purchased=date_purchased)

    stock.save()

def add_stock_handler(request):
    post_request = request.POST
    user_id = request.user.id
    currency_id = post_request["stockpage-addcurrency-2"]
    stock_ticker = post_request["stockpage-addstockticker-2"]
    average_price = post_request["stockpage-addaverageprice-2"]
    quantity = post_request["stockpage-addquantity-2"]
    date_purchased = post_request["stockpage-adddatepurchased-2"]

    result = stock_details_validator(user_id, currency_id, stock_ticker, average_price, quantity, date_purchased)

    if result == False:
        return False
    else:
        create_stock_entry(request)
        return True

def finance_api_get_stock_price(stock_ticker):
    request = YahooFinancials(stock_ticker)
    data = request.get_stock_price_data()[stock_ticker]
    current_price = float(data['regularMarketPrice'])

    return current_price

def finance_api_get_exchange_rate(from_currency_id, to_currency_id):
    from_currency_code = Currency.objects.get(pk=from_currency_id).currency_code
    to_currency_code = Currency.objects.get(pk=to_currency_id).currency_code

    if from_currency_code == to_currency_code:
        return 1
    else:
        if from_currency_code == "USD":
            from_currency_code = ""

        currency_code_for_request = "{}{}=X".format(from_currency_code, to_currency_code)
        request = YahooFinancials(currency_code_for_request)
        data = request.get_summary_data()[currency_code_for_request]
        exchange_rate = data['ask']

        return exchange_rate

def finance_api_get_currency_id(stock_ticker):
    request = YahooFinancials(stock_ticker)
    data = request.get_stock_price_data()[stock_ticker]
    currency_code = data['currency']

    currency_id = Currency.objects.filter(currency_code=currency_code)[0].id

    return currency_id

def generate_stock_table_array_dic(request, current_currency_id):
    user_id = request.user.id
    stocks = Stocks.objects.filter(user_id=user_id)
    stock_table_array_dic = []


    for stock in stocks:
        dic = {
            'stockid': 0,
            'currencyid': 0,
            'stockdatepurchased': 0,
            'stockticker': 0,
            'stockquantity': 0,
            'stockaverageprice': 0,
            'stockmarketprice': 0,
            'stockinvestedamount': 0,
            'stockmarketvalue': 0,
            'stockprofit': 0,
            'stockprofitpercentage': 0,
        }

        stock_currency_id = finance_api_get_currency_id(stock.stock_ticker)
        user_exchange_rate = finance_api_get_exchange_rate(stock.currency_id.id, current_currency_id)
        exchange_rate = finance_api_get_exchange_rate(stock_currency_id, current_currency_id)

        dic['stockid'] = stock.id
        dic['currencyid'] = stock.currency_id.id
        dic['stockdatepurchased'] = stock.date_purchased
        dic['stockticker'] = stock.stock_ticker
        dic['stockquantity'] = stock.quantity
        dic['stockaverageprice'] = stock.average_price * user_exchange_rate
        dic['stockmarketprice'] = finance_api_get_stock_price(dic['stockticker']) * exchange_rate
        dic['stockinvestedamount'] = dic['stockaverageprice'] * dic['stockquantity']
        dic['stockmarketvalue'] = dic['stockmarketprice'] * dic['stockquantity']
        dic['stockprofit'] = (dic['stockmarketvalue'] - dic['stockinvestedamount'])

        if dic['stockinvestedamount'] == 0:
            dic['stockprofitpercentage'] = 0
        else:
            dic['stockprofitpercentage'] = (dic['stockprofit'] / dic['stockinvestedamount']) * 100

        stock_table_array_dic.append(dic)

    return stock_table_array_dic


def generate_profit_table_1_dic(stock_table_array_dic, current_currency_id):

    profit_table_1_dic = {
        'currencyid': DEFAULT_CURRENCY_ID,
        'totalinvestedamount': 0,
        'totalmarketamount': 0,
        'grossprofit': 0,
        'grossprofitpercentage': 0
    }

    for stock in stock_table_array_dic:
        exchange_rate = finance_api_get_exchange_rate(current_currency_id, DEFAULT_CURRENCY_ID)

        profit_table_1_dic['totalinvestedamount'] += stock['stockinvestedamount'] * exchange_rate
        profit_table_1_dic['totalmarketamount'] += stock['stockmarketvalue'] * exchange_rate

    profit_table_1_dic['grossprofit'] = profit_table_1_dic['totalmarketamount'] - profit_table_1_dic['totalinvestedamount']

    if profit_table_1_dic['totalinvestedamount'] == 0:
        profit_table_1_dic['grossprofitpercentage'] = 0
    else:
        profit_table_1_dic['grossprofitpercentage'] = (profit_table_1_dic['grossprofit'] / profit_table_1_dic['totalinvestedamount']) * 100

    return profit_table_1_dic

def generate_profit_table_2_dic(profit_table_1_dic, request):
    user_id = request.user.id
    profit_adjustments = ProfitAdjustment.objects.filter(user_id=user_id)

    profit_table_2_dic = {
        'currencyid': DEFAULT_CURRENCY_ID,
        'profitfromsold': 0,
        'profitfromdividend': 0,
        'netprofit': 0,
        'netprofitpercentage': 0
    }

    for profit_adjustment in profit_adjustments:
        profit_table_2_dic['profitfromsold'] += profit_adjustment.profit_from_sold
        profit_table_2_dic['profitfromdividend'] += profit_adjustment.profit_from_dividends

    profit_table_2_dic['netprofit'] = profit_table_1_dic['grossprofit'] + profit_table_2_dic['profitfromsold'] + profit_table_2_dic['profitfromdividend']

    if profit_table_1_dic['totalinvestedamount'] == 0:
        profit_table_2_dic['netprofitpercentage'] = 0
    else:
        profit_table_2_dic['netprofitpercentage'] = (profit_table_2_dic['netprofit'] / profit_table_1_dic['totalinvestedamount']) * 100

    return profit_table_2_dic

def generate_currency_dic():
    currency_array_dic = []
    all_currency = Currency.objects.all()
    for currency in all_currency:
        dic = {
            'id': 0,
            'currencycode': 0,
            'currencyname': 0,
        }

        dic['id'] = currency.id
        dic['currencycode'] = currency.currency_code
        dic['currencyname'] = currency.currency_name
        currency_array_dic.append(dic)

    return currency_array_dic

def stock_table_array_dic_format(stock_table_array_dic):
    for stock in stock_table_array_dic:
        currency_code = Currency.objects.get(pk=stock['currencyid']).currency_code

        money_format = "${:.2f} {}"
        signed_money_format = "{}${:.2f} {}"
        percentage_format = "{}{:.2f}%"

        sign = "+"
        if stock['stockprofit'] < 0:
            sign = "-"

        stock['stockaverageprice'] = money_format.format(stock['stockaverageprice'], currency_code)
        stock['stockmarketprice'] = money_format.format(stock['stockmarketprice'], currency_code)
        stock['stockinvestedamount'] = money_format.format(stock['stockinvestedamount'], currency_code)
        stock['stockmarketvalue'] = money_format.format(stock['stockmarketvalue'], currency_code)

        stock['stockprofit'] = signed_money_format.format(sign, stock['stockprofit'], currency_code)


        stock['stockprofitpercentage'] = percentage_format.format(sign, stock['stockprofitpercentage'])

    return stock_table_array_dic

def profit_table_1_dic_format(profit_table_1_dic):
    currency_code = Currency.objects.get(pk=DEFAULT_CURRENCY_ID).currency_code

    money_format = "${:.2f} {}"
    signed_money_format = "{}${:.2f} {}"
    percentage_format = "{}{:.2f}%"

    sign = "+"
    if profit_table_1_dic['grossprofit'] < 0:
        sign = "-"

    profit_table_1_dic['totalinvestedamount'] = money_format.format(profit_table_1_dic['totalinvestedamount'], currency_code)
    profit_table_1_dic['totalmarketamount'] = money_format.format(profit_table_1_dic['totalmarketamount'], currency_code)
    profit_table_1_dic['grossprofit'] = signed_money_format.format(sign, profit_table_1_dic['grossprofit'], currency_code)
    profit_table_1_dic['grossprofitpercentage'] = percentage_format.format(sign, profit_table_1_dic['grossprofitpercentage'])

    return profit_table_1_dic

def profit_table_2_dic_format(profit_table_2_dic):
    currency_code = Currency.objects.get(pk=DEFAULT_CURRENCY_ID).currency_code

    money_format = "${:.2f} {}"
    signed_money_format = "{}${:.2f} {}"
    percentage_format = "{}{:.2f}%"

    sign = "+"
    if profit_table_2_dic['netprofit'] < 0:
        sign = "-"

    profit_table_2_dic['profitfromsold'] = money_format.format(profit_table_2_dic['profitfromsold'], currency_code)
    profit_table_2_dic['profitfromdividend'] = money_format.format(profit_table_2_dic['profitfromdividend'], currency_code)
    profit_table_2_dic['netprofit'] = signed_money_format.format(sign, profit_table_2_dic['netprofit'], currency_code)
    profit_table_2_dic['netprofitpercentage'] = percentage_format.format(sign, profit_table_2_dic['netprofitpercentage'])

    return profit_table_2_dic


def stockpage_context_handler(request):
    current_currency_id = 8
    stock_table_array_dic = generate_stock_table_array_dic(request, current_currency_id)
    profit_table_1_dic = generate_profit_table_1_dic(stock_table_array_dic, current_currency_id)
    profit_table_2_dic = generate_profit_table_2_dic(profit_table_1_dic, request)
    currency_array_dic = generate_currency_dic()

    stock_table_array_dic_formatted = stock_table_array_dic_format(stock_table_array_dic)
    profit_table_1_dic_formatted = profit_table_1_dic_format(profit_table_1_dic)
    profit_table_2_dic_formatted = profit_table_2_dic_format(profit_table_2_dic)

    context = {
        'stocktable': stock_table_array_dic_formatted,
        'profit_table_1_dic_formatted': profit_table_1_dic_formatted,
        'profit_table_2_dic_formatted': profit_table_2_dic_formatted,
        'currencytable': currency_array_dic
    }

    return context
