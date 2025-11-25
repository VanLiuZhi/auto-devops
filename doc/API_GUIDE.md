# API 使用指南

## 📡 接口概览

Auto DevOps 提供完整的 RESTful API，支持同步和流式两种诊断模式。新架构保持了与原有API的完全兼容性。

## 🌐 服务地址

- **本地开发**: http://localhost:8002
- **API文档**: http://localhost:8002/docs
- **健康检查**: http://localhost:8002/api/health

## 🔧 启动服务

```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动服务
python main.py

# 服务将在以下地址可用：
# - 前端页面: http://localhost:8002/
# - API文档: http://localhost:8002/docs
```

## 📋 API 接口

### 1. 健康检查

**接口**: `GET /api/health`

**描述**: 检查服务运行状态

**请求示例**:
```bash
curl -X GET http://localhost:8002/api/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "service": "故障诊断AI"
}
```

---

### 2. 同步诊断

**接口**: `POST /api/chat`

**描述**: 同步执行故障诊断，返回完整结果

**请求参数**:
```json
{
  "message": "用户输入的问题",
  "user_id": "用户ID（可选）"
}
```

**请求示例**:
```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "发布任务失败，请分析原因"}'
```

**响应示例**:
```json
{
  "response": "问题阶段：K8s部署Pod\n原因分析：Pod健康检查失败，端口8080无法访问\n解决方案：请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。",
  "status": "success"
}
```

**Python 示例**:
```python
import requests

url = "http://localhost:8002/api/chat"
payload = {
    "message": "发布任务失败，请分析原因"
}

response = requests.post(url, json=payload)
result = response.json()

print(result["response"])
```

---

### 3. 流式诊断

**接口**: `POST /api/chat/stream`

**描述**: 流式执行故障诊断，实时返回执行过程

**请求参数**: 与同步接口相同

**请求示例**:
```bash
curl -X POST http://localhost:8002/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "发布任务失败，请分析原因"}' --no-buffer
```

**响应格式**: Server-Sent Events (SSE)

**响应示例**:
```
data: {"type": "start", "message": "开始故障分析..."}

data: {"type": "tool_call", "tool": "get_build_log", "input": {}}

data: {"type": "tool_result", "tool": "get_build_log", "result": "[编译阶段日志] Maven 编译成功，没有错误。"}

data: {"type": "tool_call", "tool": "get_k8s_log", "input": {}}

data: {"type": "tool_result", "tool": "get_k8s_log", "result": "[部署阶段日志] Helm 部署成功，但 Pod 健康检查失败，端口8080无法访问。"}

data: {"type": "final", "content": "问题阶段：K8s部署Pod\n原因分析：Pod健康检查失败，端口8080无法访问\n解决方案：请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。", "status": "completed"}
```

**Python 示例**:
```python
import requests
import json

url = "http://localhost:8002/api/chat/stream"
payload = {
    "message": "发布任务失败，请分析原因"
}

response = requests.post(url, json=payload, stream=True)

for line in response.iter_lines():
    if line:
        if line.startswith('data: '):
            data = json.loads(line[6:])
            print(f"类型: {data['type']}")
            if data['type'] == 'tool_call':
                print(f"  调用工具: {data['tool']}")
            elif data['type'] == 'tool_result':
                print(f"  工具结果: {data['result'][:50]}...")
            elif data['type'] == 'final':
                print(f"  最终结果: {data['content'][:100]}...")
```

**JavaScript 示例**:
```javascript
const url = 'http://localhost:8002/api/chat/stream';
const payload = {
    message: '发布任务失败，请分析原因'
};

fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
})
.then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    function readStream() {
        return reader.read().then(({ done, value }) => {
            if (done) {
                console.log('流式响应结束');
                return;
            }

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        console.log(`类型: ${data.type}`);

                        if (data.type === 'tool_call') {
                            console.log(`  调用工具: ${data.tool}`);
                        } else if (data.type === 'final') {
                            console.log(`  最终结果: ${data.content}`);
                        }
                    } catch (e) {
                        console.error('解析错误:', e);
                    }
                }
            }

            readStream();
        });
    }

    readStream();
})
.catch(error => {
    console.error('请求错误:', error);
});
```

---

### 4. GET 方式流式诊断（兼容 EventSource）

**接口**: `GET /api/chat/stream`

**描述**: 使用 GET 方式进行流式诊断，支持 EventSource

**请求参数**:
- `message`: 诊断问题（必需）
- `user_id`: 用户ID（可选）

**请求示例**:
```bash
curl "http://localhost:8002/api/chat/stream?message=发布任务失败，请分析原因"
```

**JavaScript EventSource 示例**:
```javascript
const message = encodeURIComponent('发布任务失败，请分析原因');
const url = `http://localhost:8002/api/chat/stream?message=${message}`;

const eventSource = new EventSource(url);

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(`类型: ${data.type}`);

    if (data.type === 'tool_call') {
        console.log(`  调用工具: ${data.tool}`);
    } else if (data.type === 'final') {
        console.log(`  最终结果: ${data.content}`);
        eventSource.close(); // 完成后关闭连接
    }
};

