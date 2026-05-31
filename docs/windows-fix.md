# lark-channel-bridge Windows 兼容性修复文档

## 问题概述

在 Windows 11 (Git Bash) 上运行 `lark-channel-bridge run` 时报错：

```
✗ 未找到 claude CLI。请先安装 Claude Code：
  https://docs.anthropic.com/en/docs/claude-code/quickstart
```

但终端中 `claude --version` 可以正常执行，返回 `2.1.158 (Claude Code)`。

## 排查过程

### 第一轮：ENOENT 错误

**现象**：bridge 的 `ClaudeAdapter.isAvailable()` 检查 claude 是否存在，返回 false。

**定位**：阅读 bridge 源码 `src/agent/claude/adapter.ts`：

```typescript
async isAvailable(): Promise<boolean> {
    return new Promise((resolve) => {
      const child = spawn(this.binary, ['--version'], { stdio: 'ignore' });
      child.on('error', () => resolve(false));  // ← 这里触发 ENOENT
      child.on('exit', (code) => resolve(code === 0));
    });
  }
```

**测试验证**：

```javascript
// 不加 shell:true → ENOENT ❌
spawn('claude', ['--version'], { shell: false })

// 加 shell:true → 正常 ✅
spawn('claude', ['--version'], { shell: true })
```

**根因**：Windows 上 npm 全局安装的 `claude` 是一个无后缀的 shell 脚本（不是 `.exe`），Node.js 的 `child_process.spawn()` 在不使用 `shell: true` 时直接调用 Windows `CreateProcess` API，该 API 只识别 `.exe`、`.com`、`.bat`、`.cmd` 后缀。

**对比**：同一仓库的 `src/cli/preflight.ts` 中检查 lark-cli 时正确地使用了 `shell: process.platform === 'win32'`，说明这是一个遗漏。

### 第二轮：shell:true 导致参数传递失败（方案废弃）

**尝试修复**：在 `isAvailable()` 和 `run()` 的 `spawn` 调用中都加上 `shell: process.platform === 'win32'`。

**结果**：bridge 能启动了，但飞书返回 `(no content)`。

**日志分析**：

```
phase=agent, event=exit, code=0     ← claude 进程正常退出
phase=card, event=final, done       ← run 正常结束
```

但回复内容为空。进一步诊断发现：

- `shell: true` 在 Windows 上会经过 `cmd.exe /c` 执行
- 当 args 中包含长文本（桥接系统提示词 ~4400 字符、中文 prompt 等）时，`cmd.exe` 的参数拼接会出现转义问题
- 导致 claude 虽然正常启动和退出，但实际接收到的命令行参数可能损坏

日志中也确实出现了 `stderr: 语法不正确` 的错误记录。

**结论**：`shell: true` 对简单参数（`--version`）有效，但对复杂参数（`-p "长prompt"`）会导致参数解析失败。此方案不可行。

### 第三轮：cmd.exe /c 包装（方案废弃）

**尝试修复**：在构造函数中将 Windows 上的 binary 设为 `cmd.exe`，args 前追加 `["/c", "claude"]`：

```javascript
constructor(opts = {}) {
    if (process.platform === "win32") {
      this.binary = "cmd.exe";
      this._prefix = ["/c", "claude"];
    }
}
// spawn 变为: spawn('cmd.exe', ['/c', 'claude', '-p', ..., '--verbose'])
```

**结果**：bridge 能启动，但回复仍然是 `(no content)`。

**根因**：`cmd.exe /c` 作为中间层，标准输出管道（stdout pipe）行为与直接执行不同。当 claude 产生大量 stream-json 输出时，cmd.exe 的缓冲机制可能导致输出在管道中被截断或延迟，bridge 的 readline 解析器收不到完整的 JSON 行。

### 第四轮：claude.exe 全路径（最终方案 ✅）

