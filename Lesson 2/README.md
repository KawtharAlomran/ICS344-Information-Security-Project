# Broken Authentication 
The Broken Authentication vulnerability in the DVSA application happens because the backend does not properly verify JSON Web Tokens (JWT). Instead of validating the token’s signature, the system directly trusts the information inside the token payload, such as "username" and "sub".

As a result, an attacker can modify the JWT payload, re-encode it, and impersonate another user. This allows unauthorized access to sensitive data such as order information.

## Vulnerability Exploting
## Vulnerability Fixing