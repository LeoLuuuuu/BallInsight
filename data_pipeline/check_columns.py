import pandas as pd

# 读取 CSV 的前几行
df = pd.read_csv("data_pipeline/male_fc_24_players.csv", low_memory=False, nrows=5)
# 打印所有列名
print("CSV 文件中的所有列名为：")
print(df.columns.tolist())