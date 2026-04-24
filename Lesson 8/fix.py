import json
import urllib3
import boto3
import os
import time
import decimal
from decimal import Decimal

def lambda_handler(event, context):
    print(json.dumps(event))
    
    class DecimalEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, decimal.Decimal):
                if o % 1 > 0:
                    return float(o)
                else:
                    return int(o)
            return super(DecimalEncoder, self).default(o)

    orderId = event["orderId"]
    userId = event["user"]
    http = urllib3.PoolManager()
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["ORDERS_TABLE"])
    response = table.get_item(
        Key={"orderId": orderId, "userId": userId},
        AttributesToGet=['orderId', 'orderStatus', 'itemList']
    )
    if 'Item' not in response:
        return {"status": "err", "msg": "could not find order"}

    status = int(json.dumps(response["Item"]['orderStatus'], cls=DecimalEncoder))
    if status < 120:
        table.update_item(
            Key={"orderId": orderId, "userId": userId},
            UpdateExpression='SET orderStatus = :s',
            ExpressionAttributeValues={':s': Decimal(115)}
        )
        data_dict = []
        for key, value in response["Item"]['itemList'].items():
            data_dict.append({"itemId": key, "quantity": int(value)})
        data = json.dumps(data_dict, cls=DecimalEncoder)
        
        url = os.environ["GET_CART_TOTAL"]
        clen = len(data)
        req = http.request("POST", url, body=data, headers={'Content-Type': 'application/json', 'Content-Length': clen})
        res = json.loads(req.data)
        cartTotal = float(res['total'])
        missings = res.get("missing", {})
            
        url = os.environ["PAYMENT_PROCESS_URL"]
        data = json.dumps(event["billing"])
        clen = len(data)
        req = http.request("POST", url, body=data, headers={'Content-Type': 'application/json', 'Content-Length': clen})
        res = json.loads(req.data)
        ts = int(time.time())
        if res['status'] == 110:
            res = {"status": "err", "msg": "invalid payment details"}
        elif res['status'] == 120:
            table = dynamodb.Table(os.environ["ORDERS_TABLE"])
            key = {"orderId": orderId, "userId": userId}
            update_expression = 'SET orderStatus = :orderstatus, paymentTS = :paymentTS, totalAmount = :total, confirmationToken = :token'
            TWOPLACES = Decimal(10) ** -2
            expression_attributes = {
                ':orderstatus': res['status'],
                ':paymentTS': ts,
                ':total': Decimal(cartTotal).quantize(TWOPLACES),
                ':token': res['confirmation_token']
            }
            if missings:
                new_item_list = {}
                response = table.get_item(Key=key)
                items = response.get("Item", {}).get("itemList", {})
                for item in items:
                    new_item_list[item] = items[item] - missings[item] if missings.get(item) else items[item]
                expression_attributes[":il"] = new_item_list
                update_expression += ', itemList = :il'
            try:
                response = table.update_item(
                    Key=key,
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_attributes
                )
                sqs = boto3.client('sqs')
                sqs.send_message(
                    QueueUrl=os.environ["SQS_URL"],
                    MessageBody=json.dumps({"orderId": orderId, "userId": userId}),
                    DelaySeconds=10
                )
                res = {"status": "ok", "amount": float(cartTotal), "token": res['confirmation_token'], "missing": missings}
            except:
                res = {"status": "err", "msg": "unknown error"}
        else:
            res = {"status": "err", "msg": "could not process payment"}
    else:
        res = {"status": "err", "msg": "order already made"}

    return res