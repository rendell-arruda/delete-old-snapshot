import boto3
from datetime import datetime, timezone, timedelta

# Nome do perfil AWS configurado para se conectar à conta "sandbox"
profile_name = 'sandbox'

# Cria uma sessão boto3 utilizando o perfil especificado
session = boto3.Session(profile_name=profile_name)

# Variáveis
retention_days = 30
regions = ['us-east-1']

def lambda_handler(retention_days, region):
    # Calcula a data de retenção (data atual - dias de retenção)
    retention_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    print("Data de retenção:", retention_date)
    
    # Cria um cliente EC2 para a região especificada
    client = session.client('ec2', region_name=region)
    
    try:
        # Usa um paginator para lidar com grandes listas de snapshots
        paginator = client.get_paginator('describe_snapshots')
        for page in paginator.paginate(OwnerIds=['self']):
            snapshots = page['Snapshots']
            for snapshot in snapshots:
                snapshot_date = snapshot["StartTime"]
                if snapshot_date < retention_date:
                    snapshot_id = snapshot['SnapshotId']
                    try:
                        print(f"Deletando o snapshot {snapshot_id}...")
                        client.delete_snapshot(SnapshotId=snapshot_id)
                        print(f"Snapshot {snapshot_id} deletado com sucesso!")
                    except Exception as e:
                        print(f"Erro ao deletar o snapshot {snapshot_id}: {e}")
                else:
                    days_rest = snapshot_date - retention_date
                    print(f"Faltam {days_rest.days} dias para o snapshot {snapshot['SnapshotId']} ser deletado.")
    except Exception as e:
        print(f"Erro ao listar snapshots: {e}")

if __name__ == "__main__":
    for region in regions:
        lambda_handler(retention_days, region)
