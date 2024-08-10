import boto3
from datetime import datetime, timezone, timedelta

profile_name = 'sandbox'

session = boto3.Session(profile_name=profile_name)

# variables
retention_days = 30
# regions = ['us-east-1', 'sa-east-1']
regions = ['us-east-1']
    
def lambda_handler(retetion_days,region):
    retention_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

    print(retention_date)
    
    client = session.client('ec2', region_name=region)
    try:
        # Lista de snapshots
        snapshots = client.describe_snapshots(OwnerIds=['self'])["Snapshots"]
        for snapshot in snapshots:            
            snapshot_date = snapshot['StartTime']
            print(snapshot_date)    
    except Exception as e:
        return print(e)


if __name__ == "__main__":
    for region in regions:           
        lambda_handler(retention_days,region)