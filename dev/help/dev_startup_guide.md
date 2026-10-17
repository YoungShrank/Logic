# 开发环境启动指南（前台 / 后台）

> 面向开发人员，不是终端用户帮助（用户帮助在界面顶部栏 →「用户帮助」，或 `http://localhost:3000/#help`）。
> 实测环境：Windows 11；Python 3.10.5（`D:\Software\python.exe`）+ Flask 3.1.0 / Flask-Cors；Node v24.13.0 / npm 11.6.2。验证日期 2026-10-17。

## 1. 仓库与运行形态

| 目录 | 角色 | 默认地址 |
|---|---|---|
| `backend_logic_y2_1` | Flask 推理机（领域状态唯一所有者） | `http://127.0.0.1:5000` |
| `forend-logicy2-1` | React（CRA 5）图形界面 | `http://localhost:3000` |
| `Structure` | 后台依赖的 Python 包（`from Structure import ...`） | 必须与后台仓同级 |

后台依赖的 `Structure` 包不在本仓内，`test.py` 通过向 `sys.path` 追加 `D:/WorkPlace/github` 来找到它。目录布局应为：

```
D:/WorkPlace/github/
    backend_logic_y2_1/
    Structure/
    forend-logicy2-1/
```

## 2. 前置条件

- **Python**：3.10.x，且已安装 `flask`、`flask-cors`、`pandas`。
  本机的 `python` 命令指向 3.14，**未安装 Flask**；可用的是 `D:\Software\python.exe`（3.10.5）。缺少依赖时执行：
  ```
  D:\Software\python.exe -m pip install flask flask-cors pandas
  ```
- **Node.js**：18+（实测 v24），首次启动前在 `forend-logicy2-1` 下执行 `npm install`。
- 端口 `5000`、`3000` 未被其他进程占用。

## 3. 启动后台

从后台仓根目录运行 `test.py`，**不要**直接运行 `interface/logic_flask.py`。

**cmd：**
```
cd /d D:\WorkPlace\github\backend_logic_y2_1
set PYTHONIOENCODING=utf-8
D:\Software\python.exe test.py
```

**PowerShell：**
```
cd D:\WorkPlace\github\backend_logic_y2_1
$env:PYTHONIOENCODING="utf-8"
D:\Software\python.exe test.py
```

**Git Bash：**
```
cd /d/WorkPlace/github/backend_logic_y2_1
PYTHONIOENCODING=utf-8 D:/Software/python.exe test.py
```

也可用 `D:\Software\python.exe -X utf8 test.py` 代替环境变量（已实测两种方式均可）。

**为什么用 `test.py`：** 它在仓库根目录下补齐 `sys.path`（仓库根、`resource/`、`D:/WorkPlace/github`）后才调用 `run_logic_flask()`。直接运行 `python interface/logic_flask.py` 会因找不到 `semantic` 包而报 `ModuleNotFoundError: No module named 'semantic'`（已实测）。

**为什么要 UTF-8：** 文法初始化会向控制台打印含 `¬` 的调试信息。在 GBK 控制台下会抛 `UnicodeEncodeError: 'gbk' codec can't encode character '\xac'`，服务在监听端口前就退出。

**预期输出：** 启动时会打印大量文法调试信息（`NONONONO`、`<S> ...`、`end assert` 等），随后 Flask 开发服务器监听 `5000`（`debug=True`，改动后台代码会自动重载）。启动需要数秒。

**验证后台：**
```
curl -X POST http://127.0.0.1:5000/read -H "Content-Type: application/json" -d "{\"items\":[]}"
```
返回包含 `AS`、`AX`、`CC`、`GL` 等字段的 JSON 即为正常。CORS 已全开放（`interface/logic_flask.py:9`，`origins="*"`）。

## 4. 启动前台

**cmd / PowerShell：**
```
cd /d D:\WorkPlace\github\forend-logicy2-1
npm install
npm start
```

浏览器打开 `http://localhost:3000`。

- 前台接口地址**硬编码**在 `src/config.js`（`API_BASE_URL = 'http://127.0.0.1:5000'`），目前不读取环境变量。后台地址/端口变化时需同步修改该文件。
- Git Bash 下可用 `BROWSER=none npm start` 阻止自动打开浏览器。
- 帮助页：`http://localhost:3000/#help`（顶部栏「用户帮助」会在新页签打开）。
- 开发服务器支持热重载；修改 `src/` 后页面自动刷新。

**推荐启动顺序：** 先后台 → 用 `/read` 验证 → 再前台 → 打开 `3000`。

## 5. 测试与构建（前台）

```
cd /d D:\WorkPlace\github\forend-logicy2-1
npx react-scripts test --watchAll=false   # 当前 4 套 / 13 项通过
npm run build
```

注意：`CI=true` 时 CRA 会把 lint 警告当错误，构建会因以下**既有**告警失败：

- `src/components/ProofArea.jsx:62` — `timer` 未使用
- `src/components/ProofInterface.jsx:2/11/27` — `axios`、`API_BASE_URL`、`selectedRule`/`setSelectedRule` 未使用

这些与本次功能无关，构建时不设置 `CI=true` 即可通过；如需 CI 构建，先清理这些未使用变量。

## 6. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | 用了未装依赖的解释器 | 改用 `D:\Software\python.exe` 或安装依赖 |
| `UnicodeEncodeError: 'gbk' codec can't encode character '\xac'` | 控制台编码不是 UTF-8 | `PYTHONIOENCODING=utf-8` 或 `-X utf8` |
| `ModuleNotFoundError: No module named 'semantic'` | 直接运行了 `interface/logic_flask.py` | 从仓库根运行 `test.py` |
| `ModuleNotFoundError: No module named 'Structure'` | 仓库布局不同或 `Structure` 不在 `D:/WorkPlace/github` | 保持第 1 节目录布局，或修改 `test.py` 中的 `sys.path` 路径 |
| 后台端口被占用（`Address already in use`） | 已有后台实例在运行 | `netstat -ano \| findstr :5000` 查 PID；停止旧实例，或同时修改 `interface/logic_flask.py:109/112` 与 `src/config.js` |
| 前台请求失败 / CORS 报错 | 后台未启动或地址不一致 | 先用 `/read` 验证后台，再核对 `src/config.js` |
| `3000` 被占用 | 已有 dev server 或其他程序 | 停止旧进程，或按 CRA 提示换端口（换端口不影响后台） |
