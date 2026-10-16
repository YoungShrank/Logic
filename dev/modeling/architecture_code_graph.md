# 推理机Y 架构与代码元素知识图

> 目的：提供项目全景、快速理解、并为增量开发提供**充分但不冗余**的上下文。
> 覆盖仓库：`backend_logic_y2_1`（后台当前分支）、`forend-logicy2-1`（前台）、`cmd-logicy0`（命令行前身）、`backend_logic_y2`（后台旧分支）、`Structure`（共享数据结构库）。

## 符号系统

| 符号 | 含义 |
|:---:|---|
| `+` | 一个元素（架构元素命名为 `xx层`；代码元素为 关键路径/类/函数的引用） |
| 缩进 | 层级：父元素在下级中展开为子元素 |
| `//` | 说明：架构元素的职责；代码元素的文件名/类名/方法名要点 |
| `->` | 关联方向（见文末“关联”），如 调用/交互/依赖 |

*约定*：逻辑概念（架构层）必须有**物理载体**，即在其下级 `代码元素` 中给出对应路径；同名代码只在其**归属**的最深层次展开，其它位置仅引用，避免冗余。

---

## 架构和代码元素

```
+ 项目层
    // 逻辑推理机Y 全栈系统：形式逻辑推理引擎，支持项表示与解析、推理规则、推理环境，
    // 并通过图形界面与命令行两类前端交互。需求场景为数学定理证明/逻辑推理辅助。
    + 代码元素
      + backend_logic_y2_1          // 后台当前分支（Flask 控制器 + 语义推理核心）
      + forend-logicy2-1            // 前台（React 单页图形界面）
      + cmd-logicy0                 // 命令行前端/前身（Y0，携带独立 Structure 副本）
      + backend_logic_y2            // 后台旧分支（与当前分支同构，作为演进基线）
      + Structure                   // 共享数据结构库（Tree/Graph 与可视化）

  + 工程层
      // 开发活动流程相关，非运行态，服务于迭代而非产品本身
    + 缺陷层
        // 已知故障的记录与复现
      + 代码元素
        + backend_logic_y2_1\bugs\copy_tree.md       // 树复制（copy_subtree）
        + backend_logic_y2_1\bugs\import_order.md    // 模块导入顺序
        + backend_logic_y2_1\bugs\test_deduce.md     // 演绎推理
        + backend_logic_y2_1\bugs\  ...              // 各分支同构共享
    + 需求层
        // 需求/问题描述与设计推演
      + 代码元素
        + backend_logic_y2_1\issues\                 // applying_rules, bracket, introduce_quantifier,
                                                     //   static_analyze_term, switcher_function, inplace_substitue ...
        + backend_logic_y2_1\dev\request             // 开发请求（template.md）
        + backend_logic_y2_1\dev\modeling            // 建模文档（本文件所在层）
    + 设计文档层
      + 代码元素
        + backend_logic_y2\docs\backend-logic-y2-topview.md  // 系统总览设计文档（逆向生成）
        + backend_logic_y2_1\README.md                       // 演进说明（假设域栈、类型推断、健壮性）
        + forend-logicy2-1\context\ui-design.md              // 前端界面设计

  + 资源层
      // 不含逻辑的静态资源，由产品层在运行时读取
    + 语法定义层
        // 项/行/标识符的文法（CFG 产生式文本）
      + 代码元素
        + backend_logic_y2_1\resource\grammars\line.txt      // <line> 顶层文法（line/term/set/type 等产生式）
        + backend_logic_y2_1\resource\grammars\term.txt      // 项文法
        + backend_logic_y2_1\resource\grammars\term_plus.txt
        + backend_logic_y2_1\resource\grammars\identifier.txt
        + backend_logic_y2_1\resource\grammars\grammar.txt   // 增广/元文法
        + backend_logic_y2_1\resource\grammars\grammar_id.txt
    + 规则定义层
        // 推理规则文本，格式 {p1,p2,..} |- q
      + 代码元素
        + backend_logic_y2_1\resource\first-order\rules.txt
    + 预定义/用例层
        // 预定义对象、公理与各模块测试语料
      + 代码元素
        + backend_logic_y2_1\resource\test\sentences\predefine2.txt  // Union/N/ADD/_0 等预定义
        + backend_logic_y2_1\resource\test\sentences\predefine.txt
        + backend_logic_y2_1\resource\test\sentences\lines_for_*.txt  // lines_for_{analyser,axiom,bracket,cmd,context,
                                                                      //   converter,cp2tp,deduce,eq_replace}.txt
    + 可视化产物层
        // 语法树/类型推导的可视化输出
      + 代码元素
        + backend_logic_y2_1\resource\out\*.html    // solve_type, solve_var, solve_varT_list, sort_deduce ...

  + 产品层
      // 最终系统运行态：推理机
    + 交互层
        // 用户接口：HTTP（前台）与 命令行（cmd）
      + 协议契约层
          // 前后端解耦依据：REST 端点与数据契约
        + 代码元素
          + backend_logic_y2_1\interface\interface.yaml   // OpenAPI 3.0：12 端点定义
          + forend-logicy2-1\context\interface.yaml       // 前端本地开发用的契约副本
      + Web接口层
          // Flask 控制器：REST 端点 -> LogicApi，返回当前模式
        + 代码元素
          + backend_logic_y2_1\interface\logic_flask.py   // app；/deduce,/instance,/introduce,/select,/use,
                                                          //   /qed,/bra,/conclude,/eqrepl,/write_line,/read,/cp2tp
          + backend_logic_y2_1\interface\logic_y1.py       // GUILogicY1 适配器：装配路径并持有 LogicApi 单例
      + 命令接口层
          // 命令行解析与命令分派（Y0 交互）
        + 代码元素
          + backend_logic_y2_1\interface\commander.py      // Commander.parse：（cmd,pos,key,remainder）
          + backend_logic_y2_1\interface\logicY0.py         // CMDLogicY0.dispatch/execute/init_help
          + cmd-logicy0\semantic\logicY0.py                 // 命令行版本入口（同构）
          + cmd-logicy0\commander.py
      + 前端展示层
          // React 图形界面：布局渲染 + 全局状态 + API 客户端
        + 代码元素
          + forend-logicy2-1\src\App.js                     // 挂载 DeductionProvider + ProofInterface
          + forend-logicy2-1\src\components\ProofInterface.jsx  // 三栏布局与 /read 数据装配、命令提交
          + forend-logicy2-1\src\components\ApplicationPanel.jsx // 推理规则应用：动态组装 payload -> 端点
          + forend-logicy2-1\src\components\ProofArea.jsx        // 证明步骤展示、/cp2tp 选区换算
          + forend-logicy2-1\src\components\{AssumptionPanel,AuxiliaryItemPanel,VariablePanel,TheoremAxiomPanel}.jsx
          + forend-logicy2-1\src\contexts\DeductionContext.jsx   // 选中结论/当前模式/推理参数
          + forend-logicy2-1\src\api.js                     // axios 实例
          + forend-logicy2-1\src\config.js                  // API_BASE_URL

    + 业务层
        // 推理业务逻辑，不依赖具体呈现方式
      + 应用服务层
          // 推理操作聚合入口：把“用户操作”翻译为“环境更新”用例
        + 代码元素
          + backend_logic_y2_1\semantic\logic_api.py   // LogicApi：deduce/instance/introduce/select/use/qed
                                                       //   /bra/conclude/eqrepl/write/set_rules/predefine/switch_line
      + 解析层
          // 文本 -> 语法树
        + 词法层
            // 正则分词，输出 (symbol,value) token 序列
          + 代码元素
            + backend_logic_y2_1\words.py              // Word.look_one/parse_all；shift/union
            + backend_logic_y2_1\semantic\line.py      // LineParser.patterns/lexical（词法规则与保留字）
        + 语法层
            // CFG 分析与 LR(1) 移入-规约；含歧义消解（优先级/结合性）
          + 代码元素
            + backend_logic_y2_1\grammar.py            // Grammar：NONE/FIRST/FOLLOW/LC 求解、from_file
            + backend_logic_y2_1\lrparser.py           // LR1Item/LR1ItemSet/LR1Table(ambiguity)/LRParser
            + backend_logic_y2_1\semantic\line.py      // LineParser.build_tree/parse
      + 语义层
          // 语法树 -> 带语义属性（类型、自由/约束变元、出现位置）的树；并驱动环境变更
        + 静态分析层
            // 变量名、类型推断、自由/约束变元求解
          + 代码元素
            + backend_logic_y2_1\semantic\line.py      // TermAnalyzer.solve / solve_var / solve_type
                                                       //   / solve_varT_list / solve_var_names / sort_deduce
        + 类型系统层
            // Sort 类型代数：复合类型、子类型判定、函数与元组类型
          + 代码元素
            + backend_logic_y2_1\semantic\sort.py      // Sort/SortTuple/Func；is_super/from_str/to_words
        + 环境层
            // 推理环境状态容器：变量/公理/定理/结论/假设/规则/模式
          + 代码元素
            + backend_logic_y2_1\semantic\context.py   // Context（read/add_var/append_conclusion/assume/proof/qed
                                                       //   /conclude_start/get_rule）；Var；模式常量 MODE
            + backend_logic_y2_1\semantic\line.py      // Switcher.switch（按产生式驱动 add_var/proof/assert/qed/append）
        + 作用域层
            // 域（作用域/假设域）建模：域栈与域区间树；支持“假设域”演进
          + 代码元素
            + backend_logic_y2_1\semantic\domain.py    // Node/ListDomain：step_in/step_out/get_domain/get_domain_tree
        + 转换层
            // 符号级/语法级变换（仅依赖语法结构，不依赖附加语义）
          + 代码元素
            + backend_logic_y2_1\semantic\convert.py   // TermConverter：regular_instance/regular_fillin/
                                                       //   regular_deduce/equal_replace/regular_replace/rename/
                                                       //   introduce/on_bracket/off_bracket/conclude/line2term
      + 规则层
          // 推理规则的装载与表示
        + 代码元素
          + backend_logic_y2_1\semantic\ruler.py       // RuleSet：解析 {p1,p2} |- q

    + 基础设施层
        // 与业务无关的通用支撑
      + 数据结构层
          // 树/图/集合方程组：语法树、解析图、域树、类型关系求解
        + 代码元素
          + Structure\tree.py             // Tree（ABTree 的基类）：copy_subtree/common_ancestors/leaf 区间
          + Structure\graph.py            // DiGraph（有向图）
          + Structure\datavisual.py       // VTree/VDiGraph 可视化
          + backend_logic_y2_1\abtree.py  // ABTree：make_data/deduce/reduce/movein/copy/copy_subtree/equal/totext
          + backend_logic_y2_1\utils\mathtools.py  // SetEquation：集合方程组迭代求解（FIRST/FOLLOW/闭包）
      + 资源定位层
          // 资源相对路径 -> 绝对路径
        + 代码元素
          + backend_logic_y2_1\resource\resource_service.py  // ResourceService.get
      + 工具层
          // 无业务语义的通用工具
        + 代码元素
          + backend_logic_y2_1\utils\comcopy.py       // basiccopy（复合类型深拷贝）
          + backend_logic_y2_1\utils\line_reader.py   // LineReader（非空行迭代器）
          + backend_logic_y2_1\utils\printer.py       // Printer（环境/表格式化打印）
          + backend_logic_y2_1\utils\list_algorithm.py// ListAlgorithms（字符/片段索引换算）
          + backend_logic_y2_1\utils\serialize.py     // JsonSerializer
          + backend_logic_y2_1\utils\tostring.py      // toString（元组/列表/集合字符串化）

  + 测试层
      // 对系统各模块的验证
    + 代码元素
      + backend_logic_y2_1\test.py                       // 测试与运行入口（路径装配、选择用例运行）
      + backend_logic_y2_1\test\test_parser.py
      + backend_logic_y2_1\test\test_analyser.py
      + backend_logic_y2_1\test\test_sort.py
      + backend_logic_y2_1\test\test_converter.py        // + test_term_converter.py
      + backend_logic_y2_1\test\test_deduce.py           // + test_eq_replace.py / test_bracket.py
      + backend_logic_y2_1\test\test_axiom.py
      + backend_logic_y2_1\test\test_context_vert.py
      + backend_logic_y2_1\test\test_commander.py        // + test_logicY0.py / test_char_pos_to_token_pos.py
      + forend-logicy2-1\src\App.test.js
```

