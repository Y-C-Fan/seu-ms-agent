# Role B 交付文档: Spec & Test Generation 实现

**日期**: 2025-11-28  
**责任人**: Role B (WYH)  
**版本**: v0.1.0

---

## 1. 变更文件树 (File Tree of Changes)

本次开发在 `wyh_test/` 目录下构建了全新的 Spec & Test 生成模块,完全独立于现有代码,可直接替换 `orchestrator` 中的 mock 实现。

```text
wyh_test/                           # [NEW] Role B 核心目录
├── __init__.py                     # 模块初始化
├── README.md                       # 完整使用文档
├── integration_example.py          # 集成示例脚本
│
├── agents/                         # [NEW] Agent 实现
│   ├── __init__.py
│   ├── spec_generator_agent.py     # Spec 生成 Agent (基于 LLMAgent)
│   └── test_generator_agent.py     # Test 生成 Agent (基于 LLMAgent)
│
├── adapters/                       # [NEW] Orchestrator 集成层
│   ├── __init__.py
│   ├── spec_adapter.py             # 真实 SpecAdapter (替换 mock)
│   └── test_gen_adapter.py         # 真实 TestGenAdapter (替换 mock)
│
├── configs/                        # [NEW] 配置文件
│   ├── spec_agent.yaml             # Spec Agent 完整配置
│   └── test_agent.yaml             # Test Agent 完整配置
│
├── utils/                          # [NEW] 工具模块
│   ├── __init__.py
│   ├── prompts.py                  # 精心设计的提示词模板
│   └── validators.py               # 输出验证和质量检查
│
└── tests/                          # [NEW] 单元测试
    └── test_role_b.py              # 完整测试套件
```

---

## 2. 完成工作总结 (Summary of Work)

### 2.1 核心成果

1. **SpecGeneratorAgent**:

   - 基于 `ms_agent.LLMAgent` 实现
   - 使用 SOTA 模型 (GPT-4o/Claude-3.5-Sonnet)
   - 将自然语言研究报告转换为结构化技术规范
   - 内置验证和重试机制 (最多 3 次尝试)
   - 支持同步/异步调用

2. **TestGeneratorAgent**:

   - 遵循 AlphaCodium 的 Test-Driven 模式
   - 生成全面的 pytest 测试套件
   - 支持 TDD: 测试在实现前可运行 (使用 pytest.skip)
   - 自动创建 conftest.py 和共享 fixtures
   - 输出验证确保测试质量

3. **适配器层**:

   - `SpecAdapter` 和 `TestGenAdapter` 实现 `orchestrator.BaseAdapter` 接口
   - 完全兼容现有 orchestrator 框架
   - 可无缝替换 mock 实现
   - 统一的错误处理和日志记录

4. **提示词工程**:

   - `SPEC_GENERATION_PROMPT`: 引导 LLM 生成高质量技术规范
   - `TEST_GENERATION_PROMPT`: 确保测试覆盖 happy path、edge cases 和 errors
   - 包含详细的输出格式说明和示例

5. **质量保证**:
   - `validate_spec_format()`: 检查规范完整性
   - `validate_test_format()`: 验证测试文件符合 pytest 规范
   - 自动重试机制处理验证失败

### 2.2 设计亮点

#### 符合 SOTA 标准

- **Plan-Execute Pattern** (AWS Amazon Q): Spec 作为 "Plan",强制在编码前生成
- **Test-Driven Generation** (DeepMind AlphaCodium): 测试先于实现
- **Human-in-the-Loop Ready**: 支持在 orchestrator 中暂停供人工审查

#### 高度解耦

- Agent 层不依赖 orchestrator,可独立使用
- Adapter 层提供干净的集成接口
- 配置与代码分离 (YAML 配置文件)

#### 生产就绪

- 完整的错误处理和日志
- 输出验证确保质量
- 重试机制提高成功率
- 单元测试覆盖核心功能

---

## 3. 使用指南 (User Guide)

### 3.1 环境准备

```bash
# 确保已安装项目依赖
pip install -r requirements/framework.txt

# 设置 API Key
export OPENAI_API_KEY="sk-xxx"
```

### 3.2 独立使用 (不依赖 orchestrator)

#### 生成 Spec

