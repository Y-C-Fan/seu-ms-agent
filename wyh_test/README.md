# Role B: Spec & Test Generation Module

**Role**: Glue Layer between Research (Role A) and Coding (Role C)  
**Version**: 0.1.0  
**Author**: WYH (Role B Developer)

## 概述

本模块实现了 Research-to-Code 流水线中的关键"胶水层",负责将研究报告转换为可执行的技术规范和测试用例。这是连接知识获取和代码实现的桥梁。

### 核心组件

1. **SpecGeneratorAgent**: 将 `report.md` 转换为结构化的 `tech_spec.md`
2. **TestGeneratorAgent**: 基于 `tech_spec.md` 生成全面的 pytest 测试套件
3. **适配器层**: 与 orchestrator 框架无缝集成

### 设计理念

- **SOTA 模式**: 遵循 AlphaCodium 的 Test-Driven Development 模式
- **高质量模型**: 使用 GPT-4o / Claude-3.5-Sonnet 进行关键架构决策
- **验证机制**: 内置输出验证和重试逻辑
- **无侵入集成**: 通过适配器模式与现有系统对接

---

## 目录结构

```
wyh_test/
├── __init__.py
├── agents/                      # Agent 实现
│   ├── spec_generator_agent.py  # Spec 生成 Agent
│   └── test_generator_agent.py  # Test 生成 Agent
├── adapters/                    # Orchestrator 集成层
│   ├── spec_adapter.py          # Spec Adapter (替换 mock)
│   └── test_gen_adapter.py      # Test Gen Adapter (替换 mock)
├── configs/                     # 配置文件
│   ├── spec_agent.yaml          # Spec Agent 配置
│   └── test_agent.yaml          # Test Agent 配置
├── utils/                       # 工具函数
│   ├── prompts.py               # 提示词模板
│   └── validators.py            # 输出验证器
├── tests/                       # 单元测试
│   └── test_role_b.py
└── README.md                    # 本文件
```

---

## 快速开始

### 环境要求

```bash
# Python 3.8+
pip install -r requirements/framework.txt

# 设置 API Key
export OPENAI_API_KEY="sk-xxx"
# 或者使用其他模型服务
# export DASHSCOPE_API_KEY="xxx"
```

### 独立使用

#### 1. 生成技术规范

```bash
# 从 report.md 生成 tech_spec.md
python3 -m wyh_test.agents.spec_generator_agent \
    /path/to/report.md \
    --output /path/to/output/tech_spec.md \
    --project-name "My Project"
```

**示例代码:**

```python
from pathlib import Path
from wyh_test.agents.spec_generator_agent import SpecGeneratorAgent

# 初始化 Agent
agent = SpecGeneratorAgent(model='gpt-4o')

# 生成 Spec
result = agent.generate_spec_sync(
    report_path=Path('workspace/run_xxx/report.md'),
    output_path=Path('workspace/run_xxx/tech_spec.md')
)

print(f"Spec generated: {result['spec_path']}")
print(f"Valid: {result['is_valid']}")
```

#### 2. 生成测试用例

```bash
# 从 tech_spec.md 生成 pytest 测试
python3 -m wyh_test.agents.test_generator_agent \
    /path/to/tech_spec.md \
    --output /path/to/tests/
```

**示例代码:**

```python
from pathlib import Path
from wyh_test.agents.test_generator_agent import TestGeneratorAgent

# 初始化 Agent
agent = TestGeneratorAgent(model='gpt-4o')

# 生成测试
result = agent.generate_tests_sync(
    spec_path=Path('workspace/run_xxx/tech_spec.md'),
    output_dir=Path('workspace/run_xxx/tests')
)

print(f"Generated {len(result['test_files'])} test files")
for tf in result['test_files']:
    print(f"  - {tf.name}")
```

---

## 与 Orchestrator 集成

### 替换 Mock 实现

本模块的适配器可以直接替换 `orchestrator` 中的 mock 实现。

#### 方法 1: 修改 orchestrator/main.py

```python
# 在 orchestrator/main.py 中

# 原来的 mock 导入
# from orchestrator.adapters.spec_adapter import SpecAdapter
# from orchestrator.adapters.test_gen_adapter import TestGenAdapter

# 替换为真实实现
from wyh_test.adapters.spec_adapter import SpecAdapter
from wyh_test.adapters.test_gen_adapter import TestGenAdapter

# 其他代码保持不变,适配器接口完全兼容
```

