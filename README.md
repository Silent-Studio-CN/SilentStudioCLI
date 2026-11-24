# SilentStudio CLI

> 让开发者体验更好一点。

SilentStudio CLI 是一个命令行工具，旨在改善开发者的日常体验。它提供了项目初始化、包管理、跨平台适配等功能，所有设计都围绕一个核心理念：**程序员也是人，值得被好好对待。**

---

## 📦 安装

### 从 PyPI 安装（推荐）

```bash
pip install silentstudio
```

### 从源码安装

```bash
git clone https://github.com/Silent-Studio-CN/SilentStudioCLI.git
cd SilentStudioCLI
pip install -e .
```

---

## 🚀 快速开始

安装后同时提供 `silentstudio` 和 `ss` 两个命令，下面统一用 `ss`。

```bash
# 1. 创建一个 Java 项目
ss new my-first-project -l java

# 2. 安装 SlimeMold 库
ss slimemold

# 3. 查看已安装的库
ss install list
```

---

## 🚀 发布与 Git

    # 每个仓库一份配置
    ss release config

    # 触发 GitHub Actions 发布并等待完成
    ss release silentcraft 3.18

    # 指定 commit 和目标版本
    ss release silentcraft 3.18 <commit> --dry-run

    # git 透传 / 快捷命令
    ss git status
    ss status
    ss commit -m "message"
    ss push

配置写入仓库根目录 .ss.json，不会保存任何令牌；发布使用本机 gh auth 登录态。

## 📖 命令详解

### 1. 显示帮助

```bash
silentstudio
```

显示所有可用命令和示例。

---

### 2. 显示版本信息

```bash
silentstudio -v
# 或
silentstudio --version
```

输出示例：
```
SilentStudio CLI v0.1.0
```

---

### 3. 创建新项目

```bash
silentstudio new <项目名称> -l <编程语言>
# 或
silentstudio new <项目名称> --lang <编程语言>
```

**支持的编程语言：**

| 语言 | 说明 |
|------|------|
| `java` | 创建 Maven 风格的 Java 项目 |
| `python` | 创建 Python 包项目 |
| `go` | 创建 Go 模块项目 |

**示例：**

```bash
# 创建 Java 项目
silentstudio new my-app -l java

# 创建 Python 项目
silentstudio new my-lib -l python

# 创建 Go 项目
silentstudio new my-service -l go
```

**生成的项目结构：**

**Java 项目：**
```
my-app/
├── src/
│   ├── main/
│   │   ├── java/
│   │   └── resources/
│   └── test/
│       └── java/
├── pom.xml
├── README.md
└── .gitignore
```

**Python 项目：**
```
my-lib/
├── src/
├── tests/
├── setup.py
├── README.md
├── requirements.txt
└── .gitignore
```

**Go 项目：**
```
my-service/
├── cmd/
├── internal/
├── pkg/
├── go.mod
├── main.go
├── README.md
└── .gitignore
```

---

### 4. 安装 SilentStudio 生态库

```bash
silentstudio <包名>
```

这是 SilentStudio 的**核心功能**，它会智能地从多个源查找并安装包。

**工作流程：**

```
1. 检查本地是否已安装
   ├── 已安装 → 提示版本信息，退出
   └── 未安装 → 继续

2. 查询 SilentStudio 官方索引
   ├── 找到 → 从指定渠道安装（如 PyPI）
   └── 未找到 → 继续

3. 回退到 PyPI 官方源
   ├── 存在 → 询问用户是否安装
   │   ├── Y → 安装
   │   └── N → 取消
   └── 不存在 → 报错退出
```

**示例：**

```bash
# 安装 SlimeMold（SilentStudio 生态库）
ss slimemold

# 安装 PyPI 上的第三方库（需确认）
silentstudio requests
```

**输出示例（SilentStudio 生态库）：**
```
📡 正在查询 SilentStudio 索引...
📦 从 PyPI 安装 slimemold...
✅ 成功安装 slimemold (版本: 0.3.1)
```

**输出示例（PyPI 第三方库）：**
```
⚠️ 您搜索的 'requests' 并未在 SilentStudio 项目列表中查询到
📦 但在官方 PyPI 上找到了同名库 (最新版本: 2.31.0)
是否安装？[y/N]: y
✅ 成功安装 requests (版本: 2.31.0)
```

---

也可以通过 `ss install <包名>` 安装；安装时会流式显示各源版本，并提示选择源：

```bash
ss install pyqt6
```

支持输入编号（1-4）、源名称（如 tencent，忽略大小写），或直接回车自动选择最新源。

### 5. 列出已安装的库

```bash
ss install list
```

列出当前 Python 环境中所有已安装的库，并自动区分哪些是通过 SilentStudio 安装的。

**输出示例：**
```
╔══════════════════════════════════════════════════════════════╗
║  📦 已安装 Python 库                                        ║
╠══════════════════════════════════════════════════════════════╣
║  ✦ SilentStudio 安装 (3 个):                                ║
║    ├─ slimemold                            v0.3.1           ║
║    ├─ silent-logger                        v2.1.0           ║
║    └─ colorama                             v0.4.6           ║
╠══════════════════════════════════════════════════════════════╣
║  📚 其他库 (12 个):                                         ║
║    ├─ numpy                               v1.26.0           ║
║    ├─ pandas                              v2.0.3            ║
║    ├─ requests                            v2.31.0           ║
║    └─ ... 还有 9 个                                        ║
╚══════════════════════════════════════════════════════════════╝
```

