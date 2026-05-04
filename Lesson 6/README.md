# Denial of Service (DoS)

The Denial of Service (DoS) vulnerability in the DVSA application occurs because the billing endpoint does not have any rate limiting configured. This allows attackers to send a large number of requests at the same time, which overloads the backend services such as AWS Lambda and DynamoDB. As a result, legitimate users are unable to complete their payments.

---

## Vulnerability Exploiting

To achieve this vulnerability, you have to follow these steps:

1. Log in to the DVSA application using an attacker account  
2. Add an item to the cart and proceed to checkout  
3. Open Browser DevTools and go to the Network tab  
4. Capture the `order-id` and `Authorization token` from the order request  
5. Create a Python script that sends multiple concurrent requests (e.g., 200 requests)  
6. Run the script using PowerShell  

> While the script is running, try to complete a payment using another account

---

## Proof of Exploit

After running the attack:

1. The victim’s payment will fail  
2. The application will return an error like:

500 Internal Server Error

This happens because the backend services become overloaded and cannot handle the large number of requests.

---

## Vulnerability Fixing

The fix was applied in the API Gateway by enabling rate limiting to control the number of requests.

To apply the fix, follow these steps:

1. Open AWS Console  
2. Search for and open API Gateway  
3. Select the DVSA API (DVSA-APIS)  
4. Go to the Stage settings  
5. Enable throttling and set the Burst limit to 50  
6. Save the changes  

---

## Verification After Fix

To verify that the fix is working, run the same attack again:

1. Execute the script with 200 concurrent requests  
2. Observe the responses  

You should see a response like:

{"message": "Too Many Requests"}

This confirms that the API Gateway is blocking excessive requests and the backend is protected from overload.