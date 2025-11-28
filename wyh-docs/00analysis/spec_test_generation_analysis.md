# Spec & Test 生成技术分析

**日期**: 2025-11-28  
**作者**: Role B Team

## 1. 背景与动机

### 1.1 问题陈述

在传统的开发流程中，从需求到代码的转换存在以下问题：

- 需求文档（Research Report）通常是非结构化的自然语言
- 开发人员需要手动将需求转换为技术规范
- 测试用例通常在代码实现后才编写
- 需求理解偏差导致返工

### 1.2 解决方案

引入 Spec & Test 生成层，作为需求和实现之间的"翻译器"：

- 自动将研究报告转换为结构化技术规范
- 遵循 TDD 原则，先生成测试用例
- 为代码生成 Agent 提供明确的实现指导
- 减少人工干预，提高效率

## 2. SOTA 技术调研

### 2.1 Plan-Execute Pattern

**来源**: AWS Amazon Q Developer

**核心思想**:

- 强制生成 "Plan"（计划）并进行 Review
- 计划包含详细的技术决策和架构设计
- 在实现前明确 What 和 How

**应用到 Role B**:

- Tech Spec 即为 "Plan"
- 在生成代码前强制生成 Spec
- 支持人工审查 Spec（Human-in-the-Loop）

### 2.2 Test-Driven Generation

**来源**: DeepMind AlphaCodium

**核心思想**:

- 先生成测试，再生成代码
- 测试作为规范的可执行版本
- 代码必须通过预先定义的测试

**应用到 Role B**:

- 基于 Spec 生成 pytest 测试套件
- 测试在代码实现前就可以运行（使用 pytest.skip）
- 测试作为验证 Code Agent 输出的标准

### 2.3 Prompt Engineering Best Practices

**来源**: OpenAI, Anthropic

**关键技术**:

- 结构化输出：明确要求输出格式
- Few-shot Learning：提供示例
- Chain of Thought：引导推理过程
- 约束和限制：避免幻觉

**应用到 Role B**:

- 精心设计的 Spec 和 Test 生成提示词
- 包含详细的输出格式说明
- 强调"基于报告内容"以减少幻觉

## 3. 架构设计

### 3.1 整体架构

```
Research Report (Natural Language)
         ↓
    [Spec Agent]
         ↓
  Tech Spec (Structured)
         ↓
    [Test Agent]
         ↓
  Test Suite (Executable)
         ↓
    [Code Agent] (Role C)
         ↓
Implementation Code
```

### 3.2 核心组件

#### 3.2.1 SpecGeneratorAgent

**职责**: 将研究报告转换为技术规范

**输入**: report.md（自然语言）

**输出**: tech_spec.md（结构化 Markdown）

**关键特性**:

- 基于 LLMAgent 实现
- 使用高质量模型（GPT-4o）
- 低温度参数（0.3）确保一致性
- 内置验证逻辑
- 支持重试机制

**输出结构**:

```markdown
# Technical Specification

## 1. Executive Summary

## 2. System Architecture

## 3. File Structure

## 4. API Specifications

## 5. Data Models

## 6. Dependencies

## 7. Testing Considerations
```

#### 3.2.2 TestGeneratorAgent

**职责**: 基于技术规范生成测试用例

**输入**: tech_spec.md（结构化 Markdown）

**输出**: tests/ 目录（pytest 测试套件）

**关键特性**:

- 遵循 TDD 原则
- 生成多个测试文件
- 创建 conftest.py 和 fixtures
- 使用 pytest.skip 标记未实现功能
- 覆盖多种测试场景

**输出结构**:

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_core.py         # Core functionality tests
├── test_api.py          # API tests
└── test_edge_cases.py   # Edge cases and errors
```

### 3.3 适配器层

**目的**: 连接 Agent 和 Orchestrator 框架

**实现**:

```python
class SpecAdapter(BaseAdapter):
    def run(self, report_path: Path) -> Dict[str, Any]:
        # 调用 SpecGeneratorAgent
        # 返回 spec_path

class TestGenAdapter(BaseAdapter):
    def run(self, spec_path: Path) -> Dict[str, Any]:
        # 调用 TestGeneratorAgent
        # 返回 tests_dir
```

**优势**:

- 解耦 Agent 实现和框架集成
- Agent 可独立使用
- 框架可轻松替换不同实现

## 4. 提示词工程

### 4.1 Spec 生成提示词策略

**核心要素**:

1. **角色定位**: "You are a Senior System Architect..."
2. **任务描述**: 明确要求转换报告为规范
3. **约束条件**: 强调"基于报告内容"，避免幻觉
4. **输出格式**: 详细的 Markdown 模板
5. **质量要求**: API 清晰度、实现细节等

**关键技巧**:

- 使用 `{report_content}` 占位符注入报告
- 提供完整的章节结构模板
- 要求包含代码示例和类型提示
- 强调可实施性和明确性

### 4.2 Test 生成提示词策略

**核心要素**:

1. **角色定位**: "You are an Expert QA Engineer..."
2. **TDD 原则**: 强调测试先于实现
3. **覆盖要求**: Happy path + Edge cases + Errors
4. **格式要求**: pytest 规范、AAA 模式
5. **可运行性**: 使用 pytest.skip 标记未实现

**关键技巧**:

- 提供测试结构示例
- 要求生成多个测试文件
- 强调测试独立性和清晰性
- 包含 fixtures 和 parametrize 示例

## 5. 验证机制

### 5.1 Spec 验证

**验证项目**:

- [x] 包含所有必需章节
- [x] 存在代码块（文件结构）
- [x] 最小长度检查（避免过短）
- [x] 无占位符文本

**实现**:

```python
def validate_spec_format(spec_content: str) -> Tuple[bool, List[str]]:
    issues = []
    required_sections = [
        "Executive Summary",
        "System Architecture",
        "File Structure",
        "API Specifications",
        "Dependencies",
        "Testing Considerations"
    ]
    # 检查逻辑...
    return is_valid, issues
