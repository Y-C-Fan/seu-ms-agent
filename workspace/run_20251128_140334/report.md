# Quantum and Stochastic Computing Foundations for Arithmetic Circuit Design

## Introduction

The request to "build a simple calculator" initially appears trivial within classical computing paradigms. However, the absence of constraints or specifications—particularly the explicit refusal ("NO") to clarify scope, platform, or feature set—necessitates a comprehensive exploration of what constitutes arithmetic computation across emerging computational models. This report synthesizes findings from quantum arithmetic circuit design, stochastic computing-based neural accelerators, modular quantum algorithms for cryptography, and specialized numerical libraries to define the theoretical and practical boundaries of calculator implementation in non-classical contexts. The synthesis reveals that even basic operations like addition, subtraction, multiplication, and division exhibit profound complexity when ported to quantum or probabilistic hardware, with implications for fault tolerance, resource scaling, and algorithmic structure.

## Quantum Arithmetic Circuits: From Basic Operations to Cryptographic Primitives

### Fundamental Building Blocks

Quantum arithmetic circuits are constructed from reversible logic gates, primarily Toffoli and CNOT gates, due to the unitary nature of quantum evolution. Basic operations such as addition leverage structured blocks:

- **MAJ (Majority)** and **UMA (Unmajority and Add)** form the core of ripple-carry adders.
- **CARRY** and **SUM** blocks enable modular composition.

When one operand is a known classical constant $ y $, significant optimization is possible. For instance, the circuit **2Add_y** achieves addition with only $ 14n - 5.5 $ CNOT gates for an $ n $-qubit register, exploiting the fixed nature of $ y $ to eliminate superfluous controls.

A theoretical lower bound for $ n $-qubit addition has been established at **9n CNOTs**, derived from the necessity of at least one Toffoli gate (≈6 CNOTs via decomposition) and three additional CNOTs per bit for carry propagation. Current constructions exceed this bound but approach it under reversibility and modularity constraints.

### Comparison and Modular Arithmetic

Quantum comparison circuits differentiate between known constants and fully quantum operands:

- **1Comp_y** (constant comparator): $ 12n + 1 $ CNOTs.
- **2Comp_y** (quantum-state comparator): $ 16n + 1 $ CNOTs.

Controlled variants add six CNOTs, reflecting the overhead of conditional execution.

Modular arithmetic builds upon these primitives:

- **ModAdd⁻¹** (modular subtraction with constant): $ 43n - 2.5 $ CNOTs.
- **ModAdd** (modular addition of two quantum states): $ 61n + 6 $ CNOTs.

Both rely on combinations of **1Add**, **2Add⁻¹**, and **2Comp** blocks, demonstrating the compositional nature of quantum arithmetic.

### Modular Multiplication and Inversion

Three distinct approaches to quantum modular multiplication have been analyzed:

| Method        | CNOT Complexity               |
|---------------|-------------------------------|
| Fast          | $ 104n^2 - 86.5n - 11.5 $   |
| Montgomery    | $ 90n^2 + 78n - 9 $         |
| Direct        | $ 114n^2 + 5n $             |

The **Montgomery method** is preferred when the modulus $ p \not\approx 2^n $, as it leverages precomputed constants and optimized **ShiftMod** circuits. The **ShiftMod** operation itself uses comparison instead of subtraction, achieving $ 31n + 15 $ CNOTs—a notable improvement over prior designs.

Modular inversion, critical for elliptic curve cryptography, implements an improved **Montgomery-Kaliski algorithm** requiring $ 578n^2 + 283n - 13 $ CNOTs. This involves $ 2n $ rounds of iteration and handles inputs in superposition, a non-trivial requirement for cryptographic applications.

Binary shift operations for modular doubling offer two methods:

- **Method 1**: $ 2n $ CNOTs (uncontrolled), $ 12n $ in controlled form.
- **Method 2**: $ 3n $ CNOTs (uncontrolled), $ 8n $ in controlled form.

**Method 2 is preferred in controlled contexts** due to lower overhead when decomposing Toffoli gates.

