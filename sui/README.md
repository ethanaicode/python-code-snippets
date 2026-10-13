# 随手记报表查询

通过 `https://www.sui.com/report.rmi` 查询报表，使用 Cookie 登录态。

## 文件

- `sui_report.py`：查询脚本
- `cookies.txt`：Cookie 字符串（单行），过期后直接整体替换；包含登录信息，不要提交到 git
- `month_202607.json`：查询示例输出

## 准备

```bash
pip install requests
```

Cookie 获取：浏览器登录 sui.com，打开报表页，在开发者工具 Network 中找到 `report.rmi` 请求，复制请求头 `cookie` 的值，覆盖写入 `cookies.txt`。

## 使用

```bash
python sui/sui_report.py <开始日期> <结束日期> [-m 报表类型] [-o 输出文件]
```

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `begin_date` | 开始日期，格式 `YYYY.MM.DD` | 必填 |
| `end_date` | 结束日期，格式 `YYYY.MM.DD` | 必填 |
| `-m, --mode` | 报表类型，对应表单字段 `m` | `daily` |
| `-o, --output` | 保存为 JSON 文件，不填则打印到终端 | - |

## 案例

查询 2026 年 7 月并保存：

```bash
python sui/sui_report.py 2026.07.01 2026.07.31 -o sui/output/month_202607.json
```

直接打印到终端：

```bash
python sui/sui_report.py 2026.07.01 2026.07.31
```

在代码中调用：

```python
from sui_report import query_report

data = query_report("2026.07.01", "2026.07.31")
print(data["inAmount"], data["outAmount"])
```

## 返回结构（节选）

- `inAmount` / `outAmount`：总收入 / 总支出
- `inlst` / `outlst`：按分类汇总，每项含 `name`、`id`、`total` 及子分类 `c`

## 常见问题

- 提示响应不是 JSON：Cookie 已过期，更新 `cookies.txt`
- 500 错误：检查参数是否正确（如 `-m` 后不要带多余字符）
- `No module named 'requests'`：确认使用虚拟环境的 Python，如 `.venv/bin/python`