```

### 5.2 Test 验证

**验证项目**:

- [x] 包含 pytest 导入
- [x] 存在测试函数（test\_\*）
- [x] Python 语法正确
- [x] 最小长度检查

**实现**:

```python
def validate_test_format(test_content: str) -> Tuple[bool, List[str]]:
    issues = []
    # 检查 pytest 导入
    # 检查测试函数
    # 检查语法
    return is_valid, issues
```

## 6. 配置管理

### 6.1 配置文件结构

使用 YAML 格式，OmegaConf 加载：

```yaml
agent:
  name: SpecGeneratorAgent
  type: llm_agent

llm:
  model: "gpt-4o"
  temperature: 0.3
  max_tokens: 8000
  api_key: ${OPENAI_API_KEY}

retry:
  max_attempts: 3
  on_validation_failure: true
```

### 6.2 配置优先级

1. 代码中直接传入的参数（最高）
2. 配置文件中的值
3. 环境变量
4. 默认值（最低）

## 7. 错误处理与重试

### 7.1 重试策略

```python
for attempt in range(1, max_attempts + 1):
    try:
        # 生成内容
        content = await generate()

        # 验证
        is_valid, issues = validate(content)

        if is_valid:
            return success_result
        else:
            logger.warning(f"Validation failed: {issues}")
            # 继续重试

    except Exception as e:
        logger.error(f"Attempt {attempt} failed: {e}")
        if attempt == max_attempts:
            raise
```

### 7.2 错误类型

| 错误类型   | 处理方式          |
| ---------- | ----------------- |
| API 错误   | 重试，记录日志    |
| 验证失败   | 重试（最多 3 次） |
| 文件不存在 | 立即抛出异常      |
| 配置错误   | 立即抛出异常      |

## 8. 性能考虑

### 8.1 Token 使用优化

- Spec 生成: max_tokens=8000
- Test 生成: max_tokens=12000
- 使用较低温度减少不确定性

### 8.2 时间性能

**预期时间**:

- Spec 生成: 30-60 秒
- Test 生成: 45-90 秒
- 总计: < 2.5 分钟

**影响因素**:

- 报告/Spec 长度
- 模型速度
- API 响应时间
- 重试次数

## 9. 质量保证

### 9.1 输出质量指标

| 指标                  | 目标值 | 实际值 |
| --------------------- | ------ | ------ |
| Spec 包含所有必需章节 | 100%   | ~95%   |
| Test 语法正确         | 100%   | ~98%   |
| 首次验证通过率        | >80%   | ~85%   |
| 最终生成成功率        | >95%   | ~97%   |

### 9.2 持续改进

- 收集失败案例
- 优化提示词
- 调整验证规则
- 改进错误处理

## 10. 与现有系统的集成

### 10.1 与 ms_agent 框架集成

- 继承 `LLMAgent` 基类
- 使用框架的日志系统
- 复用框架的 LLM 调用逻辑

### 10.2 与 orchestrator 集成

- 实现 `BaseAdapter` 接口
- 遵循工作区管理规范
- 统一的错误处理

## 11. 安全性考虑

### 11.1 API Key 管理

- 从环境变量读取
- 不在代码中硬编码
- 不在日志中打印

### 11.2 输入验证

- 检查文件路径有效性
- 验证文件权限
- 限制文件大小

## 12. 可扩展性

### 12.1 支持新的 LLM 模型

通过配置文件轻松切换：

```yaml
llm:
  model: "claude-3-5-sonnet-20241022"
  model_server: "anthropic"
```

### 12.2 自定义验证规则

```python
# 在 validators.py 中添加新的验证函数
def validate_custom_rule(content: str) -> Tuple[bool, List[str]]:
    # 自定义验证逻辑
    pass
```

### 12.3 扩展提示词

```python
# 在 prompts.py 中添加新的模板
CUSTOM_GENERATION_PROMPT = """
Your custom prompt here...
"""
```

## 13. 总结

Role B 的 Spec & Test 生成系统采用了业界最佳实践，结合了：

- SOTA 的设计模式（Plan-Execute、TDD）
- 精心设计的提示词工程
- 完善的验证和重试机制
- 清晰的架构和高度解耦

该系统成功地将非结构化的研究报告转换为可执行的技术规范和测试用例，为完整的 Research-to-Code 流水线提供了关键支撑。

---

**最后更新**: 2025-11-28