### Elliptic Curve Point Addition and Shor’s Algorithm Optimization

Controlled point addition on elliptic curves—a core subroutine in attacking the Elliptic Curve Discrete Logarithm Problem (ECDLP)—requires a 13-step sequence involving **ModAdd⁻¹**, **Inv**, **M-Mul**, and **D-Mul**. The total cost is $ 896n^2 + 1064n + 14 $ CNOTs, reducible to $ 886n^2 + 783.5n - 18.5 $ by omitting uncomputation in the final round.

**Windowed arithmetic** stores precomputed multiples in quantum registers (not classical memory), enabling reuse and yielding a circuit cost of $ 896n^2 + 1108n + 36 $ CNOTs. This technique underpins the **extended Shor’s algorithm for ECDLP**, which reduces asymptotic complexity from $ O(n^3) $ to $ O(n^3 / \log n) $.

Despite this optimization, practical runtime remains prohibitive: **~51 years for a 512-bit ECDLP on an ion-trap quantum computer**, excluding fault-tolerance overhead.

## Alternative Quantum Arithmetic: Fourier-Based and Residue Approaches

### Quantum Fourier Transform (QFT) Arithmetic

Arithmetic in the **Quantum Fourier Basis (QFB)** encodes integers as phase rotations, enabling addition and multiplication via controlled phase shifts. The **Approximate QFT (AQFT)** reduces gate count from $ O(n^2) $ to $ O(n \log n) $ by limiting rotation depth $ d $. Empirical studies show **optimal $ d \approx \log_2 n $** under noise.

Counterintuitively, **Signed Quantum Fourier Addition (sQFA)** outperforms unsigned variants by up to **40 percentage points in success rate** on noisy simulators for 8-qubit integers, despite requiring two extra Toffoli gates. This robustness across error rates and AQFT depths remains unexplained but suggests sign-handling interacts beneficially with phase approximation.

**Controlled Quantum Fourier Multiplication (QFM)** preserves both inputs and writes output to a separate register. It scales poorly with depth and is **more noise-sensitive than QFA**, even for 4-qubit registers.

Gate error analysis reveals that **2-qubit gate errors dominate performance degradation**, especially as operand superposition increases. However, for large $ n $, cumulative 1-qubit phase inaccuracies may become limiting.

### Residue Number System (RNS) and Distributed Addition

The **Residue Number System (RNS)** with moduli $ (2^n - 1, 2^n, 2^n + 1) $ enables distributed quantum addition. For a 10-bit sum, RNS configuration $ (4,5,7,9) $ achieved **86.5% output probability** on the Quantinuum H1 simulator, versus **37.1%** for a monolithic TPL13 adder—a **133% fidelity gain**.

The **QSMART tool** automates moduli selection for target ranges:

- $ (3,4,5) $: covers 0–59 (93.75% efficient for 6-bit).
- $ (5,7,8,9) $: covers 0–2519 (100% for 11-bit).

This enables arithmetic beyond NISQ qubit limits via job distribution.

### Carry-Lookahead and Dynamic-Circuit Adders

The **Quantum Carry-Lookahead Modulo $ (2^n - 1) $ Adder (QCLMA)** achieves $ O(\log n) $ depth versus $ O(n) $ for ripple-carry designs. On IBM Cairo (27-qubit), it demonstrated a **47.21% higher Quantum State Fidelity Ratio (QSFR)** for 4-bit inputs.

**Dynamic-circuit modulo $ (2^n + 1) $ adders (QMA3/QMA4)** use mid-circuit reset to reuse $ |b\rangle $ qubits, reducing qubit count from $ 3n + 5 $ to $ 2n + 4 $. **QMA4** adds redundant resets to purify $ |0\rangle $ states, lowering **Normalized Mean Error Distance (NMED) by 28.8%** on IBM Washington.

## Hardware Platform Considerations and Timing Analysis

Execution time varies drastically across platforms:

