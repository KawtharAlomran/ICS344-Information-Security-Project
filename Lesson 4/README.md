# Insecure Cloud Configuration Vulnerability
The Insecure Cloud Configuration vulnerability in the DVSA application occurs because the S3 bucket permissions are set to "public," allowing anyone to upload files or folders. This setup is dangerous because it gives attackers direct access to sensitive user data and website items. Beyond just stealing information, an attacker can upload malicious files that run on the server side, enabling them to manipulate the application's internal logic and change its behavior.


---
## Vulnerability Exploting
To achieve this vulnerability, you have to following these steps:
1.	Search for and open S3 in the AWS console.
2.	Copy the name of the bucket that you want to add your file to.
3.	Open the Terminal
4.	Write this command and replace what is in the square brackets with your bucket name.

```
curl.exe -X PUT -d "malicious" 'https://[dvsa-feedback-bucket-726695008551-us-east-1].s3.us-east-1.amazonaws.com/test.txt'
```

> After running this command nothing will appear in the terminal

To prove that you achieve the vulnerability open AWS consol and do these steps:

1.	Open CloudWatch and go to log management inside the log tab
2.	Search for and open the bucket name (it is /aws/lambda/DVSA-FEEDBACK-UPLOADS in my example).
Open the recent log, and you will see a message similar the one in the image below

---
Also, you can see the file from S3 by following these steps:

1.	Search and open S3
2.	Open the bucket that you uploaded the file to. 
You will see the file mane in the files list in Objects tap

---
## Vulnerability Fixing

The fix was applied in the S3 buckets by changing the permissions to block public access by following the steps:
1.	Search for and open S3
2.	Open the bucket that you upload files to.
3.	Go to the Permissions tab
4.	Click Edit in Block public access (bucket settings)
5.	Select Block all public access and save changes


To verify that the fix above is working, we have to run the command again and see the results in the termianl the CloudWatch logs. You should get Access Denied error message in the terminal and not seeing any new upload message. 
