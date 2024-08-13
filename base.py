import boto3
from datetime import datetime, timezone, timedelta

# Configurações
retention_days = 30  # Quantidade de dias para reter os snapshots
region = 'us-east-1'  # Defina a região

# Inicializa o cliente EC2
ec2 = boto3.client('ec2', region_name=region)

def delete_old_snapshots(retention_days):
    # Calcula a data de corte para a retenção
    retention_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    
    # Obtém todos os snapshots criados pela sua conta
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    
    for snapshot in snapshots:
        # Verifica se o snapshot é mais antigo que a data de retenção
        snapshot_date = snapshot['StartTime']
        if snapshot_date < retention_date:
            snapshot_id = snapshot['SnapshotId']
            print(f'Deletando snapshot {snapshot_id} criado em {snapshot_date}')
            try:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f'Snapshot {snapshot_id} deletado com sucesso')
            except Exception as e:
                print(f'Erro ao deletar snapshot {snapshot_id}: {str(e)}')

if __name__ == "__main__":
    delete_old_snapshots(retention_days)
