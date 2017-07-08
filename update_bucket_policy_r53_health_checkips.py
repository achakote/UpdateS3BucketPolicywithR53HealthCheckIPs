# This lambda code updates the bucket policy in bucket
# In this example my bucket has access only to cloudfront Origin Access Identity 
# and this function will allow route 53 health check IPs to access it.

import boto3
import hashlib
import json
import urllib2


SERVICE = "ROUTE53_HEALTHCHECKS"
INGRESS_PORTS = { 'Http' : 80, 'Https': 443 }
OAI = "CloudFront Origin Access Identity XXXXXXXXX"
OAI_ARN = "".join(["arn:aws:iam::cloudfront:user/",OAI])
BUCKET = "BUCKET_NAME"
BUCKET_ARN = "".join(["arn:aws:s3:::",BUCKET,"/*"])



def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    message = json.loads(event['Records'][0]['Sns']['Message'])

    # Load the ip ranges from the url
    ip_ranges = json.loads(get_ip_groups_json(message['url'], message['md5']))

    # extract the service ranges
    hc_ranges = get_ranges_for_service(ip_ranges, SERVICE)
    s3_client = boto3.client('s3')

    bucket_policy = {
        "Version": "2012-10-17", 
        "Statement": [
            {
                "Sid": "RestrictAccessToCloudfront-ThisPolicyIsGeneratedByLambdaCode",
                "Effect": "Allow",
                "Principal": {
                    "AWS": OAI_ARN
                },
                "Action": "s3:GetObject",
                "Resource": BUCKET_ARN
            },
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": BUCKET_ARN,
                "Condition": {
                    "IpAddress": {
                        "aws:SourceIp": hc_ranges
                    }
                }
            }
        ]
    }

    bucket_policy = json.dumps(bucket_policy)
    s3_client.put_bucket_policy(Bucket=BUCKET, Policy=bucket_policy)

def get_ip_groups_json(url, expected_hash):
    print("Updating from " + url)

    response = urllib2.urlopen(url)
    ip_json = response.read()

    m = hashlib.md5()
    m.update(ip_json)
    hash = m.hexdigest()

    if hash != expected_hash:
        raise Exception('MD5 Mismatch: got ' + hash + ' expected ' + expected_hash)

    return ip_json

def get_ranges_for_service(ranges, service):
    service_ranges = list()
    for prefix in ranges['prefixes']:
        if prefix['service'] == service:
            print('Found ' + service + ' range: ' + prefix['ip_prefix'])
            service_ranges.append(prefix['ip_prefix'])

    return service_ranges


