# 随手记 (sui.com) 接口脚本

通过 Cookie 登录态调用 sui.com 的网页接口。每个接口一个独立脚本，公共逻辑集中在 `sui_client.py`。

## 文件

| 文件 | 作用 |
| --- | --- |
| `sui_client.py` | 公共组件：请求头、Cookie 读取、`post()` 封装、`parse_loose_json()` |
| `sui_report.py` | 查询报表 `/report.rmi` |
| `sui_add.py` | 新建支出 `/tally/payout.rmi` |
| `sui_del.py` | 删除记录 `/tally/new.rmi`（`opt=del`） |
| `cookies.txt` | Cookie 单行字符串，过期后整体替换；含登录信息，不要提交到 git |
| `cookies.txt.example` | Cookie 文件示例 |
| `output/` | 查询结果输出目录 |

## 准备

```bash
pip install requests
```

Cookie 获取：浏览器登录 sui.com，在开发者工具 Network 中任选一个 `.rmi` 请求，复制请求头 `cookie` 的值，覆盖写入 `cookies.txt`。

脚本之间通过 `from sui_client import ...` 引用，直接 `python sui/xxx.py` 运行即可。

## 使用

### 查询报表

```bash
python sui/sui_report.py <开始日期> <结束日期> [-m 报表类型] [-o 输出文件]
python sui/sui_report.py 2026.07.01 2026.07.31 -o sui/output/month_202607.json
```

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `begin_date` / `end_date` | 日期，格式 `YYYY.MM.DD` | 必填 |
| `-m, --mode` | 报表类型，对应表单字段 `m` | `daily` |
| `-o, --output` | 保存为 JSON 文件，不填则打印 | - |

返回（节选）：`inAmount` / `outAmount` 为总收入 / 总支出，`inlst` 为按分类汇总。

### 新建支出

```bash
python sui/sui_add.py 12.50 -c 核对金额 -m "午餐" [-t "2026-10-13 18:37"] [--dry-run]
```

- 分类、商家、项目、成员、账户在 `sui_add.py` 顶部的 `CATEGORY` / `STORE` / `PROJECT` / `MEMBER` / `ACCOUNT` 中维护 `名称 -> id` 映射；传入的值不在映射中但是纯数字时，直接当作 id 使用
- `--dry-run` 只打印表单，不发请求
- 成功时返回新记录 id，如 `{id:{id:21693789142455},budget:0,price:12.50}`

### 删除记录

```bash
python sui/sui_del.py <记录id> [<记录id> ...]
```

记录 id 来自新建时返回的 id，或报表明细中的 `tranId`。

## 在代码中调用

```python
from sui_report import query_report
from sui_add import add_payout
from sui_del import delete_trans
```

## 新增接口

1. 在浏览器 Network 中复制目标请求，确认路径、表单字段、`referer` 和响应格式
2. 新建 `sui_<动作>.py`，复用公共组件：

```python
from sui_client import BASE_URL, parse_loose_json, post

resp = post("/xxx/yyy.rmi", {"opt": "..."}, referer=f"{BASE_URL}/xxx/page.do")
result = parse_loose_json(resp.text)  # 响应是标准 JSON 时用 resp.json()
```

3. 按响应判断成功与否，失败抛异常，命令行入口以退出码 1 结束
4. 在本文档的文件表和使用章节补充说明

约定：

- 请求头、Cookie 只在 `sui_client.py` 维护，不要在单个脚本里重复
- 脚本需同时支持命令行和函数调用
- 写操作（新增 / 删除 / 修改）尽量提供 `--dry-run` 或明确的成功校验

## 响应格式说明

- 报表接口返回标准 JSON，使用 `resp.json()`
- 写操作接口返回 `text/html`，内容是键未加引号的类 JSON，如 `{id: [{value: 123}]}`，用 `parse_loose_json()` 解析；该函数不适用于值中含字符串的响应

## 常见问题

- 响应无法解析 / 不是 JSON：Cookie 已过期，更新 `cookies.txt`
- 500 错误：检查参数是否正确（如 `-m` 后不要带多余字符）
- `No module named 'requests'`：确认使用虚拟环境的 Python，如 `.venv/bin/python`
