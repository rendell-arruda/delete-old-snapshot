import boto3  # type: ignore # Importa a biblioteca boto3, que permite a interação com serviços da AWS.
import logging  # Importa o módulo logging para registrar eventos e erros no seu código.
from datetime import datetime, timezone, timedelta  # Importa classes para manipular datas e horários.

from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
# Importa exceções específicas do boto3 para tratamento de erros.

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
# Configura o logging para registrar mensagens com nível INFO ou superior, usando um formato específico para as mensagens.

# Nome do perfil da AWS configurado
profile_name = 'sandbox'

# Cria uma sessão boto3 utilizando o perfil especificado
session = boto3.Session(profile_name=profile_name)
# Cria uma nova sessão boto3 usando o perfil da AWS configurado com o nome 'sandbox'.

# Variáveis
retention_days = 1  # Define o número de dias para a retenção de snapshots (snapshots mais antigos serão deletados).
regions = ['us-east-1']  # Lista de regiões AWS onde os snapshots serão gerenciados.

def delete_snapshot_with_retry(client, snapshot_id, max_retries=2):
    """Função para tentar deletar o snapshot várias vezes em caso de erro."""
    for attempt in range(max_retries):
        try:
            client.delete_snapshot(SnapshotId=snapshot_id)
            # Tenta deletar o snapshot com o ID fornecido.
            logger.info(f"Snapshot {snapshot_id} deletado com sucesso!")
            # Registra uma mensagem de sucesso se o snapshot for deletado.
            return True  # Retorna True indicando que a operação foi bem-sucedida.
        except ClientError as e:
            logger.error(f"Tentativa {attempt + 1} falhou ao deletar snapshot {snapshot_id}: {e}")
            # Registra uma mensagem de erro para cada tentativa falha.
            if attempt + 1 == max_retries:
                logger.critical(f"Falha ao deletar snapshot {snapshot_id} após {max_retries} tentativas")
                # Se todas as tentativas falharem, registra uma mensagem crítica.
                return False  # Retorna False indicando que a operação falhou.
        except Exception as e:
            logger.critical(f"Erro inesperado ao deletar snapshot {snapshot_id}: {e}")
            # Registra uma mensagem crítica para qualquer outro erro inesperado.
            return False  # Retorna False indicando que a operação falhou.

def lambda_handler(retention_days, region):
    # Calcula a data de retenção (data limite para exclusão de snapshots).
    retention_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    logger.info(f"Data de retenção: {retention_date}")
    # Registra a data de retenção calculada.

    client = session.client('ec2', region_name=region)
    # Cria um cliente EC2 para a região especificada.

    try:
        # Obtém um paginador para listar todos os snapshots do proprietário ('self') em páginas de resultados.
        paginator = client.get_paginator('describe_snapshots')
        for page in paginator.paginate(OwnerIds=['self']):
            # Para cada página de resultados...
            snapshots = page['Snapshots']
            # Obtém a lista de snapshots da página atual.

            for snapshot in snapshots:
                # Itera sobre cada snapshot na lista.
                snapshot_date = snapshot["StartTime"]
                # Obtém a data de criação do snapshot.

                if snapshot_date < retention_date:
                    # Se o snapshot for mais antigo que a data de retenção...
                    snapshot_id = snapshot['SnapshotId']
                    # Obtém o ID do snapshot.
                    if not delete_snapshot_with_retry(client, snapshot_id):
                        logger.error(f"Snapshot {snapshot_id} não pôde ser deletado.")
                        # Se a função de deleção falhar, registra um erro.
                else:
                    days_rest = snapshot_date - retention_date
                    logger.info(f"Faltam {days_rest.days} dias para o snapshot {snapshot['SnapshotId']} ser deletado.")
                    # Se o snapshot não for deletado, registra quantos dias faltam para ele ser elegível à exclusão.
    except NoCredentialsError as e:
        logger.critical(f"Erro de credenciais: {e}")
        # Registra uma mensagem crítica se houver problemas de credenciais.
    except EndpointConnectionError as e:
        logger.critical(f"Erro de conexão com o endpoint da AWS: {e}")
        # Registra uma mensagem crítica se houver problemas de conexão com a AWS.
    except ClientError as e:
        logger.error(f"Erro ao listar snapshots: {e}")
        # Registra um erro se ocorrer um problema ao listar os snapshots.
    except Exception as e:
        logger.critical(f"Erro inesperado: {e}")
        # Registra uma mensagem crítica para qualquer outro erro inesperado.

# Caso você queira executar o script localmente, utilize a parte do código abaixo
if __name__ == "__main__":
    # Itera sobre cada região na lista de regiões configuradas.
    for region in regions:           
        lambda_handler(retention_days, region)
        # Chama a função principal para cada região.
