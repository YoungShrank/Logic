# 用户帮助与选区内容展示 设计

- 日期：2026-10-17
- 状态：设计已获用户认可
- 需求来源：`dev/request/user_help.md`
- 实现仓库：`forend-logicy2-1`
- 参考：
  - `dev/modeling/ui/forend_logic_y2_1_modeling.md`
  - `dev/modeling/architecture_code_graph.md`
  - `dev/help/proof_add_add_zero_guide.md`

## 1. 目标

1. 新增用户帮助页，从顶部栏在新页签打开。
2. 结论 ID、辅助项、替换/操作范围的展示补充对应项内容，不再只显示 ID 或起止编号。
3. 为等式替换的「左侧替换 / 右侧替换」增加问号悬浮说明。
4. 修正选区监听中 `bra` 分支的条件优先级缺陷。

## 2. 非目标

- 不引入 `react-router-dom`、Markdown 渲染器等新依赖。
- 不改后端接口与 `interface.yaml` 契约。
- 不改变结论 ID 的 0 基语义。
- 不修复「`introduce` 手输 ID 缺少 `conclusion_id`」与「选区 `/cp2tp` 固定 3 秒且不可取消」两个既有缺陷；帮助页 FAQ 中给出规避方法，另按 `dev/issues/template.md` 跟踪。

## 3. 当前状态与问题

- `ProofInterface.jsx:170-176` 已把 `conclusions`、`terms`、`selectedSubterm` 传给 `ApplicationPanel`，但 `ApplicationPanel.jsx:23-24` 未使用 `conclusions` 与 `terms`。
- 顶部「选择结论ID」、等式替换「等式ID」只显示数字；量词消去的辅助项只显示名称；「替换范围 / 操作范围」只显示起止 token。
- 后端结论下标为 0 基（`logic_api.py:112` 直接 `env.conclusions[conclusion_id]`），界面步骤标号为 1 基，用户难以把 ID 与具体项对应。
- `ApplicationPanel.jsx:37-39` 的条件 `selectedSubterm && selectedRule === 'eqrepl' || selectedRule === 'bra'` 存在优先级问题：`bra` 在无选区时也会读取 `selectedSubterm?.tstart`。

## 4. 总体方案

采用少量共享组件，把「ID→内容」解析与预览展示集中到一份实现中；帮助页作为 React 内部页面，通过 URL 哈希 `#help` 进入。

### 4.1 组件与改动清单

| 文件 | 类型 | 职责 |
|---|---|---|
| `src/components/AppHeader.jsx` | 新增 | 顶部窄栏：产品名 + 「用户帮助」链接 |
| `src/components/HelpPage.jsx` | 新增 | 帮助页：固定侧边目录 + 滚动正文 + 返回链接 |
| `src/components/common/HelpTip.jsx` | 新增 | `?` 悬浮提示，支持 hover 与键盘 focus |
| `src/components/common/ReferencePreview.jsx` | 新增 | 结论内容、辅助项内容、选区文本三种只读预览 |
| `src/utils/reference.js` | 新增 | 纯函数：0 基 ID 解析、辅助项查找、选区文本判定 |
| `src/styles/help.css` | 新增 | 帮助页样式 |
| `src/App.js` | 修改 | 移除 `hello, world.`；挂载 `AppHeader`；按 `#help` 渲染帮助页 |
| `src/components/ApplicationPanel.jsx` | 修改 | 接入预览与 tooltip；修正 `bra` 条件 |
| `src/styles/interface.css` | 修改 | 顶部栏高度、预览框、tooltip 样式 |
| `src/App.css` | 修改 | `.App` 改为左对齐；移除未使用的 logo 样式与导入 |
| `src/App.test.js` | 替换 | 原断言为 CRA 模板的 “learn react”，改为 `AppHeader` 测试 |

### 4.2 入口与路由

- 顶部栏右侧： `<a href="/#help" target="_blank" rel="noopener noreferrer">用户帮助</a>`。
- `App` 用状态保存 `window.location.hash === '#help'`，并监听 `hashchange`。
- 为真时只渲染 `HelpPage`（不挂载推理界面，不发起 `/read`）。
- 未知哈希按主界面处理。
- 帮助页内提供 `href="/"` 的「返回推理界面」链接。

### 4.3 布局

- 新增 CSS 变量 `--app-header-height: 48px`。
- `.app-header` 为 flex 横栏，左侧产品名，右侧帮助链接。
- `.interface-container` 高度由 `100vh` 改为 `calc(100vh - var(--app-header-height))`。

## 5. 展示与数据流

### 5.1 数据来源

- 结论内容：`ProofInterface` 从 `/read` 的 `CC` 得到 `conclusions`（`ProofInterface.jsx:59`）。
- 辅助项内容：`/read` 的 `TM` 映射为 `terms: [{name, content}]`（`ProofInterface.jsx:54-57`）。
- 选区：`ProofArea` 在 `/cp2tp` 返回后回调 `{conclusion_id, text, start, end, tstart, tend}`（`ProofArea.jsx:73-80`）。
- 预览全部为只读派生，不参与请求载荷，提交逻辑保持原样。

### 5.2 解析规则

| 预览 | 规则 |
|---|---|
| 结论内容 | 先排除空串（`String(id).trim() === ''`，注意 `Number('') === 0`）；再转整数 `n`，`n >= 0` 且 `n < conclusions.length` 时取 `conclusions[n]`（0 基） |
| 辅助项内容 | `terms.find(t => t.name === id)?.content` |
| 选区文本 | 仅当 `selectedSubterm` 存在、`String(first) === String(tstart)`、`String(last) === String(tend)`、且选区结论与当前结论 ID 一致时，取 `text.slice(start, end + 1)`（`end` 为闭区间） |

