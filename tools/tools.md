# python tools/工具代码合集

使用方法：通常都是直接运行代码，然后根据提示输入参数，或者直接查看输出结果。

## HTTP工具

- [HTTP客户端](http_client.py)：Postman的命令行替代品，用于发送HTTP请求并美化显示响应。
  
  **功能特点：**
  - 支持所有HTTP方法（GET/POST/PUT/DELETE等）
  - 支持从JSON文件读取请求体
  - 自动格式化JSON响应（带语法高亮）
  - 美观显示状态码、响应头、响应时间
  - 支持请求头和查询参数配置
  - 可保存/加载请求配置
  - 彩色输出，易于阅读
  
  **使用示例：**
  ```bash
  # 简单GET请求
  python tools/http_client.py GET https://api.github.com/users/octocat
  
  # POST请求（JSON body）
  python tools/http_client.py POST https://api.example.com/login -d '{"username":"admin","password":"123"}'
  
  # 从文件读取body
  python tools/http_client.py POST https://api.example.com/users -f data/user.json
  
  # 添加请求头
  python tools/http_client.py GET https://api.example.com/api -H "Authorization:Bearer token123"
  
  # 添加查询参数
  python tools/http_client.py GET https://api.example.com/search -q "keyword:python" -q "page:1"
  
  # 保存请求配置（方便重复使用）
  python tools/http_client.py POST https://api.example.com/login -d '{"user":"admin"}' --save login.json
  
  # 从配置加载并执行
  python tools/http_client.py --load login.json
  
  # 显示详细信息（包括响应头）
  python tools/http_client.py GET https://httpbin.org/get -v
  ```
  
  **配置文件示例：** 参考 [http_client.example.json](http_client.example.json)
  
  配置文件格式说明：
  - `method`: HTTP方法（GET/POST/PUT/DELETE等）
  - `url`: 请求URL
  - `headers`: 请求头数组，格式为 "Key:Value"
  - `params`: 查询参数数组，格式为 "key:value"
  - `data`: 请求体JSON字符串（与body_file二选一）
  - `body_file`: 请求体文件路径（与data二选一）
  - `timeout`: 超时时间（秒）

- [HTTP压力测试工具](http_stress_test.py)：用于测试HTTP接口在高并发情况下的表现，特别适合排查502等间歇性错误。
  
  **功能特点：**
  - 支持多种HTTP方法（GET/POST/PUT/DELETE等）
  - 可配置请求头和请求体
  - 详细的统计信息（成功率、QPS、响应时间分布、状态码统计）
  - 支持真实用户模拟（请求延迟、连接复用）
  - 实时进度显示
  - 自动生成JSON格式详细测试报告
  - 完整的命令行参数支持
  
  **核心参数：**
  - `-u, --url`: 目标URL（必填）
  - `-n, --number`: 总请求数（默认1000）
  - `-c, --concurrent`: 并发数（默认50）
  - `-m, --method`: HTTP方法（GET/POST/PUT等）
  - `-t, --timeout`: 超时时间（默认30秒）
  - `-H, --header`: 自定义请求头（可多次使用）
  - `-d, --data`: 请求体数据
  - `--delay`: 请求间延迟（秒），模拟真实用户
  - `--no-keepalive`: 禁用HTTP连接复用
  
  **使用示例：**
  ```bash
  # 基本使用 - 测试GET请求
  python tools/http_stress_test.py -u https://api.example.com/users
  
  # 模拟真实用户访问（推荐）
  python tools/http_stress_test.py -u https://api.example.com/api -n 2000 -c 50 --delay 0.1
  
  # 高并发压力测试
  python tools/http_stress_test.py -u https://api.example.com/api -n 5000 -c 150 --delay 0.05
  
  # 测试POST请求
  python tools/http_stress_test.py -u https://api.example.com/login -m POST -d '{"username":"test","password":"123"}'
  
  # 带认证的请求
  python tools/http_stress_test.py -u https://api.example.com/api -H "Authorization: Bearer token123" -n 3000 -c 80
  
  # 禁用连接复用（更严格的测试）
  python tools/http_stress_test.py -u https://api.example.com/api -n 1000 -c 30 --no-keepalive
  ```
  
  **测试建议：**
  1. 测试前先提高系统文件描述符限制：`ulimit -n 10240`
  2. 从小并发开始逐步增加，找出服务器承受上限
  3. 使用 `--delay` 参数模拟真实用户，避免客户端连接错误
  4. 报告保存在 `data/stress_test_reports/` 目录

- [并发基准测试](concurrent_benchmark.py)：基础的异步HTTP并发测试工具。

## 音视频处理

- [音频提取](video_moviepy_extract_audio.py)：从视频中提取音频。

- [视频编辑](video_moviepy_edit_video.py)：视频剪辑、合并、添加音频等。

  - **add_watermark**：给视频添加水印

  - **crop_video**：裁剪视频到指定区域

  - **trim_video**：截取视频片段

  - **flip_video**：镜像翻转视频
