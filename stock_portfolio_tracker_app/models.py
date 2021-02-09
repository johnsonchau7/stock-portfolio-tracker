from django.db import models
from django.contrib.auth.models import User

class Currency(models.Model):
    currency_code = models.CharField(max_length=50)
    currency_name = models.CharField(max_length=200)
    currency_symbol = models.CharField(max_length=50)

class Stocks(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    currency_id = models.ForeignKey(Currency, on_delete=models.CASCADE)
    stock_ticker = models.CharField(max_length=50)
    average_price = models.FloatField()
    quantity = models.IntegerField()
    date_purchased = models.CharField(max_length=50)

class ProfitAdjustment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    currency_id = models.ForeignKey(Currency, on_delete=models.CASCADE)
    profit_from_sold = models.FloatField()
    profit_from_dividends = models.FloatField()
