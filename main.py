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
        # abre a paginação para listar todos os snapshots por bloco de 1000
        paginator = client.get_paginator('describe_snapshots')
        # para cada bloco de 1000 snapshots da mesma propriedade, ele vai listar o dicionario de snapshots
        for page in paginator.paginate(OwnerIds=['self']):
            # dentro do dicionario de snapshots, ele vai listar os snapshots 
            snapshots = page['Snapshots']
            # para cada snapshot dentro do dicionario
            for snapshot in snapshots:
                # pega a data de criação do snashot
                snapshot_date = snapshot["StartTime"]
                print(snapshot_date)

                # se a data do snapshot for menor que a data de retenção, quer dizer que ele é mais antigo que a data de retenção
                #  exemplo: se a data de retenção for 30 dias, ele vai deletar todos os snapshots mais antigos que 30 dias
                #  data de retenção/retention_date: 2024-07-16 , data de criação do snapshot: 2024-08-11
                # do dia 16/07 ao dia 11/08 faltam 26 dias para o snapshot ser eleito a deleção;
                if snapshot_date < retention_date:
                    #  pega o id do snapshot
                    snapshot_id = snapshot['SnapshotId']
                    try:
                        print(f"deletando o snapshot {snapshot_id} ")
                        # tenta deletar o snapshot    
                        client.delete_snapshot(SnapshotId=snapshot_id)
                        print(f"deletado com sucesso {snapshot_id} ")
                    except Exception as e:
                        print(f"Erro ao deletar o snapshot {snapshot_id}: {e}")
                else:
                    # ESSA PARTE DO CODIGO É OPCIONAL E APENAS EXIBE QUANTOS DIAS FALTAM PARA O SNAPSHOT SER DELETADO;
                    days_rest = snapshot_date - retention_date
                    print(f"Faltam {days_rest.days} dias para o snapshot ser deletado")
                    # OPCIONAL
    except Exception as e:
        print(f"Erro ao listar snapshots: {e}")
# Caso você queira executar o script localmente, utilize a parte do codigo abaixo
if __name__ == "__main__":
    # faz  um loop para cada região. Preciso verificar se preciso desse loop.
    for region in regions:           
        lambda_handler(retention_days,region)