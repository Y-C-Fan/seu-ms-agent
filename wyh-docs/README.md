# wyh-docs: Role B 文档目录

**角色**: Role B - Spec & Test Generation (胶水层)  
**负责人**: WYH  
**最后更新**: 2025-11-28

---

## 📚 文档结构

本目录包含 Role B (Spec & Test 生成模块) 的完整文档，参考 chao-docs 的结构组织。

```
wyh-docs/
├── README.md                    # 本文件
├── 00analysis/                  # 技术分析文档
│   └── spec_test_generation_analysis.md
├── 01goals/                     # 目标与规划
│   └── role_b_goals.md
└── 02todos/                     # 任务追踪与交付
    └── 0.0_Role_B_Delivery_Note.md
```

---

## 📖 文档索引

### 00analysis/ - 技术分析

#### [spec_test_generation_analysis.md](00analysis/spec_test_generation_analysis.md)

全面的技术分析文档，包含：

- SOTA 技术调研（Plan-Execute、TDD、Prompt Engineering）
- 架构设计（SpecAgent、TestAgent、适配器层）
- 提示词工程策略
- 验证机制
- 性能与质量保证

**适合阅读对象**: 技术负责人、架构师、想深入了解实现细节的开发者

---

### 01goals/ - 目标文档

#### [role_b_goals.md](01goals/role_b_goals.md)

Role B 的目标定义文档，包含：

- 总体目标
- 技术目标（Spec 生成、Test 生成、集成）
- 功能目标清单
- 质量标准
- 与 Role A/C 的协作目标
- 验收标准

**适合阅读对象**: 项目经理、团队成员、想了解 Role B 职责的人

---

### 02todos/ - 任务与交付

#### [0.0_Role_B_Delivery_Note.md](02todos/0.0_Role_B_Delivery_Note.md)

最终交付文档，包含：

- 变更文件树
- 完成工作总结
- 使用指南
- 协作说明
- 配置说明
- 故障排查
- 验收标准

**适合阅读对象**: 所有人，这是最重要的文档

---

## 🎯 Role B 概述

### 角色定位

Role B 是 Research-to-Code 流水线的**"胶水层"**，负责：

1. 将自然语言研究报告 → 结构化技术规范
2. 将技术规范 → 可执行的测试用例

### 工作流程

```
Research Report (Role A)
         ↓
    SpecAgent ─────→ tech_spec.md
         ↓
    TestAgent ─────→ tests/
         ↓
Implementation (Role C)
```

### 核心组件

| 组件               | 位置                   | 作用         |
| ------------------ | ---------------------- | ------------ |
| SpecGeneratorAgent | wyh_test/agents/       | 生成技术规范 |
| TestGeneratorAgent | wyh_test/agents/       | 生成测试用例 |
| SpecAdapter        | orchestrator/adapters/ | 集成桥接     |
| TestGenAdapter     | orchestrator/adapters/ | 集成桥接     |

---

## 🚀 快速开始

### 查看完整实现

```bash
cd /workspaces/seu-ms-agent

# 查看 Agent 实现
cat wyh_test/agents/spec_generator_agent.py
cat wyh_test/agents/test_generator_agent.py

# 查看适配器
cat orchestrator/adapters/spec_adapter.py
cat orchestrator/adapters/test_gen_adapter.py
```

### 运行示例

```bash
# 通过 orchestrator 运行完整流程
python3 orchestrator/main.py "Build a REST API"

# 查看生成的 Spec 和 Tests
ls workspace/run_*/
cat workspace/run_*/tech_spec.md
ls workspace/run_*/tests/
```

### 查看配置

```bash
# Spec Agent 配置
cat wyh_test/configs/spec_agent.yaml

# Test Agent 配置
cat wyh_test/configs/test_agent.yaml
```

---

## 📊 项目状态

### ✅ 已完成

- [x] SpecGeneratorAgent 实现 (314 lines)
- [x] TestGeneratorAgent 实现 (429 lines)
- [x] 适配器层实现 (202 lines)
- [x] 提示词工程 (440 lines)
- [x] 验证器实现 (214 lines)
- [x] 配置文件 (182 lines)
- [x] 文档完善
- [x] 集成到 orchestrator

**总代码量**: ~1,781 lines

### 🎯 验收状态

| 标准       | 状态    |
| ---------- | ------- |
| 代码完整性 | ✅ 100% |
| 适配器集成 | ✅ 完成 |
| 配置文件   | ✅ 完整 |
| 文档完善度 | ✅ 完整 |
| 质量验证   | ✅ 通过 |

---

## 🔗 相关资源

### 核心实现目录

- **wyh_test/** - Role B 核心实现（不可删除）
  - agents/ - Agent 实现
  - adapters/ - 适配器（备份）
  - configs/ - 配置文件
  - utils/ - 工具函数
  - tests/ - 单元测试

### 其他文档

- **wyh_test/README.md** - 详细使用文档
- **wyh_test/DELIVERY_NOTE.md** - 原始交付说明
- **orchestrator/** - Role A 的编排器框架

---

## 📝 文档阅读顺序建议

### 新手入门

1. 先读本 README 了解整体
2. 阅读 [0.0_Role_B_Delivery_Note.md](02todos/0.0_Role_B_Delivery_Note.md) 了解如何使用
3. 查看 wyh_test/README.md 了解详细用法

### 深入学习

1. 阅读 [role_b_goals.md](01goals/role_b_goals.md) 了解设计目标
2. 阅读 [spec_test_generation_analysis.md](00analysis/spec_test_generation_analysis.md) 了解技术细节
3. 查看源代码实现

### 集成开发

1. 查看 [0.0_Role_B_Delivery_Note.md](02todos/0.0_Role_B_Delivery_Note.md) 的协作章节
2. 了解适配器接口
3. 参考配置文件进行定制

---

## 🤝 团队协作

### 与 Role A (Orchestrator) 的协作

- **输入**: report.md
- **输出**: tech_spec.md, tests/
- **接口**: BaseAdapter

参考文档: [0.0_Role_B_Delivery_Note.md § 4](02todos/0.0_Role_B_Delivery_Note.md)

### 与 Role C (Coding Agent) 的协作

- **提供**: 技术规范、测试用例
- **支持**: 代码验证、迭代优化

参考文档: [role_b_goals.md § 5.2](01goals/role_b_goals.md)

---

## 💡 关键设计决策

### 1. 为什么使用适配器模式？

- **解耦**: Agent 可独立于 orchestrator 使用
- **灵活**: 易于替换不同实现
- **清晰**: 明确的接口边界

### 2. 为什么先生成测试？

- **TDD**: 遵循业界最佳实践
- **规范**: 测试是可执行的规范
- **验证**: 为 Code Agent 提供验证标准

### 3. 为什么使用高质量模型？

- **准确性**: Spec 是整个流程的基础
- **减少返工**: 高质量输出减少后续修改
- **成本效益**: 虽然单次调用贵，但总体更经济

---

## 📞 支持与反馈

如有问题或建议，请：

1. 查看文档中的故障排查章节
2. 检查 workspace/\*/logs/orchestrator.log
3. 联系 Role B 负责人

---

## 📅 版本历史

| 版本   | 日期       | 说明                   |
| ------ | ---------- | ---------------------- |
| v0.1.0 | 2025-11-28 | 初始版本，完成核心功能 |

---

**维护者**: Role B Team  
**最后更新**: 2025-11-28  
**状态**: ✅ 生产就绪
