# Over-Privileged Function

The Over-Privileged Function vulnerability in the DVSA application occurs because the Lambda execution role is granted more permissions than required. The function DVSA-SEND-RECEIPT-EMAIL is only supposed to send receipt emails, but it has access to additional AWS resources such as S3, DynamoDB, and SES. This is dangerous because if the function is compromised, an attacker can use these permissions to access or modify sensitive data.

---

## Vulnerability Exploiting

To achieve this vulnerability, you have to follow these steps:

1. Open the AWS Management Console  
2. Navigate to Lambda → Functions  
3. Search for DVSA-SEND-RECEIPT-EMAIL  
4. Open the function and go to Configuration → Permissions  
5. Click on the execution role to open it in IAM  
6. Review the attached policies and observe that they allow access to multiple services (S3, DynamoDB, SES)  

---

## Proof of Exploit

To prove the vulnerability, the IAM Policy Simulator and CloudTrail were used:

1. The execution role was tested using the IAM Policy Simulator  
2. The results showed that the role can access and modify data in multiple DynamoDB tables and S3 buckets  
3. A CloudTrail trail was created to monitor the function activity  
4. The generated policy showed that the function only uses a small subset of permissions  

To further demonstrate the impact:

1. The function was modified to print environment variables in CloudWatch Logs  
2. Temporary AWS credentials were exposed  
3. These credentials were used in a local terminal  
4. A command was executed to retrieve all records from the DynamoDB table  

This confirms that an attacker can perform unauthorized actions using the function’s credentials.

---

## Vulnerability Fixing

The fix was applied by reducing the permissions of the execution role to only what the function needs.

To apply the fix, follow these steps:

1. Open AWS Console  
2. Navigate to IAM → Roles  
3. Select the execution role of the function  
4. Remove unnecessary permissions such as:
   - Full S3 access  
   - Full DynamoDB access  
   - Full SES access  
5. Replace them with limited permissions:
   - Allow only sending emails (SES)  
   - Allow access only to required resources (specific S3 bucket and DynamoDB table)  

---

## Verification After Fix

To verify that the fix is working:

1. Use the same previously exposed credentials  
2. Attempt to access DynamoDB or other resources  

You should receive an error like:

AccessDeniedException

This confirms that unauthorized access is blocked, while the function still performs its normal task of sending receipt emails correctly.