eventSource.onerror = function(error) {
    console.error('EventSource错误:', error);
    eventSource.close();
};
```

---

## 🔧 响应数据格式

### 通用响应字段

所有响应都包含 `type` 字段，表示消息类型：

| 类型 | 描述 | 包含字段 |
|------|------|----------|
| `start` | 开始诊断 | `message` |
| `thinking` | AI思考过程 | `content` |
| `tool_call` | 工具调用 | `tool`, `input` |
| `tool_result` | 工具执行结果 | `tool`, `result`, `success` |
| `final` | 最终结果 | `content`, `status` |
| `error` | 错误信息 | `message`, `status` |

### 同步响应格式

同步接口返回标准的 JSON 对象：

```json
{
  "response": "完整的诊断结果字符串",
  "status": "success|error"
}
```

## 🧪 测试工具

### 1. curl 测试脚本

```bash
#!/bin/bash
# 健康检查
echo "=== 健康检查 ==="
curl -s http://localhost:8002/api/health | jq .

echo -e "\n=== 同步诊断 ==="
curl -s -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "发布任务失败，请分析原因"}' | jq .

echo -e "\n=== 流式诊断 ==="
curl -s -X POST http://localhost:8002/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "发布任务失败，请分析原因"}' | while read line; do
    if [[ $line == data:* ]]; then
      echo "${line#data: }"
    fi
  done
```

### 2. Python 测试脚本

```python
import requests
import json
import time

BASE_URL = "http://localhost:8002"

def test_health():
    """测试健康检查"""
    response = requests.get(f"{BASE_URL}/api/health")
    print("健康检查:", response.json())

def test_sync_chat():
    """测试同步诊断"""
    payload = {"message": "发布任务失败，请分析原因"}
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    result = response.json()
    print("同步诊断结果:")
    print(result["response"])

def test_stream_chat():
    """测试流式诊断"""
    payload = {"message": "发布任务失败，请分析原因"}
    response = requests.post(f"{BASE_URL}/api/chat/stream", json=payload, stream=True)

    print("流式诊断过程:")
    for line in response.iter_lines():
        if line and line.startswith(b'data: '):
            data = json.loads(line[6:])
            print(f"  {data['type']}: {data.get('message', data.get('content', ''))[:50]}...")

if __name__ == "__main__":
    print("开始API测试...")
    test_health()
    test_sync_chat()
    test_stream_chat()
    print("测试完成!")
```

### 3. JavaScript 测试脚本

```html
<!DOCTYPE html>
<html>
<head>
    <title>Auto DevOps API 测试</title>
</head>
<body>
    <h1>Auto DevOps API 测试</h1>

    <div>
        <h2>同步诊断</h2>
        <textarea id="input" rows="3" cols="50" placeholder="输入诊断问题...">发布任务失败，请分析原因</textarea><br><br>
        <button onclick="testSync()">同步诊断</button>
        <button onclick="testStream()">流式诊断</button>
        <button onclick="clearResult()">清空结果</button>
    </div>

    <div>
        <h2>诊断结果</h2>
        <pre id="result"></pre>
    </div>

    <script>
        const resultDiv = document.getElementById('result');

        function clearResult() {
            resultDiv.textContent = '';
        }

        function appendResult(text) {
            resultDiv.textContent += text + '\n';
        }

        async function testSync() {
            clearResult();
            appendResult('开始同步诊断...');

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: document.getElementById('input').value
                    })
                });

                const result = await response.json();
                appendResult(`状态: ${result.status}`);
                appendResult(`结果: ${result.response}`);
            } catch (error) {
                appendResult(`错误: ${error.message}`);
            }
        }

        async function testStream() {
            clearResult();
            appendResult('开始流式诊断...');

            try {
                const response = await fetch('/api/chat/stream', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: document.getElementById('input').value
                    })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                appendResult(`${data.type}: ${JSON.stringify(data, null, 2)}`);
                            } catch (e) {
                                // 忽略解析错误
                            }
                        }
                    }
                }
            } catch (error) {
                appendResult(`错误: ${error.message}`);
            }
        }
    </script>
</body>
</html>
```

## 🔍 错误处理

### HTTP 状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "response": "诊断执行失败: 具体错误信息",
  "status": "error"
}
```

### 流式错误

流式接口在发生错误时会返回错误类型消息：

```
data: {"type": "error", "message": "诊断过程中出现错误: 具体错误信息", "status": "failed"}
```

## 📊 性能优化建议

### 客户端优化

1. **连接复用**: 使用 HTTP Keep-Alive
2. **并发控制**: 限制并发请求数量
3. **错误重试**: 实现指数退避重试机制
4. **缓存结果**: 对相同问题进行缓存

### 服务端优化

1. **异步处理**: 充分利用异步特性
2. **资源限制**: 设置最大并发数
3. **超时控制**: 设置合理的超时时间
4. **监控告警**: 监控API性能和错误率

---

🚀 **开始使用 Auto DevOps API，享受智能故障诊断服务！**