### 5.3 展示位置

| 位置 | 现有内容 | 新增内容 |
|---|---|---|
| 顶部「选择结论ID」 | ID | 该结论完整文本 |
| 等式替换「等式ID」 | ID | 该结论完整文本 |
| 量词消去辅助项拖放提示 | 名称徽标 | 名称 + 辅助项文本 |
| 等式替换「替换范围」 | 起止编号 | 当前选区子项文本 |
| 括号操作「操作范围」 | 起止编号 | 当前选区子项文本 |

### 5.4 展示样式

- 预览框：`div.reference-preview`，等宽字体、浅灰背景、`word-break: break-all`，位于对应输入附近。
- ID 为空：不渲染预览。
- ID 非法或越界：显示「未找到 ID 为 X 的结论」/「未找到辅助项 X」，使用警示色。
- 选区为空：范围下方显示弱提示「尚未选择子项（在结论中拖选后自动填入）」。
- 手动改过起止编号导致与最后选区不一致：隐藏旧文本，显示「手动范围，无选区预览」。

### 5.5 等式替换 tooltip

在「替换位置」标签旁放置 `?`，hover 或键盘聚焦时显示：

- 左侧替换：等式**左端为旧项**，用右端替换结论中与旧项相同的子项。
- 右侧替换：等式**右端为旧项**，用左端替换结论中与旧项相同的子项。

语义依据：`semantic/convert.py:99-125`（`old_side` 决定 old/new 取等式的哪一侧）。

### 5.6 条件修正

```js
if (selectedSubterm && (selectedRule === 'eqrepl' || selectedRule === 'bra')) {
  // ...
}
```

## 6. 帮助页

### 6.1 布局

- 左侧固定目录，右侧滚动正文。
- 窄屏（建议断点 900px）下目录变为正文顶部的一组锚点链接，仅用 CSS。
- 帮助页自带标题与「返回推理界面」链接，不展示主界面顶部栏。

### 6.2 章节

1. 快速开始：Global / Proof / Assert 模式，命令输入，结论编号。
2. 命令速查：`theorem`/`lemma`、`proof`、`any`、`one`、`one x := t`、`assume`、`assert`、`;`、`qed`。
3. 推理规则：一阶推理、量词消去、量词引入、等式替换、括号操作、结束证明的参数与用途；等式替换含左右侧说明。
4. 界面面板：定理/公理、变量、假设、证明区、辅助项、规则应用区、拖放约定。
5. 完整示例：`dev/help/proof_add_add_zero_guide.md` 的 12 步 ADD 证明。
6. 常见问题：
   - 选区后需等待约 3 秒；
   - 量词引入的结论 ID 必须拖动结论卡片；
   - ID 为 0 基而步骤标号为 1 基；
   - `tadd` 选区不含外层括号，替换/去括号选区含外层括号；
   - `qed` 逐字符精确匹配。

### 6.3 内容维护

帮助内容直接写在 `HelpPage.jsx` 中。与 `dev/help` 指南存在一份示例重复，属于跨仓文档同步成本；本次不引入运行期 Markdown 加载。

## 7. 异常与边界

- 帮助页直接访问、刷新、书签打开均可用；不依赖后端。
- 未知哈希回主界面。
- 帮助页不发起任何 API 请求。
- 预览解析失败不影响表单提交。
- tooltip 在滚动容器内不被裁剪；窄屏下允许换行。

## 8. 测试与验收

### 8.1 单元测试

- `src/utils/reference.test.js`：
  - 结论 ID `0`、字符串 `"0"`、越界、负数、空值；
  - 辅助项存在与不存在；
  - 选区匹配/不匹配（`tstart/tend`、结论 ID）。
- `src/components/AppHeader.test.js`：
  - 渲染产品名；
  - 帮助链接 `href="/#help"`、`target="_blank"`、`rel` 含 `noopener noreferrer`。
- 删除失效的 `App.test.js`（其断言 “learn react” 与当前界面无关，必然失败）。

### 8.2 手工验收

1. 点击「用户帮助」→ 新页签打开 `/#help`，目录锚点可跳转，返回链接可用。
2. 拖动/输入结论 ID → 两个结论输入位置均显示结论文本；越界 ID 显示警示。
3. 在结论中拖选并等待 3 秒 → 替换/操作范围显示选中子项文本；手动改编号后预览消失。
4. 拖入辅助项 → 显示名称与文本。
5. hover / Tab 聚焦 `?` → tooltip 显示左右侧语义。
6. 按 `dev/help/proof_add_add_zero_guide.md` 完成 12 步 ADD 证明，确认无回归。

## 9. 风险

- 帮助页示例与 `dev/help` 指南可能随时间漂移；以帮助页 FAQ 和指南互链的方式降低误解成本。
- 结论 ID 仍为 0 基；预览缓解但不消除「步骤 1 对应 ID 0」的认知负担，帮助页 FAQ 明确说明。
- 顶部栏占用 48px 高度，需确认小屏下主界面仍可用。
- tooltip 位于规则应用区内，需避免被后续表单元素遮挡（提高 `z-index`）。

## 10. 后续事项

- 按 `dev/issues/template.md` 记录：
  - `introduce` 手输结论 ID 时载荷缺少 `conclusion_id`；
  - 选区 `/cp2tp` 固定 3 秒延迟且无取消机制。
- 设计通过后进入 `writing-plans`，生成实现计划。