---

### 6. 多源版本查询

```bash
ss sources silentstudio
```

同时查询 PyPI、阿里云、清华、腾讯云等索引，显示每个源的最新版本：

```text
Package: silentstudio
Source       Version          URL
------------------------------------------------------------------------
PyPI         0.3.1            https://pypi.org/simple
Aliyun       0.1.7            https://mirrors.aliyun.com/pypi/simple
Tsinghua     0.1.7            https://pypi.tuna.tsinghua.edu.cn/simple
Tencent      0.1.7            https://mirrors.cloud.tencent.com/pypi/simple
```

`ss install <包名>` 会先打印同样的源版本表，然后自动选择版本最新的源安装；如果失败，会按顺序回退到其他源。

---

## 🔧 配置

```bash
ss config                 # 查看全部配置
ss config install         # 交互式修改安装范围
ss config language ja     # 修改语言
```


SilentStudio 在用户目录下创建 `~/.silentstudio/` 文件夹：

```
~/.silentstudio/
├── config.json          # 用户配置
├── installed.json       # 安装记录
└── index.cache.json     # 索引缓存
```

### config.json

```json
{
  "language": "auto",              // auto / zh-CN / en-US
  "pypi_mirror": "https://pypi.org/simple/",
  "index_url": "https://raw.githubusercontent.com/Silent-Studio-CN/index/main/index.jsonl",
  "install_scope": "user"          // user / system
}
```

| 配置项 | 说明 | 可选值 |
|--------|------|--------|
| `language` | 界面语言 | `auto`（自动检测）/ `zh-CN` / `en-US` |
| `pypi_mirror` | PyPI 镜像源 | 任意 PyPI 镜像 URL |
| `index_url` | SilentStudio 索引地址 | 任意 JSONL 格式的索引 URL |
| `install_scope` | 安装范围 | `user`（用户级）/ `system`（系统级） |

---

## 📊 SilentStudio 官方索引

SilentStudio 维护了一个官方索引，列出了所有经过验证的生态库。

**索引格式（JSONL）：**

```jsonl
{"name":"SlimeMold","latest_version":"0.3.1","channel":"pypi","pkg_name":"slimemold","description":{"zh-CN":"黏菌启发的轻量级路径规划库 - BFS + 加权概率爬行","en-US":"A lightweight path planning library inspired by slime molds - BFS + Weighted Probabilistic Crawling"}}
{"name":"SilentLogger","latest_version":"2.1.0","channel":"pypi","pkg_name":"silent-logger","description":{"zh-CN":"安静的日志库，支持结构化输出","en-US":"A quiet logger with structured output"}}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 显示名称 |
| `latest_version` | string | 最新版本号 |
| `channel` | string | 发布渠道（目前仅支持 `pypi`） |
| `pkg_name` | string | 在渠道中的实际包名 |
| `description` | object | 多语言描述（`zh-CN` / `en-US`） |

---

## 🎯 设计哲学

**程序员也是人，值得被好好对待。**

- **报错信息写给人看**：告诉你哪里错了、收到了什么、应该是什么
- **适配不同习惯**：跨平台快捷键差异？我们想到了
- **注释说人话**：下一个维护者应该一眼看懂
- **多语言文档**：不是所有人都说英语
- **有温度的安全政策**：24 小时内确认漏洞，不追责善意测试者

---

## 🛠️ 开发指南

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/Silent-Studio-CN/SilentStudioCLI.git
cd SilentStudio

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 开发模式安装
pip install -e .
```

### 项目结构

```
SilentStudio/
├── src/
│   └── silentstudio/
│       ├── __init__.py       # 包元信息
│       ├── __main__.py       # python -m 入口
│       ├── cli.py            # 命令行入口
│       ├── installer.py      # 安装逻辑
│       ├── list_packages.py  # 列出包
│       ├── project_new.py    # 创建项目
│       ├── config.py         # 配置管理
│       ├── utils.py          # 工具函数
├── index.jsonl               # 官方索引
├── setup.py                  # 安装脚本
├── pyproject.toml            # 项目配置
├── requirements.txt          # 依赖列表
└── README.md                 # 本文档
```

### 运行测试

```bash
# 测试命令
silentstudio -v
silentstudio new test -l python
ss install list
```

### 构建发布

```bash
# 安装构建工具
pip install build twine

# 构建分发包
python -m build

# 上传到 PyPI
python -m twine upload dist/*
```

---

## 📝 更新日志

### v0.1.0 (2026-07-13)

- 🎉 首次发布
- ✨ 支持 `new` 命令（Java/Python/Go）
- ✨ 支持包安装（索引 + PyPI 回退）
- ✨ 支持 `install list` 列出已安装库
- 🌐 支持中英文自适应
- 📦 支持 PyPI 镜像源配置

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 📄 许可证

MIT License © 2026 SilentStudio

---

## 📧 联系我们

- **SilentStudio 邮箱**：SilentStudio@Home.email.cn
- **项目列表**：[SilentStudio-ProjectList](https://github.com/Silent-Studio-CN/SilentStudio-ProjectList)
- **GitHub**：[Silent-Studio-CN](https://github.com/Silent-Studio-CN)

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
```