**关键突破**：参考了 GitHub Issue [#13](https://github.com/zarazhangrui/feishu-claude-code-bridge/issues/13) 中其他用户的调试发现。

该 Issue 的关键发现：

> `claude.exe` 在 PowerShell 中可以直接执行，但通过 Node.js `child_process` 调用时会无限挂起。即使在 `claude.exe` 所在目录之外使用完整路径调用也会失败。

这表明 `claude.exe` 对其安装目录有依赖。但值得注意：该 Issue 作者的版本是 `2.1.148`，问题表现是"挂起"；而当前环境 `2.1.158` 中，"挂起"已修复，但 "ENOENT" 仍然存在。

**该 Issue 最重要的启发**：

```cmd
REM claude.cmd 内容
"%dp0%\node_modules\@anthropic-ai\claude-code\bin\claude.exe" %*
```

`claude.cmd` 使用 `%dp0%`（即 npm 全局 bin 目录）来定位 `claude.exe`。这意味着：
1. `claude.exe` 的实际路径是确定的：`{npm-global}\node_modules\@anthropic-ai\claude-code\bin\claude.exe`
2. 绕过 `claude.cmd` 包装，直接调用 `claude.exe` 可以避开 shell 执行的各种问题

**测试验证**：

```javascript
const claudeExe = process.env.APPDATA +
  '\\npm\\node_modules\\@anthropic-ai\\claude-code\\bin\\claude.exe';

// 测试：全路径 + 项目目录作为 cwd → 完美工作 ✅
const c = spawn(claudeExe, [
  '-p', '说一个字：好',
  '--output-format', 'stream-json',
  '--verbose'
], {
  cwd: 'd:/Coding/vibe_coding项目/vibe_coding_tutorial',  // 与 claude 安装目录不同
  stdio: ['ignore', 'pipe', 'pipe']
});
// 输出：
// assistant: thinking: "The user just said..."
// assistant: text: "好！有什么我可以帮你的吗？"
```

**结论**：
- `claude.exe` 可以通过全路径在任意工作目录下正常执行
- 不需要 `shell: true`
- 不需要 `cmd.exe` 包装
- 直接 spawn 的 stdout pipe 工作正常

## 最终修复

### 修改文件

```
C:\Users\<用户名>\AppData\Roaming\npm\node_modules\lark-channel-bridge\dist\cli.js
```

### 修改内容

**位置**：`ClaudeAdapter` 类的构造函数（约第 1175 行）

```javascript
// 修改前
constructor(opts = {}) {
    this.binary = opts.binary ?? "claude";
}

// 修改后
constructor(opts = {}) {
    if (process.platform === "win32") {
      this.binary = process.env.APPDATA + "\\npm\\node_modules\\@anthropic-ai\\claude-code\\bin\\claude.exe";
    } else {
      this.binary = opts.binary ?? "claude";
    }
}
```

### 为什么只改这一处

`this.binary` 在 `isAvailable()` 和 `run()` 两处都被使用：

```javascript
// isAvailable() — 检查 claude 是否存在
spawn(this.binary, ["--version"], { stdio: "ignore" });

// run() — 实际执行 claude
spawn(this.binary, args, { cwd: opts.cwd, ... });
```

构造函数改了 `this.binary` 的值，两处 spawn 自动生效，不需要分别修改。

### 为什么不需要 shell: true

Windows 的 `CreateProcess` API 可以直接执行 `.exe` 文件。`claude.exe` 全路径指向的是真正的 PE 可执行文件，不需要 shell 包装。这避免了所有 shell 转义和管道缓冲问题。

### 方案对比

| 方案 | isAvailable | run() 参数传递 | 回复内容 | 最终 |
|------|------------|---------------|---------|------|
| 原始代码 (spawn 'claude') | ENOENT ❌ | N/A | N/A | ❌ |
| shell: true 全局 | 通过 ✅ | 参数损坏 ❌ | (no content) | ❌ |
| cmd.exe /c 包装 | 通过 ✅ | 管道问题 ❌ | (no content) | ❌ |
| **claude.exe 全路径** | **通过 ✅** | **正常 ✅** | **正常 ✅** | **✅** |

## 副作用与注意事项

1. **npm update 会覆盖**：`npm update -g lark-channel-bridge` 会用官方版本覆盖修改。升级后需要重新应用补丁。

2. **APPDATA 路径假设**：补丁假设 npm 全局安装目录为 `%APPDATA%/npm`。如果用户使用 `nvm` 或自定义 npm prefix，需要相应调整路径。

3. **仅影响 Windows**：`process.platform === "win32"` 条件确保 macOS/Linux 行为完全不变。

4. **lark-cli bind 问题独立存在**：bridge 启动时用了 `--skip-check-lark-cli` 跳过了 lark-cli 绑定（这是另一个 Windows 兼容性问题：lark-cli 的 Go 安全审计误判 NTFS 文件权限为 "world-writable"）。聊天核心功能不受影响，但 Claude 无法直接调用飞书 API（日历、文档等）。

## 参考

- [GitHub Issue #13](https://github.com/zarazhangrui/feishu-claude-code-bridge/issues/13) — 其他用户提供的 Windows 调试发现
- lark-channel-bridge 源码 `src/agent/claude/adapter.ts` — ClaudeAdapter 实现
- lark-channel-bridge 源码 `src/cli/preflight.ts` — 已有 `shell: platform === 'win32'` 先例