---

## 关联

> 元素均取自上文；把孤立的层与代码组织成有机系统。

**1) 交互：前后端闭环（请求-处理-刷新）**
```
frontend 组件 (ProofInterface / ApplicationPanel / ProofArea)
  -> api.js (axios) -> HTTP
  -> interface\logic_flask.py:端点
  -> interface\logic_y1.py:GUILogicY1.logic_api (LogicApi)
  -> 业务层（应用服务层 -> 解析/语义/转换/环境层）
  -> 返回 env.mode
frontend 再 -> /read -> Context.read -> 各 Panel 重绘
```
- 前端各操作与端点映射：`write_line`←命令提交；`use`←应用假设/公理；`select`←添加辅助项；`ApplicationPanel` 按 `selectedRule` 动态 POST `/instance|/deduce|/eqrepl|/bra|/qed`；`ProofArea`→`/cp2tp`。
- 契约耦合：`interface\interface.yaml` 定义端点，前端按契约调用。

**2) 依赖：解析链（链状）**
```
words.Word(词法层) -> semantic\line.LineParser.lexical
  -> lrparser.LRParser.parse  [依赖 grammar.Grammar + LR1Table(优先级/结合性)]
  -> abtree.ABTree(构建语法树)
```
说明：`LR1Table` 构建时经 `utils\mathtools.SetEquation` 求解 FIRST/FOLLOW/闭包；`Grammar.solve_LC` 生成正则文法。

