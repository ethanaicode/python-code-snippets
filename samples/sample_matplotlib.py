import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置中文字体
# plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # Windows
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# ================================= 基础折线图

# # 原始数据
# data = {
#     '季度': [
#         '2021Q1', '2021Q2', '2021Q3', '2021Q4',
#         '2022Q1', '2022Q2', '2022Q3', '2022Q4',
#         '2023Q1', '2023Q2', '2023Q3', '2023Q4',
#         '2024Q1', '2024Q2', '2024Q3', '2024Q4'
#     ],
#     'MAU': [223.3, 237.1, 267.2, 271.7, 293.6, 305.7, 332.6, 326.0,
#             315.2, 324.0, 341.3, 335.7, 336.5, 350.1, 354.2, 358.5],
#     'DAU': [60.1, 62.7, 72.1, 72.2, 79.4, 83.5, 90.3, 92.8,
#             93.7, 95.1, 102.8, 100.1, 100.9, 105.0, 106.3, 108.3]
# }

# # 创建 DataFrame 并计算 DAU/MAU 比率
# df = pd.DataFrame(data)
# df['DAU/MAU'] = df['DAU'] / df['MAU']

# # 绘图
# plt.figure(figsize=(12, 6))
# plt.plot(df['季度'], df['DAU/MAU'], marker='o', linestyle='-', color='teal')
# plt.title('哔哩哔哩 DAU/MAU 比率变化趋势（2021Q1 - 2024Q4）')
# plt.xlabel('')
# plt.ylabel('DAU/MAU 比率')
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# ================================= 基础折线图

# # 年份和投稿量数据
# years = [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
# uploads = [60284, 103745, 207470, 371126, 816395, 2346162, 5530617, 12769254, 27567200]

# # 将投稿量转为百万单位
# uploads_million = [x / 1_000_000 for x in uploads]

# # 绘图
# plt.figure(figsize=(10, 6))
# plt.plot(years, uploads_million, marker='o', linestyle='-', color='steelblue')

# # 标题和标签
# plt.title('B站历年投稿量（单位：百万）')
# plt.xlabel('年份')
# plt.ylabel('投稿量（M）')
# plt.xticks(years)  # 设置X轴刻度
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# ================================= 柱状图和折线图组合

# # 数据
# quarters = ['2020 Q3', '2021 Q3', '2022 Q3', '2023 Q3', '2024 Q3']
# usage_minutes = [81, 88, 96, 100, 106]

# x = np.arange(len(quarters))  # X轴刻度位置

# # 创建画布
# fig, ax1 = plt.subplots(figsize=(10, 6))

# # 绘制柱状图
# bars = ax1.bar(x, usage_minutes, width=0.4, color='skyblue', label='日均使用时长（分钟）')

# # 在柱子上标出具体数值
# for i, val in enumerate(usage_minutes):
#     ax1.text(x[i], val + 1, str(val), ha='center', va='bottom', fontsize=10)

# # 绘制折线图
# ax2 = ax1.twinx()
# ax2.plot(x, usage_minutes, marker='o', color='orange', linestyle='-', label='趋势线')
# ax2.set_ylim(ax1.get_ylim())  # 保持 Y 轴范围一致

# # 设置X轴
# ax1.set_xticks(x)
# ax1.set_xticklabels(quarters)
# ax1.set_title('B站用户日均使用时长（分钟）趋势图')
# ax1.set_ylabel('日均使用时长（分钟）')
# ax1.grid(True, axis='y')

# # 图例
# lines, labels = ax1.get_legend_handles_labels()
# lines2, labels2 = ax2.get_legend_handles_labels()
# ax1.legend(lines + lines2, labels + labels2, loc='upper left')

# plt.tight_layout()
# plt.show()

# ================================= 柱状图和折线图组合

# 数据
quarters = ['2023 Q3', '2023 Q4', '2024 Q1', '2024 Q2', '2024 Q3']
revenue = [2595, 2857, 2529, 2566, 2821]  # 单位：百万

x = np.arange(len(quarters))

# 创建图表
fig, ax1 = plt.subplots(figsize=(10, 6))

# 柱状图
bars = ax1.bar(x, revenue, width=0.4, color='cornflowerblue', label='增值服务收入（百万）')

