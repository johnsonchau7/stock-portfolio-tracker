import requests

request = requests.get("https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=demo")
print(request.json()[0])
# data = requests.data.json()
# print(data)
