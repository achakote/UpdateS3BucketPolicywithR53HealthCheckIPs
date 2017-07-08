# Update S3 Bucket Policy with Route 53 Health Check IPs

## About: 

If you have a critical bucket which is not public and you want to get alerts using route 53 health checks. This lambda function will help you auto update bucket policy with Route 53 health check IPs using lambda, so bucket can be montiored using Route 53 health check.

### Steps:

1. Create the lambda function using update_bucket_policy_r53_health_checkips.py
1. Create a new SNS trigger for the Lambda Function using CLI commands below.

            aws sns subscribe --topic-arn "arn:aws:sns:us-east-1:806199016981:AmazonIpSpaceChanged" --protocol lambda --notification-endpoint "YourLambdaARN" --region "us-east-1"

            aws lambda add-permission --function-name "YourLambdaARN" --statement-id "HealthCheckSG_Lam" --action "lambda:InvokeFunction" --principal "sns.amazonaws.com" --source-arn "arn:aws:sns:us-east-1:806199016981:AmazonIpSpaceChanged"