#### 方法 2: 动态替换 (推荐)

```python
# 在 orchestrator 的配置文件中指定适配器路径
import sys
from pathlib import Path

# 添加 wyh_test 到 Python 路径
wyh_path = Path(__file__).parent.parent / "wyh_test"
sys.path.insert(0, str(wyh_path))

# 然后正常导入
from wyh_test.adapters import SpecAdapter, TestGenAdapter
```

### 完整流程示例

```python
from orchestrator.core.config import OrchestratorConfig
from orchestrator.core.workspace import WorkspaceManager
from orchestrator.adapters.doc_research_adapter import DocResearchAdapter
from wyh_test.adapters import SpecAdapter, TestGenAdapter

# 1. 初始化
config = OrchestratorConfig.load_from_env()
workspace = WorkspaceManager.create()

# 2. Phase 1: Research (使用现有的 adapter)
research_adapter = DocResearchAdapter(config, workspace)
report_result = research_adapter.run(
    file_paths=['requirements.pdf'],
    urls=[]
)
report_path = report_result['report_path']

# 3. Phase 2: Spec Generation (使用 Role B)
spec_adapter = SpecAdapter(config, workspace)
spec_result = spec_adapter.run(report_path)
spec_path = spec_result['spec_path']

# 4. Phase 2.5: Human Review (可选)
input(f"Please review {spec_path}, press Enter to continue...")

# 5. Phase 3: Test Generation (使用 Role B)
test_adapter = TestGenAdapter(config, workspace)
test_result = test_adapter.run(spec_path)
tests_dir = test_result['tests_dir']

print(f"✓ Tests generated in: {tests_dir}")

# 6. Phase 4: Coding (Role C) - 预留接口
# code_adapter = CodeAdapter(config, workspace)
# code_result = code_adapter.run(spec_path, tests_dir)
```

---

## 配置说明

### Spec Agent 配置 (`configs/spec_agent.yaml`)

```yaml
llm:
  model: "gpt-4o" # 或 claude-3-5-sonnet-20241022
  temperature: 0.3 # 较低温度确保一致性
  max_tokens: 8000 # Spec 可能很长

system_prompt: |
  You are a Senior System Architect...

output:
  validation:
    enabled: true # 启用输出验证

retry:
  max_attempts: 3 # 验证失败时重试次数
```

### Test Agent 配置 (`configs/test_agent.yaml`)

```yaml
llm:
  model: "gpt-4o"
  temperature: 0.4 # 稍高温度鼓励创造性测试用例
  max_tokens: 12000 # 测试套件可能非常长

testing:
  framework: "pytest"
  coverage:
    target: 90 # 目标覆盖率
```

---

## 高级特性

### 1. 自定义提示词

```python
from wyh_test.agents.spec_generator_agent import SpecGeneratorAgent

agent = SpecGeneratorAgent()

# 修改系统提示词
agent.config.system_prompt = "You are an expert in domain XYZ..."

result = agent.generate_spec_sync(...)
```

### 2. 验证与调试

```python
from wyh_test.utils.validators import validate_spec_format

spec_content = Path('tech_spec.md').read_text()
is_valid, issues = validate_spec_format(spec_content)

if not is_valid:
    print("Validation issues found:")
    for issue in issues:
        print(f"  - {issue}")
```

### 3. 提取代码块

```python
from wyh_test.utils.validators import extract_code_blocks

spec_content = Path('tech_spec.md').read_text()
code_blocks = extract_code_blocks(spec_content)

for block in code_blocks:
    print(f"Language: {block['language']}")
    print(f"Code: {block['code'][:100]}...")
```

---

## 测试

### 运行单元测试

```bash
# 运行所有测试
pytest wyh_test/tests/ -v

# 运行特定测试类
pytest wyh_test/tests/test_role_b.py::TestValidators -v

# 显示覆盖率
pytest wyh_test/tests/ --cov=wyh_test --cov-report=html
```

### 集成测试

```bash
# 端到端测试 (需要真实 API key)
cd wyh_test/tests
python3 test_integration.py
```