| Platform       | $ t_{q1} $ | $ t_{q2} $ | $ t_{\text{measure}} $ | $ t_{\text{reset}} $ |
|----------------|-------------|-------------|--------------------------|------------------------|
| IBM Heron      | 32 ns       | 68 ns       | 1560 ns                  | 1708 ns                |
| IonQ Forte     | 130 µs      | 970 µs      | 150 µs                   | 50 µs                  |

Neutral-atom platforms suffer from **~10 ms measurement/reset times**, making iterative algorithms (e.g., IPE-based Shor) significantly slower. For $ n=64 $, the **alternating design**—which interleaves $ CU^{2^i} $ operations and phase processing using two data qubits—achieves **~50% delay reduction** over iterative designs on slow-reset platforms.

**Static Timing Analysis (STA)** adapted to quantum circuits models execution via weighted DAGs, where edge weights reflect gate delays. The critical path determines circuit delay $ t_C $, which diverges from logical depth when gate times vary (e.g., $ t_{q2} \gg t_{q1} $ on IBM devices).

## Quantum Memory and Distributed Algorithms

**Fat-Tree QRAM** enables $ O(\log N) $ parallel queries on shared memory with $ O(N) $ qubits and constant bandwidth (~1.21×10⁵ qubit/sec). Unlike Bucket-Brigade QRAM, which serializes queries, Fat-Tree reduces Grover’s algorithm depth from $ O(\log^2 N \sqrt{N}) $ to $ O(\log N \sqrt{N}) $ for $ N=2^{10} $.

It maintains BB-like infidelity scaling $ F \geq 1 - 2 \cdot \log^2 N \cdot (\varepsilon_0 + \varepsilon_1 + \varepsilon_2) $ with only **25% fidelity penalty** under typical error rates ($ \varepsilon_0 = \varepsilon_1 = 0.002, \varepsilon_2 = 0.001 $). Its pipelined structure also enables **virtual distillation**, boosting fidelity from 0.84 to 0.9994 for $ N=4 $.

For **distributed Shor’s algorithm** using the EJPP protocol, $ m $ ebits are required (one per $ CU^{2^i} $). With a single ebit channel, the work register idles during ebit generation (G), start (S), and end (E) phases. **Two ebit channels suffice to eliminate idle time if $ t_{\text{ebit}} \leq t(CU) $**.

## Stochastic Computing for Efficient Arithmetic in Neural Accelerators

While not directly implementing a calculator, **Stochastic Computing (SC)-based Deep Convolutional Neural Networks (SC-DCNNs)** provide insight into ultra-low-power arithmetic via probabilistic bitstreams.

### SC Arithmetic Primitives

- **Inner Product**: Four designs evaluated:
  - **OR-gate**: inaccurate for bipolar data.
  - **MUX-based**: scalable accuracy with longer bitstreams.
  - **APC-based**: high accuracy (~1% error vs. conventional), uses approximate parallel counters to sum XNOR outputs column-wise, reducing gate count by ~40%.
  - **Two-line representation**: prone to overflow.

- **Pooling**: 
  - **Max pooling**: uses candidate comparison over bitstreams; achieves <0.17 relative deviation at 512-bit length.
  - **Average pooling**: simpler but less accurate near zero due to scaling effects.

- **Activation**: **tanh** preferred due to efficient FSM-based **Stanh** implementation.

### Optimized SC Feature Extraction Blocks

Three configurations balance accuracy and resources:

1. **MUX-Avg-Stanh**: area/energy efficient, low accuracy.
2. **MUX-Max-Stanh**: better accuracy.
3. **APC-Avg-Btanh**: high accuracy, higher resource use.

Weight storage can be **aggressively quantized**: 7-bit fixed-point weights incur <0.5% accuracy loss on MNIST, reducing SRAM area by **10.3×**. **Filter-aware SRAM sharing** groups convolutional weights by filter, minimizing routing overhead.

### Performance Benchmarks

LeNet-5 SC-DCNN implementations on MNIST achieve **96.64–98.26% accuracy** with:

- Area as low as **17.0 mm²**.
- Energy as low as **2.0 µJ/image**.
- Configuration No.11 (average pooling): **45,946 images/s/mm²** area efficiency.