# 添加数值标注
for i, val in enumerate(revenue):
    ax1.text(x[i], val + 30, str(val), ha='center', va='bottom', fontsize=10)

# 折线图（共享 x 轴）
ax2 = ax1.twinx()
ax2.plot(x, revenue, marker='o', color='orange', linestyle='-', label='趋势线')
ax2.set_ylim(ax1.get_ylim())  # 保持 Y 轴一致

# 设置坐标轴和标题
ax1.set_xticks(x)
ax1.set_xticklabels(quarters)
ax1.set_title('B站增值服务收入趋势图')
ax1.set_ylabel('收入（百万）')
ax1.grid(True, axis='y')

# 图例合并
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper left')

plt.tight_layout()
plt.show()

# ================================= 柱状图和折线图组合

# # 数据输入
# data = {
#     '季度': [
#         '2022 Q1', '2022 Q2', '2022 Q3', '2022 Q4',
#         '2023 Q1', '2023 Q2', '2023 Q3', '2023 Q4',
#         '2024 Q1', '2024 Q2', '2024 Q3'
#     ],
#     '广告收入': [2052, 2103, 2210, 2350, 1573, 1621, 1638, 1929, 1669, 2037, 2094]
# }

# df = pd.DataFrame(data)

# # 计算同比增长率
# df['同比增长'] = [None] * len(df)
# for i in range(4, len(df)):
#     last_year_val = df.loc[i - 4, '广告收入']
#     if last_year_val != 0:
#         df.loc[i, '同比增长'] = (df.loc[i, '广告收入'] - last_year_val) / last_year_val
#     else:
#         df.loc[i, '同比增长'] = None

# # 设置横坐标
# x = np.arange(len(df))

# # 创建图表
# fig, ax1 = plt.subplots(figsize=(12, 6))

# # 柱状图：广告收入
# ax1.bar(x, df['广告收入'], width=0.4, color='cornflowerblue', label='广告收入（百万）')
# ax1.set_ylabel('广告收入（百万）')
# ax1.set_xticks(x)
# ax1.set_xticklabels(df['季度'], rotation=45)
# ax1.set_title('哔哩哔哩广告收入及同比增长趋势图')
# ax1.grid(True, axis='y')

# # 添加数值标签
# for i, val in enumerate(df['广告收入']):
#     ax1.text(x[i], val + 30, str(val), ha='center', va='bottom', fontsize=9)

# # 折线图：同比增长（右轴）
# ax2 = ax1.twinx()
# yoy_percent = df['同比增长'] * 100  # 转为百分比
# ax2.plot(x, yoy_percent, marker='o', color='orange', label='同比增长（%）')
# ax2.set_ylabel('同比增长（%）')

# # 合并图例
# lines1, labels1 = ax1.get_legend_handles_labels()
# lines2, labels2 = ax2.get_legend_handles_labels()
# ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# plt.tight_layout()
# plt.show()

# ================================= 饼状图

# # 原始数据
# labels_raw = ['18-24', '25-30', '31-35', '36-40', '41-45', '46-50', '51以上']
# percentages_raw = [39.7, 23.8, 20.4, 9.6, 1.5, 2.9, 2.2]

# # 合并 36岁以上
# labels = ['18-24', '25-30', '31-35', '36岁以上']
# percentages = [
#     percentages_raw[0],
#     percentages_raw[1],
#     percentages_raw[2],
#     sum(percentages_raw[3:])
# ]

# # 自定义颜色（可根据需要微调）
# colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3']

# # 创建图形
# fig, ax = plt.subplots(figsize=(8, 6), dpi=100)

# # 绘制饼状图并美化（设置环形、阴影、样式等）
# wedges, texts, autotexts = ax.pie(
#     percentages,
#     labels=labels,
#     autopct='%1.1f%%',
#     startangle=140,
#     counterclock=False,
#     colors=colors,
#     wedgeprops=dict(width=0.4, edgecolor='white'),  # 环形 + 白色边
#     pctdistance=0.8,
#     textprops={'fontsize': 12}
# )

# # 添加中央空白文字
# ax.text(0, 0, '年龄\n分布', ha='center', va='center', fontsize=14, weight='bold')

# # 标题
# plt.title('哔哩哔哩用户年龄分布（截止2023年）', fontsize=14)

# # 保持圆形
# ax.axis('equal')

# # 显示图
# plt.tight_layout()
# plt.show()