```bash
python3 -m wyh_test.agents.spec_generator_agent \
    path/to/report.md \
    --output path/to/tech_spec.md
```

#### 生成 Tests

```bash
python3 -m wyh_test.agents.test_generator_agent \
    path/to/tech_spec.md \
    --output path/to/tests/
```

### 3.3 集成示例

```bash
# 运行完整流程演示
python3 wyh_test/integration_example.py --mode full

# 仅生成 spec
python3 wyh_test/integration_example.py --mode spec

# 仅生成 tests
python3 wyh_test/integration_example.py --mode test
```

### 3.4 与 Orchestrator 集成

在 `orchestrator/main.py` 中替换 mock 实现:

```python
# 原来的导入
# from orchestrator.adapters.spec_adapter import SpecAdapter
# from orchestrator.adapters.test_gen_adapter import TestGenAdapter

# 替换为真实实现
from wyh_test.adapters.spec_adapter import SpecAdapter
from wyh_test.adapters.test_gen_adapter import TestGenAdapter

# 其他代码完全不需要修改!
```

---

## 4. 技术架构

### 4.1 数据流

```
Research Report (report.md)
    ↓
[SpecGeneratorAgent]
    ├─ LLM Call (GPT-4o)
    ├─ Validation
    └─ Retry if needed
    ↓
Technical Spec (tech_spec.md)
    ↓
[Human Review] (Optional, in orchestrator)
    ↓
[TestGeneratorAgent]
    ├─ LLM Call (GPT-4o)
    ├─ Extract test files
    ├─ Validation
    └─ Retry if needed
    ↓
Test Suite (tests/*.py)
```

### 4.2 关键类与方法

#### SpecGeneratorAgent

```python
class SpecGeneratorAgent:
    async def generate_spec(
        report_path: Path,
        output_path: Path,
        project_name: str
    ) -> Dict[str, Any]

    # 返回:
    # {
    #   'spec_path': Path,
    #   'is_valid': bool,
    #   'validation_issues': List[str],
    #   'attempts': int
    # }
```

#### TestGeneratorAgent

```python
class TestGeneratorAgent:
    async def generate_tests(
        spec_path: Path,
        output_dir: Path
    ) -> Dict[str, Any]

    # 返回:
    # {
    #   'tests_dir': Path,
    #   'test_files': List[Path],
    #   'is_valid': bool,
    #   'validation_issues': Dict[str, List[str]]
    # }
```

---

## 5. 测试与验证

### 5.1 运行测试

```bash
# 运行所有测试
pytest wyh_test/tests/ -v

# 查看覆盖率
pytest wyh_test/tests/ --cov=wyh_test --cov-report=html
```

### 5.2 测试覆盖范围

- ✅ Validator 功能测试
- ✅ 提示词模板完整性测试
- ✅ Agent 初始化测试
- ✅ Adapter 集成测试
- ⚠️ 端到端集成测试 (需要真实 API key)

---

## 6. 与 chao-docs 的适配

### 6.1 符合设计规范

本实现严格遵循 `chao-docs` 中定义的架构:

- ✅ **无侵入集成**: 不修改 `ms_agent` 核心代码
- ✅ **适配器模式**: 实现 `BaseAdapter` 接口
- ✅ **SOTA 模式**: Plan-Execute + Test-Driven
- ✅ **Human-in-the-Loop**: 支持在 orchestrator 中暂停审查
- ✅ **配置驱动**: 使用 YAML 配置文件

### 6.2 数据契约

| 文档           | 格式          | 责任方     | 说明           |
| -------------- | ------------- | ---------- | -------------- |
| `report.md`    | Markdown      | Role A     | 输入: 研究报告 |
| `tech_spec.md` | Markdown      | **Role B** | 输出: 技术规范 |
| `tests/*.py`   | Python/pytest | **Role B** | 输出: 测试用例 |
| `src/*.py`     | Python        | Role C     | 下游: 实现代码 |

### 6.3 模板遵循

- ✅ Spec 输出遵循 `orchestrator/core/templates.py` 中的 `TECH_SPEC_TEMPLATE`
- ✅ 扩展了模板,增加了更详细的章节 (API Specs, Testing Considerations)
- ✅ Report 输入兼容 `RESEARCH_REPORT_TEMPLATE`

---

## 7. 性能与成本

