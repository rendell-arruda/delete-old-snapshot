import boto3
from datetime import datetime, timezone, timedelta

profile_name = 'sandbox'

session = boto3.Session(profile_name=profile_name)

# variables
retention_days = 30
# regions = ['us-east-1', 'sa-east-1']
regions = ['us-east-1']
    
def lambda_handler(retention_days,region):
    # O propósito dessa linha é calcular a data limite (ou seja, retention_date) 
    # a partir da qual você deseja excluir snapshots.
    #                retorna a data atual       -  timedelta cria um intervalo de tempo de 30 dias 
    retention_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

    print("data de retenção")
    print(retention_date)
    
    client = session.client('ec2', region_name=region)
    try:
        # Lista de snapshots
        paginator = client.get_paginator('describe_snapshots')
        for page in paginator.paginate(OwnerIds=['self']):
            snapshots = page['Snapshots']
            for snapshot in snapshots:
                snapshot_date = snapshot["StartTime"]
                # se a data do snapshot for menor que a data de retenção, quer dizer que ele é mais antigo que a data de retenção
                if snapshot_date < retention_date:
                    snapshot_id = snapshot['SnapshotId']
                    try:
                        print(f"deletando o snapshot {snapshot_id} ")
                        client.delete_snapshot(SnapshotId=snapshot_id)
                        print(f"deletado com sucesso {snapshot_id} ")
                    except Exception as e:
                        print(f"Erro ao deletar o snapshot {snapshot_id}: {e}")
                else:
                    days_rest = snapshot_date - retention_date
                    print(f"Faltam {days_rest.days} dias para o snapshot ser deletado")
    except Exception as e:
        print(f"Erro ao listar snapshots: {e}")

if __name__ == "__main__":
    for region in regions:           
        lambda_handler(retention_days,region)