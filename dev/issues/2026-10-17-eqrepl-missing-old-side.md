## META
发现时间：2026-10-17 18:49
简要描述：等式替换请求缺少 `old_side` 字段，后台 `KeyError` 导致 HTTP 500
功能模块：前台推理面板（`ApplicationPanel`）→ `POST /eqrepl`
发现者：CLAUDE（用户提供复现请求与响应）

## 问题描述
- 问题现象

  预期：选择“左侧替换”后应用等式替换，请求成功并生成新结论。

  实际：`POST http://127.0.0.1:5000/eqrepl` 返回 `500 INTERNAL SERVER ERROR`。请求体：

  ```json
  {
      "conclusion_id": "2",
      "equal_id": "1",
      "first": 3,
      "last": 13
  }
  ```

  后台堆栈：

  ```
  File "D:\WorkPlace\github\backend_logic_y2_1\interface\logic_flask.py", line 82, in eqrepl
      old_side = request.json['old_side']
  KeyError: 'old_side'
  127.0.0.1 - - [17/Oct/2026 18:49:11] "POST /eqrepl HTTP/1.1" 500 -
  ```

- 相关信息
  - 前端“替换位置”下拉显示值为 `inputParams.old_side || 'left'`（`src/components/ApplicationPanel.jsx:148`），初始 `inputParams` 中并没有 `old_side`，因此界面显示“左侧替换”，但状态值为 `undefined`。
  - 提交时直接使用原始状态：`old_side: inputParams.old_side`（`src/components/ApplicationPanel.jsx:344`），字段被 JSON 序列化丢弃。
  - 每次提交后的 `finally` 会执行 `setInputParams({})`（`src/components/ApplicationPanel.jsx:375`），即使补了初始值，状态也会再次丢失。
  - 后台 `TermConverter.equal_replace` 的 `old_side` 有默认值 `"left"`（`semantic/convert.py:99`），但 Flask 路由把它当作必填字段硬取键（`interface/logic_flask.py:82`）。
  - 同源隐患：`bra` 的 `off_on` 同样只在界面渲染，未选择任何单选项时按钮仍可点击，提交会缺字段（尚未复现）。

## 问题原因
- 一句话
  默认值只落在渲染层（`|| 'left'`），没有落到提交层；后台把 `old_side` 当作必填字段。

- 故障传播链
  `inputParams` 初值不含 `old_side` → 下拉框借助 `|| 'left'` 显示“左侧替换”（造成已选中的假象）→ 用户点击应用 → payload 中无 `old_side` → `request.json['old_side']` 抛 `KeyError` → Flask 返回 500。

- 根因
  前端“显示值”和“提交值”使用了两种取值方式（渲染时兜底、提交时不兜底），两者不一致；接口契约未对缺省字段做容错。

## 修改方案

以下方案尚未实施，待确认后再改：

1. **前端提交层补默认（最小修复）**：`old_side: inputParams.old_side || 'left'`。
2. **状态初始化与重置保持一致**：初始 `inputParams` 增加 `old_side: 'left'`，并把提交后的 `setInputParams({})` 改为恢复默认值，避免显示/状态再次分叉。
3. **后台防御（可选）**：路由改为 `request.json.get('old_side', 'left')`，与 `convert.py` 的默认值一致。单独使用会掩盖前端缺字段问题，建议作为兜底而非主方案。
4. **同源隐患**：`bra` 在未选择“添加/去除括号”时禁用应用按钮，或与方案 2 一样提供显式默认。

建议：以方案 1 + 2 为主，方案 3 视契约约定决定，方案 4 一并修复。

**已实施（仅前台）**：采用方案 2 + 4，并按“单一事实源”清理渲染层兜底。`inputParams` 的初始值与每次提交后的重置值统一为 `createDefaultParams()`（含 `old_side: 'left'`），保证提交时该字段始终存在；下拉框直接由状态渲染（移除 `|| 'left'`、`|| '∀'`），可选文本输入使用 `?? ''` 仅做受控空值适配；`bra` 在未选择括号操作前禁用应用按钮。后台未改动。回归测试见 `src/components/ApplicationPanel.test.js`（2 项）。

## 验证结果

待用户填写
