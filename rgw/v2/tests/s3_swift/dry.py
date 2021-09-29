import os

import boto3
import botocore

#
access_key_t1 = "30VFOK06W2EVL6I5JX3P"
secret_key_t1 = "nebI5M7fygd5BAAEJVcnF9STs5XQBBTRYtoSNnhb"
access_key_t2 = "KVQ9XPRLB4LT3X9O4MY6"
secret_key_t2 = "5vPMvoJBEhKayM5qdmZpny2w6rYovSpuvruPpAdf"
hostname = "10.74.182.153"
port = "8080"
additional_config = None

"""
1. Create 2 users t1 and t2.
2. Add the caps for t1 : radosgw-admin caps add --uid="t1" --caps="roles=*"
3. Create a role testrole3 
4. Attach the policy to the role: 
# cat policy.json 
{"Version":"2012-10-17","Statement":{"Effect":"Allow","Action":["s3:*"],"Resource":"arn:aws:s3:::*"}}
5. Create a bucket "testbucket2" using t1's credentials add some objects to it. 
6. Using t2 assume role of t1 user
7. Export the credentials and try to access the head_object which doesn't exist in the bucket testbucket2
"""

# password = "32characterslongpassphraseneeded".encode('utf-8')
# encryption_key = hashlib.md5(password).hexdigest()
#
# def create_file(fname, size):
#
#     # give the size in mega bytes.
#
#     file_size = 1024 * 1024 * size
#
#     with open(fname, "wb") as f:
#         f.truncate(file_size)
#
#     fname_with_path = os.path.abspath(fname)
#
#     # md5 = get_md5(fname)
#
#     return fname_with_path


#
# fname = create_file("sample1", 10)
# print(fname)
#
#
#

iam_client = boto3.client("iam",
aws_access_key_id=access_key_t1,
aws_secret_access_key=secret_key_t1,
endpoint_url="http://%s:%s" % (hostname, port),
region_name=""
)

#
#policy_document = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":[\"arn:aws:iam:::user/t2\"]},\"Action\":[\"sts:AssumeRole\"]}]}"

policy_document = (
        '{"Version":"2012-10-17",'
        '"Statement":[{"Effect":"Allow","Principal":{"AWS":["arn:aws:iam:::user/%s"]},'
        '"Action":["sts:AssumeRole"]}]}' % 't2')




role_response = iam_client.create_role(
AssumeRolePolicyDocument=policy_document,
Path='/',
RoleName='testrole8',
)

#role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":{\"Effect\":\"Allow\",\"Action\":\"s3:*\",\"Resource\":\"arn:aws:s3:::*\"}}"
#
role_policy = (
    '{"Version":"2012-10-17",'
    '"Statement":{"Effect":"Allow",'
    '"Action":"s3:*",'
    '"Resource":"arn:aws:s3:::*"}}'
)
#
response = iam_client.put_role_policy(
RoleName='testrole8',
PolicyName='read-access-folder4',
PolicyDocument=role_policy
)

print("put role policy")

bucket_name = "testbucket2"



s3_conn_resource = boto3.resource(
    "s3",
    aws_access_key_id=access_key_t1,
    aws_secret_access_key=secret_key_t1,
    endpoint_url="http://%s:%s" % (hostname, port),
    use_ssl=False,
    config=additional_config,
)
#
s3_conn_client = boto3.client(
    "s3",
    aws_access_key_id=access_key_t1,
    aws_secret_access_key=secret_key_t1,
    endpoint_url="http://%s:%s" % (hostname, port),
    config=additional_config,
)


sts_client = boto3.client('sts',
aws_access_key_id=access_key_t2,
aws_secret_access_key=secret_key_t2,
endpoint_url="http://%s:%s" % (hostname, port),
region_name="",
)

print("connection to sts client ")
print(role_response)

response = sts_client.assume_role(
RoleArn=role_response['Role']['Arn'],
RoleSessionName='t2',
DurationSeconds=3600
)

print("assoume role operation")

s3client = boto3.client('s3',
aws_access_key_id = response["Credentials"]["AccessKeyId"],
aws_secret_access_key = response["Credentials"]["SecretAccessKey"],
aws_session_token = response["Credentials"]["SecretAccessKey"],
endpoint_url="http://%s:%s" % (hostname, port),
region_name="",)

print("connection to s3client")

unexisting_object = bucket_name + "_unexisting_object"
existing_object = "policy.json"

print("finding unknown object here")

response_r2 = s3client.head_object(Bucket=bucket_name, Key=existing_object)

try:
    response_r1 = s3client.head_object(Bucket=bucket_name, Key=unexisting_object)
except botocore.exceptions.ClientError as e:
    response_code = e.response['Error']['Code']
    if e.response['Error']['Code'] == "404":
        print("404 Unexisting Object Not Found")
    elif e.response['Error']['Code'] == "403":
        print("403 Forbidden")

#
#

# buck1 = s3_conn_resource.Bucket(bucket_name)
# buck1.create()
# print("bucket created")

# buck1.upload_file('sample', 'sample')

# with open('sample1', 'r') as data:
#    buck1.put_object(Body=data, Key='sample1')
# print 'obj uploaded'

# obj_acl = s3_conn_resource.ObjectAcl(bucket_name, "sample1")
# print("putting acl")
# response = obj_acl.put(ACL="private")
# print("response: %s\n" % response)
#
# print("grants")
# print(obj_acl.grants)
#
#
# print(obj_acl.load())
# print("---- grants")
#
# print(obj_acl.grants)
#
#
# print("performing get")
# sample = s3_conn_resource.Object(bucket_name, "sample1")
#
# print(sample.get())


#
#
# buck1.put_object(Body=open('sample'), Key='sample8',
#                  SSECustomerAlgorithm=None,
#                  SSECustomerKey=None
#                  )
#
# # print(s3_conn_client.put_object(Bucket='Buck2',Key='sample_obj',Body=open('sample'),SSECustomerAlgorithm='AES256',SSECustomerKey=encryption_key))
#
#
# # buck1.put_object(Key='myobject_aes2',Body=open('sample'),SSECustomerAlgorithm='AES256',  SSECustomerKey=encryption_key)
#
# # buck1.download_file('sample', 'sample_downloaded')
#
#
# for object in buck1.objects.all():
#     print object.key
#
# buck1.download_file('sample8','sample_download_enc1',ExtraArgs={'SSECustomerKey':encryption_key,'SSECustomerAlgorithm':'AES256'})
#
#