**3) 依赖：语义链（链状）**
```
LineParser.parse -> semantic\line.TermAnalyzer.solve
      -> solve_var_names / solve_type / solve_varT_list / solve_var / sort_deduce
        -> semantic\sort.Sort(类型判定 is_super) + semantic\context.Context.get_var(类型来源)
```

**4) 调用：推理操作链（统一的“生成新行文本->重解析->改环境”）**
```
LogicApi.<op> (应用服务层)
  -> semantic\convert.TermConverter.<op>   // 产出新行文本（regular_* / equal_replace / on|off_bracket / conclude）
  -> LogicApi.switch_line
       -> semantic_parse (LineParser.parse -> TermAnalyzer.solve)
       -> semantic\line.Switcher.switch -> semantic\context.Context 状态更新
```
代表：`deduce` 经 `regular_deduce`（模板填充 + 精确匹配）产出行；`conclude` 经 `TermConverter.conclude` 合成蕴涵式。

**5) 时序：环境状态机（网状 + 时序）**
```
Global --theorem/lemma--> Proof --qed(结论与待证匹配)--> Global
Global --assert--> Assert --;--> Global
Proof 内：assume 入栈 -> 结论追加 -> (可选 conclude 归结)
```
载体：`Context.proof/qed/assert_/end_assert` + `Switcher.switch`（`<theorem>`/`<qed>`/`<assert>`/`<end>` 产生式）。

