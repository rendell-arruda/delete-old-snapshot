import boto3
from datetime import datetime, timezone, timedelta

profile_name = 'sandbox'

session = boto3.Session(profile_name=profile_name)

# variables
retention_days = 30
# regions = ['us-east-1', 'sa-east-1']
regions = ['us-east-1']
    
def lambda_handler(retetion_days,region):
    # O propósito dessa linha é calcular a data limite (ou seja, retention_date) 
    # a partir da qual você deseja excluir snapshots.
    #                retorna a data atual       -  timedelta cria um intervalo de tempo de 30 dias 
    retention_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

    print("data de retenção")
    print(retention_date)
    
    client = session.client('ec2', region_name=region)
    try:
        # Lista de snapshots
        snapshots = client.describe_snapshots(OwnerIds=['self'])["Snapshots"]
        for snapshot in snapshots:
            print("========= separador =========")
            # print(f"O snaphot : {snapshot["Description"]}, foi criado em: {snapshot["StartTime"]}")
            snapshot_date = snapshot["StartTime"]
            # se a data do snapshot for menor que a data de retenção, quer dizer que ele é mais antigo que a data de retenção
            if snapshot_date < retention_date:
                snapshot_id = snapshot['SnapshotId']
                try:
                    print("deletando o snapshot {snapshot_id} ")
                    
                except Exception as e:
                    print("Erro ao deletar o snapshot {snapshot_id}: {e}")
                ...
            else:
                days_rest = snapshot_date - retention_date
                print(f"Faltam {days_rest.days } para o snapshot ser deletado")
         
           
    except Exception as e:
        return print(e)


if __name__ == "__main__":
    for region in regions:           
        lambda_handler(retention_days,region)