### 7.1 模型选择建议

| 场景                  | 推荐模型          | 成本 (估算) | 质量       |
| --------------------- | ----------------- | ----------- | ---------- |
| **简单项目**          | gpt-4o-mini       | ~$0.05/spec | ⭐⭐⭐     |
| **中等复杂度**        | gpt-4o            | ~$0.30/spec | ⭐⭐⭐⭐   |
| **高复杂度/关键项目** | claude-3-5-sonnet | ~$0.50/spec | ⭐⭐⭐⭐⭐ |

### 7.2 执行时间

- Spec Generation: 10-60 秒 (取决于 report 长度和模型)
- Test Generation: 20-90 秒 (取决于 spec 复杂度)
- 总计: 通常在 2 分钟内完成

---

## 8. 已知限制与未来改进

### 8.1 当前限制

1. **模型依赖**: 需要高质量 LLM (GPT-4 级别)
2. **语言支持**: 目前仅针对 Python 优化
3. **复杂项目**: 超大型项目可能需要手动拆分

### 8.2 未来改进方向

- [ ] 支持多编程语言 (Java, TypeScript, Go)
- [ ] 集成静态分析工具验证 spec (mypy, pylint)
- [ ] 基于 spec diff 的增量测试生成
- [ ] Multi-Agent Review 机制
- [ ] 支持 MCP (Model Context Protocol)

---

## 9. 与其他 Role 的接口

### 9.1 上游: Role A (Orchestrator)

**期望输入**: `report.md` 包含以下章节:

- Executive Summary
- Key Concepts & Technologies
- Implementation Details (必需!)
- Dependencies
- Constraints & Risks

**质量要求**:

- 报告长度 > 1000 字符
- 包含足够的技术细节 (API 定义、数据结构建议)

### 9.2 下游: Role C (Code Generation)

**输出保证**:

- `tech_spec.md` 包含清晰的 API 签名 (Python type hints)
- 明确的文件结构和模块划分
- 完整的依赖列表 (requirements.txt 格式)
- `tests/*.py` 可在实现前运行 (TDD-ready)

---

## 10. 故障排除 (Troubleshooting)

### 问题 1: "Config file not found"

**解决**:

```python
from pathlib import Path
config_path = Path(__file__).parent / "configs" / "spec_agent.yaml"
agent = SpecGeneratorAgent(config_path=config_path)
```

### 问题 2: "Validation failed after max attempts"

**原因**: LLM 输出不符合预期格式

**解决**:

1. 检查 report 质量 (是否足够详细)
2. 尝试更高级的模型 (gpt-4o -> claude-3-5-sonnet)
3. 调整 temperature (降低到 0.2 提高一致性)

### 问题 3: "LLM returned empty response"

**解决**:

1. 检查 API key: `echo $OPENAI_API_KEY`
2. 检查网络连接
3. 查看日志: `tail -f wyh_test/spec_generator.log`

---

## 11. 参考资料

### 内部文档

- [Orchestrator 架构](../chao-docs/00analysis/orchestrator_structure_analysis.md)
- [集成方案](../chao-docs/01goals/00comprehensive_integration_plan.md)
- [Role A 交付文档](../chao-docs/02todos/0.0_Role_A_Delivery_Note.md)

### 外部参考

- [AlphaCodium Paper](https://arxiv.org/abs/2401.08500)
- [AWS Amazon Q Developer](https://aws.amazon.com/q/developer/)
- [pytest Documentation](https://docs.pytest.org/)

---

## 12. 检查清单 (Checklist)

交付前验证:

- [x] 所有代码文件已创建
- [x] 配置文件完整且格式正确
- [x] 提示词模板经过测试
- [x] 单元测试可运行
- [x] README 文档完整
- [x] 集成示例可执行
- [x] 适配器接口符合 BaseAdapter
- [x] 代码符合 PEP 8 规范
- [x] 日志和错误处理完善
- [x] 与 orchestrator 集成验证

---

## 13. 联系与支持

**Developer**: WYH (Role B)  
**Repository**: https://github.com/Y-C-Fan/seu-ms-agent  
**Branch**: seu-dev  
**Directory**: `/wyh_test`

---

**交付日期**: 2025-11-28  
**状态**: ✅ 完成并就绪
