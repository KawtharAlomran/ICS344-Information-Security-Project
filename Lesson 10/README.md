# Unhandled Exceptions Vulnerability 
The Unhandled Exceptions vulnerability in the DVSA application happens because the backend Lambda function does not properly handle malformed or incomplete requests. When required fields such as `orderId` are missing, the application crashes and returns internal error details instead of a safe message.

This leads to information disclosure, where sensitive data such as stack traces, file paths, and code fragments are exposed to the user, increasing the risk of further attacks.

## Vulnerability Exploting
To achieve this vulnerability, we will use the Terminal, Browser Developer Tools, and the AWS console. The DVSA application is deployed on AWS, and the vulnerability exists in the `/order` API endpoint handled by a Lambda function.

You have to follow these steps:

1. Open the DVSA website and log in using a valid user account.
2. Open the Browser Developer Tools.
3. Go to the Network tab and capture the authorization token.
4. Open the AWS console.
5. Search for API Gateway and open it.
6. Open the DVSA API and copy the Invoke URL.
7. Open the Terminal and write this command:
curl -i -X POST "API_URL/order" \
-H "Content-Type: application/json" \
-H "authorization: TOKEN" \
--data-raw '{"action":"get"}'

Replace `API_URL` with the actual API endpoint and `TOKEN` with the captured authorization token. The request intentionally does not include the required `orderId` field.

8. After running the command, observe the response in the terminal.

The application returns an error message containing internal details such as:
- Error type (e.g., Syntax error)
- File path (e.g., `/var/task/get_order.py`)
- Line number of the error

This confirms that the application exposes sensitive backend information instead of handling the error safely.

## Vulnerability Fixing
The fix of this vulnerability is done in the `DVSA-ORDER-GET` Lambda function by doing the following:

1. Open the AWS console.
2. Search for and open Lambda.
3. Open the `DVSA-ORDER-GET` function from the functions list.
4. Open the `get_order.py` file in the code tab.
5. Find this vulnerable line:

```python
orderId = event["orderId"]
```

6. Replace it with the following safer code:

 ```python
orderId = event.get("orderId")
if not orderId:
    return {
        "statusCode": 400,
        "body": json.dumps({"msg": "Invalid request"})
    }
```

7. Deploy the changes by clicking on the Deploy button.

This fix ensures that missing or invalid input is handled safely without exposing internal error details to the client.

To verify that the fix is working, run the same curl command again:
curl -i -X POST "API_URL/order" \
-H "Content-Type: application/json" \
-H "authorization: TOKEN" \
--data-raw '{"action":"get"}'

After applying the fix, the application will return a safe response:
{"msg":"Invalid request"}
The response will no longer include stack traces, file paths, or internal code details.