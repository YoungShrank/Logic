

## 需求

开发流程有变，文档组织也变了

## 想法

文档重构  改用 backend_logic_y2_1\dev   旧的 D:\WorkPlace\github\backend_logic_y2_1\bugs | issues 目录直接删除 （没事，有git记录） 

## 方案

- 删除仓库根目录 `bugs/`、`issues/`，工程性文档统一由 `dev/` 承载（历史见 git 记录）。
- `dev/issues/`：问题记录，按 `template.md` 新增 `<时间>-<topic>.md`。
- `dev/request/`：开发请求，`template.md`；bugfix 请求使用 `bugfix/template.md`。
- `dev/modeling/`：架构与建模文档。
- 同步更新 `dev/modeling/architecture_code_graph.md` 与 `dev/modeling/backend_logic_y2_1_modeling.md` 中的路径引用。

## 参考

D:\WorkPlace\github\backend_logic_y2_1\dev\modeling\architecture_code_graph.md