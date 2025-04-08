import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
# plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # Windows
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 数据
quarters = [
    '2021Q1', '2021Q2', '2021Q3', '2021Q4',
    '2022Q1', '2022Q2', '2022Q3', '2022Q4',
    '2023Q1', '2023Q2', '2023Q3', '2023Q4',
    '2024Q1', '2024Q2', '2024Q3', '2024Q4'
]
mau = [223.3, 237.1, 267.2, 271.7, 293.6, 305.7, 332.6, 326.0,
       315.2, 324.0, 341.3, 335.7, 336.5, 350.1, 354.2, 358.5]
dau = [60.1, 62.7, 72.1, 72.2, 79.4, 83.5, 90.3, 92.8,
       93.7, 95.1, 102.8, 100.1, 100.9, 105.0, 106.3, 108.3]

x = np.arange(len(quarters))  # X轴坐标

width = 0.35  # 柱状图宽度

fig, ax = plt.subplots(figsize=(14, 6))
bars1 = ax.bar(x - width/2, mau, width, label='MAU（月活）')
bars2 = ax.bar(x + width/2, dau, width, label='DAU（日活）')

# 标题和标签
ax.set_title('哔哩哔哩月活和日活用户数（2021Q1 - 2024Q4）')
ax.set_xlabel('')
ax.set_ylabel('用户数（百万）')
ax.set_xticks(x)
ax.set_xticklabels(quarters, rotation=45)
ax.legend()

plt.tight_layout()
plt.show()