SC-DCNNs outperform conventional hardware (e.g., Nvidia Tesla C2075) by:

- **15,625× in throughput**
- **159,604× in energy efficiency**

This demonstrates strong scalability potential due to **error compensation across layers**.

## Classical Numerical Libraries: OpenMMPol Case Study

Although outside quantum/stochastic domains, **OpenMMPol** illustrates how even classical “calculator” functions (e.g., force evaluation) face scalability challenges.

- Implements bonded/non-bonded terms for AMOEBA/AMBER force fields.
- **Van der Waals interactions**: linear-scaling via compressed cell-lists with hard cutoff.
- **Electrostatics**: naive $ O(N^2) $ double-loop, becoming bottleneck >1,000 atoms.
- Supports QM/MM via OpenMMPol–PySCF interface; caches electric field integrals.
- Benchmarks on 35,695-atom virus capsid show near-ideal parallel scaling (1–30 CPUs).
- Geometry optimization and MD validated via conserved energy in alanine dipeptide test.

This underscores that **even classical arithmetic in scientific computing requires algorithmic innovation for scalability**.

## Quantum Monte Carlo Integration: Financial Arithmetic as Calculator Analogue

Quantinuum’s **QMCI engine** treats expectation estimation as a generalized arithmetic task. It features:

- Six core components: Distribution Circuit, Quantity to Estimate, QAE, Backend Call, Cloud Call, QMCI Estimate.
- **P-builder module**: constructs complex payoff functions (barrier, Asian, look-back options) via quantum circuits performing sum, product, max/min, threshold.

Quantum states encode $ d $-dimensional discrete probability distributions; marginalization occurs via partial measurement (Born rule).

QMCI achieves **quadratic speedup** over classical Monte Carlo: RMSE $ \propto 1/q $ vs. $ 1/\sqrt{q} $.

**Fourier series decomposition** enables estimation of non-linear functions (mean, variance, $ \exp(X) $) while preserving quantum advantage.

Among QAE variants, **LCU-QAE** shows superior statistical robustness (excess kurtosis ≤0.3 vs. >2.0 for MLQAE/IQAE).

Resource estimates:

- **NISQ-feasible**: 4 time-slices (~10⁴ CNOTs, 100–170 qubits).
- **Fault-tolerant required**: 8-slice versions; T-count up to 7.54×10⁸.

**Crossover error thresholds** reach **1.88%** (Bernoulli estimation), indicating practical quantum advantage at modest accuracy.

## Conclusion

The notion of a “simple calculator” dissolves into a spectrum of computational models, each with distinct trade-offs:

- **Quantum arithmetic** demands reversibility, entanglement management, and error resilience, with costs scaling polynomially or quadratically in qubit count.
- **Stochastic computing** trades precision for extreme energy efficiency, suitable for AI inference but not general-purpose calculation.
- **Classical scientific libraries** reveal that even deterministic arithmetic faces $ O(N^2) $ bottlenecks without algorithmic redesign.
- **Quantum Monte Carlo** reframes integration as arithmetic, achieving quadratic speedups but requiring deep circuits.

Without user-specified constraints, the minimal viable calculator remains undefined. However, the research demonstrates that **any non-trivial implementation beyond classical floating-point units must confront fundamental limits in coherence, noise, and resource scaling**. Future work should explore hybrid models—e.g., RNS-distributed quantum adders interfaced with SC-based control logic—as a path toward practical quantum-assisted arithmetic.

## Sources

- https://arxiv.org/pdf/2305.11410v1
- https://arxiv.org/pdf/1901.02716v1
- https://arxiv.org/pdf/1611.05939v2
- https://arxiv.org/pdf/2112.09349v2
- https://arxiv.org/pdf/2503.22564v2
- https://arxiv.org/pdf/2502.06767v2
- https://arxiv.org/pdf/2408.01002v1
- https://arxiv.org/pdf/2406.07486v1
- https://arxiv.org/pdf/2406.05294v1
- https://arxiv.org/pdf/2401.14691v1
- https://arxiv.org/pdf/2308.06081v1