---

## 故障排除

### 问题 1: "Config file not found"

**原因**: 配置文件路径不正确。

**解决**:

```python
from pathlib import Path

config_path = Path(__file__).parent / "configs" / "spec_agent.yaml"
agent = SpecGeneratorAgent(config_path=config_path)
```

### 问题 2: "Validation failed"

**原因**: 生成的输出不符合预期格式。

**解决**:

- 检查 `validation_issues` 列表了解具体问题
- 增加 `max_attempts` 允许更多重试
- 调整提示词使其更明确

### 问题 3: "LLM returned empty response"

**原因**: API 调用失败或模型超时。

**解决**:

- 检查 API key 是否正确
- 检查网络连接
- 增加 `max_tokens` 限制
- 查看 agent 日志文件

---

## 架构设计原则

### 1. 单一职责

- **SpecGeneratorAgent**: 只负责 Spec 生成
- **TestGeneratorAgent**: 只负责 Test 生成
- **Adapters**: 只负责与 orchestrator 对接

### 2. 依赖倒置

- Agents 依赖于 `ms_agent.LLMAgent` 抽象
- Adapters 实现 `orchestrator.BaseAdapter` 接口

### 3. 开闭原则

- 对扩展开放: 可以添加新的 Agent
- 对修改封闭: 现有代码无需修改

### 4. 测试驱动

- 所有 Agent 都有对应的单元测试
- Validators 确保输出质量

---

## 与其他 Role 的协作

### 上游: Role A (Orchestrator)

**输入**: `report.md` (来自 DocResearch 或 DeepResearch)

**依赖**:

- Report 必须包含足够的技术细节
- Report 格式应遵循 `orchestrator/core/templates.py` 中的 `RESEARCH_REPORT_TEMPLATE`

### 下游: Role C (Code Generation)

**输出**:

- `tech_spec.md` (详细的技术规范)
- `tests/` 目录 (TDD-ready 的 pytest 测试)

**保证**:

- Spec 包含清晰的 API 签名和数据结构
- Tests 可以在实现前运行 (使用 `pytest.skip()`)
- Tests 覆盖 happy path、edge cases 和 error handling

---

## 性能优化建议

1. **模型选择**:

   - 对于简单项目: `gpt-4o-mini` 或 `claude-3-haiku`
   - 对于复杂架构: `gpt-4o` 或 `claude-3-5-sonnet`

2. **批处理**:

   - 如果生成多个模块的 tests,可以并行调用 Agent

3. **缓存**:
   - 对于相同的 report,可以缓存生成的 spec

---

## 未来扩展

### 计划中的特性

- [ ] 支持多语言规范 (Java, TypeScript, etc.)
- [ ] 集成静态分析工具验证 spec
- [ ] 基于 spec diff 增量生成 tests
- [ ] 支持 MCP (Model Context Protocol) 集成
- [ ] Web UI 用于交互式 spec 编辑

### 实验性特性

- **Spec Refinement Loop**: 基于测试结果反向优化 spec
- **Multi-Agent Review**: 多个 Agent 协作 review spec 质量

---

## 贡献指南

如果你想改进 Role B 模块:

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/improvement`
3. 编写代码并通过测试: `pytest wyh_test/tests/`
4. 提交 PR 并描述改动

---

## 参考资料

### 学术论文

- **AlphaCodium**: "Code Generation with Iterative Refinement"
- **SWE-bench**: "Evaluating LLMs on Real-World Software Engineering"

### 行业实践

- **AWS Amazon Q Developer**: Plan-Execute pattern
- **OpenAI O1**: Human-in-the-Loop reasoning
- **DeepMind**: Test-driven AI systems

### 相关文档

- [Orchestrator 架构分析](../chao-docs/00analysis/orchestrator_structure_analysis.md)
- [集成方案](../chao-docs/01goals/00comprehensive_integration_plan.md)
- [赛题要求](../chao-docs/01goals/赛题.md)

---

## 许可证

本模块遵循项目主仓库的许可证。

---

## 联系方式

**Role B Developer**: WYH  
**项目地址**: https://github.com/Y-C-Fan/seu-ms-agent  
**分支**: seu-dev

---

**最后更新**: 2025-11-28
