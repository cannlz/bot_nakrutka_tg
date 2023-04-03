import requests
import json
import os


#my_secret = os.environ['request']

def checkList(action, targetsite):
    url = 'https://ozzz.ru/api/v2'
    myobj = {'api_token': '$2y$10$VmuQDKAjteHl8dutZPdN4eRMTMLbKysAIHmUHAsfF6u9qsQQAghpi', 'action': f'{action}'}
    x = requests.post(url, json = myobj)

    a_list = json.loads(x.text)
    penis = []
    #print(x.text)
    for dictionary in a_list:
        if dictionary['social_network'] == targetsite:
            a = dictionary['id'], dictionary['name'], dictionary['description'], dictionary['min'], dictionary['max'], dictionary['rate']
            penis.append(a)
            #print(penis)
    return(penis)       
    
    
def checkingOrderStatus(action, idOrder):
    url = 'https://ozzz.ru/api/v2'
    myobj = {'api_token': '$2y$10$VmuQDKAjteHl8dutZPdN4eRMTMLbKysAIHmUHAsfF6u9qsQQAghpi', 'action':f'{action}', 'order':f'{idOrder}'}
    post = requests.post(url, json = myobj)
    data = post.json()
    #print(data)
    responseOrder = data['status'], data['charge']
    #print(responseOrder)
    return(responseOrder)

def createOrder(action, serviceID, link, quantity):
    url = 'https://ozzz.ru/api/v2'
    myobj = {'api_token': '$2y$10$VmuQDKAjteHl8dutZPdN4eRMTMLbKysAIHmUHAsfF6u9qsQQAghpi', 'action':f'{action}', 'service':f'{serviceID}', 'link':f'{link}', 'quantity':f'{quantity}'}
    post = requests.post(url, json = myobj)
    data = post.json()
    check = data['order']
    return(check)


#checkPrice("balance")
#checkingOrderStatus("status", "21217327")
#createOrder("add", "266", "https://t.me/aveline2004/3a", "101")
#checkList("packages", "Telegram")