import boto3

profile_name = 'sandbox'

session = boto3.Session(profile_name=profile_name)
client = session.client('ec2')



    
def lambda_handler( event, context):
    try:
        response = client.describe_snapshots(OwnerIds=['self'])
        return print(response)
    except Exception as e:
         return print(e)
lambda_handler(None, None)
