from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from ..models import Currency, Stocks, ProfitAdjustment

import requests
import json

API_KEY = "QW5STDSFU45AUKEU"

def logout_user(request):
    logout(request)
    return True

def finance_api_get_stock(stock_ticker):
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=5min&datatype=json&apikey={}".format(stock_ticker, API_KEY)
    stock_api_data = requests.get(url).json()
    print(stock_api_data)
    pass

#True for valid, False for invalid
def stock_details_validator(user_id, currency_code, stock_ticker, average_price, quantity):
    if not User.objects.filter(pk=user_id).exists():
        return False

    if not Currency.objects.filter(currency_code=currency_code).exists():
        return False

    finance_api_get_stock(stock_ticker)
    pass

def add_stock_handler(request):
    post_request = request.POST
    user_id = request.user.id
    currency_code = post_request["stockpage-addcurrency-2"]
    stock_ticker = post_request["stockpage-addstockticker-2"]
    average_price = post_request["stockpage-addaverageprice-2"]
    quantity = post_request["stockpage-addquantity-2"]

    stock_details_validator(user_id, currency_code, stock_ticker, average_price, quantity)
