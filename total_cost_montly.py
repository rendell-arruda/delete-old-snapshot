import matplotlib.pyplot as plt

# Dados estimados
snapshot_size_gb = 100  # tamanho médio de um snapshot em GB
num_snapshots = 50  # número de snapshots antigos
cost_per_gb = 0.05  # custo por GB por mês na região us-east-1

# Cálculo da economia mensal
cost_per_snapshot = snapshot_size_gb * cost_per_gb
total_cost_monthly = cost_per_snapshot * num_snapshots

# Gerando gráfico de economia
snapshots_to_delete = list(range(1, num_snapshots + 1))
savings = [cost_per_snapshot * i for i in snapshots_to_delete]

plt.figure(figsize=(10, 6))
plt.plot(snapshots_to_delete, savings, marker='o', color='b', label='Economia')
plt.title('Economia Acumulada ao Deletar Snapshots Antigos')
plt.xlabel('Número de Snapshots Deletados')
plt.ylabel('Economia Mensal (USD)')
plt.grid(True)
plt.legend()
plt.xticks(snapshots_to_delete)

# Exibir gráfico
plt.tight_layout()
plt.show()

# Retornando o valor total de economia
total_cost_monthly