**6) 数据：规则与预定义装载（配置 -> 运行态）**
```
resource\first-order\rules.txt -> semantic\ruler.RuleSet
  -> LogicApi.set_rules (逐条 LineParser.parse 模板) -> Context.rules
  -> deduce 时 Context.get_rule -> convert.regular_deduce 匹配前提
resource\test\sentences\predefine2.txt -> LogicApi.predefine -> semantic_parse -> switch
```

**7) 类型：类继承与装配（树状）**
```
semantic\sort.Sort  <|-- Func / SortTuple
context.Context.globals[..]/locals[..] : Var(含 Sort)
abtree.ABTree  <|-- Structure\tree.Tree
```

**8) 演进关联（规划 / 未接通）**
- `semantic\domain.ListDomain`（作用域层）**尚未接入** `Context`：README 描述的“假设域栈 / assumption domain”为其目标，属增量开发的预留接口。
- `backend_logic_y2`（旧分支）为 `backend_logic_y2_1` 的基线；`cmd-logicy0` 为命令交互前身（Y0），核心理念同构但带独立 `Structure` 副本与 `semantic\logicY0.py` 入口。
- 共享库 `Structure` 被后台（`abtree`/`lrparser`）与命令行前端共同依赖。

**9) 面向增量开发的上下文入口（信息充分且不冗余）**
- 加“解析/文法”特性 → 看 解析层（`grammar.py`/`lrparser.py`/`words.py`/`line.py`）+ 资源层`grammars`。
- 加“推理操作” → 看 应用服务层`logic_api.py` + 转换层`convert.py` + 环境层`context.py` + `interface.yaml`/`logic_flask.py`。
- 加“类型推断” → 看 `sort.py` + `line.py:TermAnalyzer` + 环境层`Var`。
- 加“作用域/假设域” → 看 `domain.py` + `README.md` + `issues\applying_rules.md`。
```
