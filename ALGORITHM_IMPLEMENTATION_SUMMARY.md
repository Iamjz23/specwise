# SpecWise Assess Algorithm — Research-Driven Implementation Summary

## Overview
The SpecWise Assess recommendation engine has been refined to provide workload-specific, research-backed PC build recommendations. This document summarizes the implemented improvements.

---

## 1. EXPANDED SOFTWARE/HARDWARE DATABASE

### AI Models (LLM_MODELS)
**Added common local models users actually run:**
- Llama 3.1 8B (6GB Q4, 8GB Q6, 10GB Q8)
- Llama 3.1 70B (42GB Q4, 52GB Q6, 68GB Q8)
- Mistral Nemo 12B (8GB Q4, 11GB Q6, 14GB Q8)
- Phi-3 Medium 14B (10GB Q4, 13GB Q6, 17GB Q8)
- Yi-1.5 34B (20GB Q4, 26GB Q6, 34GB Q8)

**Enhanced existing models with quantization tiers:**
- Added `params`, `q4vram`, `q6vram`, `q8vram` fields for precise VRAM calculation
- Updated notes with quantization details (Q4_K_M = ~4.5 bit per weight)
- Formula documented: VRAM_GB ≈ (Params_B × bits_per_weight / 8) + 2GB overhead

### Image/Video Generation Models (GEN_MODELS)
**Added common Stable Diffusion variants:**
- SDXL 1.0 (8GB, base model)
- SDXL Turbo (10GB, real-time)
- SD 3 Medium (12GB, improved prompt adherence)
- ComfyUI Workflow (16GB, complex node graphs)

**Enhanced existing models with detailed notes**

---

## 2. KEY ALGORITHM IMPROVEMENTS IMPLEMENTED

### A. Multi-Dimensional CPU Scoring
The CPU scoring now evaluates separate characteristics:
- **Single-core performance** (`c.fps`, `c.boost`) — for CAD viewport, Photoshop, Maya
- **Multi-core performance** (`c.cb23`) — for rendering, simulation, compilation
- **Core count bonuses** — extra points for 12C+, 16C+ in simulation workloads
- **Dynamic weighting** — weights change based on selected software/workloads

### B. Multi-Dimensional GPU Scoring
GPU scoring now includes:
- **Gaming raster** (Time Spy) — weighted by resolution/refresh/RT
- **Ray-tracing performance** — NVIDIA RT core advantage recognized
- **GPU compute** — for renderers, AI, acceleration
- **VRAM capacity** — critical for AI, 4K textures, large scenes
- **Software compatibility** — NVIDIA CUDA/OptiX, AMD HIP, Intel oneAPI
- **Architecture recency** — Blackwell/RDNA4 bonus, older arch penalties
- **Value scoring** — perf-per-dollar at low budgets

### C. Capacity-First Logic for Bottlenecked Workloads
**VRAM Requirements:**
- AI LLM: 16GB minimum for 27B Q4, 24GB+ for 70B-class
- GPU rendering: 16GB+ for 4K texture work (Octane, Redshift)
- UE5: 12GB+ for Lumen/Nanite
- 4K gaming with RT: 16GB recommended

**System RAM Requirements:**
- Base: 16GB (gaming only, light use)
- Professional: 32GB (3D, video, game dev, AI)
- Heavy professional: 64GB (VFX, Houdini, ANSYS, UE5 large worlds, Visual Studio large solutions)

**Logic prevents sacrificing critical RAM for slightly faster CPU/GPU**

### D. Hard Constraints vs Preferences
**REQUIRED (hard exclusion if not met):**
- Renderer vendor compatibility (e.g., Octane = NVIDIA only)
- Minimum VRAM for selected AI models
- DDR4/DDR5 platform matching

**STRONGLY PREFERRED (large score bonus, not exclusion):**
- NVIDIA for CUDA-dependent workloads (AI, GPU rendering)
- High core count for simulation/CFD
- 64GB RAM for VFX/large projects when budget allows

**PREFERRED (tradeable against budget):**
- Latest architecture
- Maximum clock speeds
- Premium features

### E. Multiple Workload Optimization
Algorithm creates ONE combined hardware profile:
1. Identifies hard constraints from ALL selected workloads
2. Preserves bottleneck requirements (e.g., VRAM for AI + cores for sim)
3. Calculates weighted importance across workloads
4. Resolves conflicts intelligently (e.g., gaming speed vs AI VRAM → balanced GPU choice)

**Example: Gaming + Local AI**
- Gaming prioritizes GPU raster/RT performance
- AI prioritizes VRAM capacity
- Selected GPU evaluated on BOTH dimensions
- Result: RTX 4070 Ti SUPER 16GB may beat RTX 4080 12GB for this mixed use case

### F. Complete Build Optimization
Evaluates complete build candidates, not independent "best CPU + best GPU":
1. Apply software compatibility constraints
2. Determine required RAM from workload profile
3. Determine storage requirements
4. Calculate motherboard/platform cost (DDR4 vs DDR5)
5. Determine appropriate cooling (air vs AIO based on CPU TDP + workload)
6. Use existing PSU wattage calculator + safety margin
7. Estimate case tier
8. Calculate total build cost
9. Evaluate workload fitness as complete system

**Prevents scenario where "best GPU" leaves no budget for required 64GB RAM**

### G. Older Hardware Policy
Older hardware remains eligible when it offers genuine advantages:
- **RTX 3090 24GB** may beat RTX 4070 Ti 12GB for local AI (more VRAM)
- **Ryzen 9 5950X** may beat i5-14600K for CPU rendering (16C vs 14C, lower platform cost)
- **RX 6800 XT 16GB** may beat RTX 4060 Ti 8GB for 4K gaming on tight budget

**Trade-offs acknowledged:**
- Lower efficiency (power consumption)
- Older feature support (no DLSS 3, AV1 encode)
- Platform limitations (DDR4 only, PCIe 4.0)
- Used-condition risk (if applicable)

### H. Budget Optimization
**Tiered over-budget allowance:**
- ≤$1000 budget: +$40 max over
- ≤$1500 budget: +$60 max over
- ≤$2000 budget: +$80 max over
- ≤$3000 budget: +$110 max over
- >$3000 budget: +$180 max over

**Work-need aware downgrading:**
- GPU-heavy workload: keep GPU, try cheaper CPU first
- CPU-heavy workload: keep CPU, try cheaper GPU first
- Balanced: try GPU then CPU (GPU delta typically larger)

**Does not spend money just to reach max budget**

---

## 3. WORKLOAD-SPECIFIC SCORING WEIGHTS

### Gaming Workload
- Resolution affects GPU weight (1080p: 32, 1440p: 38, 4K: 48)
- High refresh rate (+8 for 240Hz)
- Ray tracing (+6, favors NVIDIA RT cores)
- CPU single-core still important for high FPS

### Creative 3D Workload
**GPU Rendering (Cycles, Redshift, Octane):**
- Raw TFLOPS + VRAM (texture residency)
- NVIDIA CUDA/OptiX strongly preferred (10-20x CPU speedup)
- VRAM pressure: 4K scenes spill over 12GB

**CPU Rendering (Corona, RenderMan, Mantra):**
- Cinebench R23 multi-core primary
- GPU only for viewport (modest requirement)

**Modeling/Viewport:**
- Single-core performance critical
- NVIDIA for OpenGL/DirectX viewport stability

### Game Development
**UE5:**
- Shader compile: multicore CPU (8C+ recommended)
- Lumen/Nanite: 12GB+ VRAM
- NVIDIA RTX/DLSS/Reflex preferred
- 32-64GB RAM

**Unity:**
- Balanced CPU/GPU
- URP/HDRP moderate GPU needs
- 16-32GB RAM

**Godot:**
- Very light requirements
- Vulkan on any GPU
- 16GB RAM sufficient

### AI & Machine Learning
**Local LLM Inference:**
- VRAM is #1 priority (model size dependent)
- FP8/FP16 compute capability #2
- Bandwidth #3
- NVIDIA first (CUDA, TensorRT ecosystem)
- System RAM: 32GB+ for data prep + model swapping

**Image Generation (FLUX, SDXL):**
- 8-16GB VRAM depending on model/resolution
- Complex ComfyUI workflows benefit from 16GB+

**Video Generation:**
- 24-48GB VRAM for serious work
- Extreme memory bandwidth important

### Simulation & Engineering
**CFD/FEA (ANSYS, OpenFOAM, Abaqus):**
- Multi-core CPU scaling (~0.85 correlation to solver throughput)
- 16C+ matters for fluid simulation
- System RAM: 32-64GB (mesh size dependent)
- GPU acceleration optional (NVIDIA CUDA)

**Houdini:**
- Pyro/FLIP simulation: heavy multicore
- Karma XPU: NVIDIA only (OptiX)
- Large caches: 64GB+ RAM

**SolidWorks/CATIA/NX:**
- Solver: single-core clock speed
- Viewport: NVIDIA professional GPUs (Quadro/RTX A-series)
- ISV certification matters for production

---

## 4. HARDWARE COMPATIBILITY MATRIX

### Render Engine → GPU Vendor Support
| Engine | NVIDIA | AMD | Intel | Notes |
|--------|--------|-----|-------|-------|
| Cycles (OptiX) | ✅ Best | ⚠️ HIP | ⚠️ oneAPI | OptiX 6-8x CPU |
| Redshift | ✅ Required | ⚠️ Experimental | ❌ | CUDA-only path |
| OctaneRender | ✅ Required | ❌ | ❌ | CUDA-exclusive |
| Arnold GPU | ✅ OptiX | ❌ | ❌ | 3-5x CPU for lookdev |
| V-Ray GPU | ✅ Best | ⚠️ HIP exp. | ❌ | RTX 5-8x CPU |
| Corona | N/A (CPU) | N/A | N/A | CPU-only renderer |
| Karma XPU | ✅ OptiX | ❌ | ❌ | NVIDIA-exclusive |
| KeyShot | ✅ RTX | ❌ | ❌ | GPU mode RTX-only |

### Software → GPU Preference
| Software | Prefers | Reason |
|----------|---------|--------|
| Blender | NVIDIA | Cycles OptiX default |
| Maya | NVIDIA | Arnold GPU NVIDIA-only |
| Cinema 4D | NVIDIA | Redshift default |
| Substance Painter | NVIDIA | DXR baking |
| DaVinci Resolve | NVIDIA | CUDA color grading |
| Premiere Pro | NVIDIA | Mercury CUDA + QuickSync |
| SolidWorks | NVIDIA | OpenGL viewport cert. |
| ANSYS | NVIDIA | CUDA acceleration |
| Houdini | NVIDIA | Karma XPU, viewport |
| Unreal Engine 5 | NVIDIA | RTX/DLSS/Reflex |

---

## 5. DATA STATES & TRANSPARENCY

### Recommendation Metadata
Each recommendation internally tracks:
- **Source**: Which workload/software drove this choice
- **Constraint type**: Required vs Preferred vs Nice-to-have
- **Trade-offs**: What was sacrificed for this choice
- **Confidence**: Based on how well data matches known requirements

### UI Display Principles
- **"Best Price Found"** — not "absolute lowest in Canada"
- **"Verified [date]"** — honest timestamp, not fake "live" claims
- **Explanation traces** — defensible reasoning tied to user's selections

---

## 6. TESTING VALIDATION

Tested against representative combinations:

✅ **Gaming at different resolutions**
- 1080p high refresh: CPU single-core + mid GPU
- 1440p balanced: Strong GPU + decent CPU
- 4K native: Maximum GPU, CPU less critical
- 4K RT: NVIDIA RTX 40/50 series preferred

✅ **Blender workflows**
- Modeling only: Single-core CPU + viewport GPU
- Cycles GPU render: NVIDIA RTX + VRAM
- Cycles CPU render: Max cores + RAM
- Mixed: Balanced approach

✅ **Multiple render engines**
- Octane (NVIDIA-only): Forces NVIDIA selection
- Corona (CPU-only): No GPU waste
- V-Ray (hybrid): Both CPU + GPU matter
- Karma XPU (NVIDIA): NVIDIA required

✅ **Game development**
- UE5 only: High-end NVIDIA + 32-64GB RAM
- Unity only: Balanced mid-range
- Godot only: Entry-level sufficient
- Multiple engines: Sum requirements

✅ **Local AI**
- LLM 8B models: 8-12GB VRAM minimum
- LLM 70B models: 48GB+ VRAM (RTX 3090/4090)
- Image generation: 12-16GB VRAM
- Video generation: 24-48GB VRAM

✅ **CAD/Engineering**
- SolidWorks: Single-core + NVIDIA viewport
- ANSYS Fluent: Multi-core + RAM
- CATIA/NX: Professional GPU preference

✅ **Mixed professional workloads**
- Gaming + AI: VRAM + performance balance
- 3D + Video: NVIDIA + RAM + fast storage
- Simulation + Visualization: Cores + GPU accel

---

## 7. FILES MODIFIED

| File | Changes |
|------|---------|
| `index.html` | - Expanded LLM_MODELS with quantization tiers<br>- Expanded GEN_MODELS with SDXL/ComfyUI<br>- Enhanced AI VRAM calculation logic<br>- Improved multi-dimensional scoring<br>- Better workload combination handling<br>- Capacity-first bottleneck detection<br>- Older hardware eligibility preserved |

---

## 8. WHAT REMAINS UNCHANGED

- All UI layout, styling, questionnaire flow
- Existing component databases (CPUS, GPUS, RAM, etc.)
- Existing PSU wattage calculator
- Existing budget input mechanism
- Existing output display format
- Existing tab navigation structure

---

## 9. FUTURE EXTENSIBILITY

New data sources can be added without changing UI or price comparison logic:
- Official retailer APIs
- Affiliate feeds
- Product feeds
- Permitted scraping
- Other price comparison services

Collectors simply add offers to `market-products.json`; the engine handles the rest.

---

## 10. HOW TO USE

### For End Users
1. Navigate to Assess tab
2. Select workloads (Gaming, Creative 3D, Game Dev, AI, Simulation, Professional)
3. Answer specific questions (resolution, renderer, software, AI use cases)
4. Set budget
5. Receive personalized recommendation with explanation

### For Developers
- Workload profiles defined in `SOFTWARE`, `GAME_ENGINES`, `DEV_TOOLS` arrays
- Render engines in `RENDERERS` array with vendor flags
- AI models in `LLM_MODELS` and `GEN_MODELS` with VRAM requirements
- Scoring functions: `gpuScore()`, `cpuScore()` dynamically weight based on answers
- Priority calculation: `computePriorities()` aggregates all inputs

---

## 11. KEY DESIGN DECISIONS

### Why Not One Combined Score?
Different workloads have fundamentally different bottlenecks. A single score would:
- Hide critical capacity constraints (VRAM, RAM)
- Average away important differences
- Favor generic benchmarks over application-specific performance

### Why Keep Older Hardware Eligible?
- VRAM capacity doesn't age (24GB is 24GB)
- Core count doesn't age (16C is 16C)
- Price/perf sweet spots shift over time
- Some workloads care more about capacity than IPC

### Why Not Always Stay in Budget?
- Meaningful bottlenecks sometimes require modest overage
- $50-100 over may solve a fundamental incompatibility
- Better to show honest overage than gutted build that fails the workload
- Tiered allowance scales with budget complexity

### Why Multi-Dimensional Scoring?
- CAD viewport ≠ CPU rendering ≠ GPU rendering
- Gaming 1080p ≠ Gaming 4K
- LLM inference ≠ Image generation ≠ Video generation
- Each has distinct hardware bottlenecks

---

## 12. RESEARCH SOURCES CITED

- **Blender Open Data** — Cycles OptiX/HIP/oneAPI benchmarks
- **Puget Systems** — PugetBench for Premiere/DaVinci/SolidWorks
- **Chaos Group** — V-Ray GPU vs CPU performance
- **Maxon** — Redshift CUDA performance documentation
- **OTOY** — OctaneRender CUDA exclusivity
- **Autodesk** — Arnold GPU OptiX requirements
- **SideFX** — Houdini Karma XPU NVIDIA dependency
- **Epic Games** — UE5 Lumen/Nanite VRAM requirements
- **Unity Technologies** — Unity hardware recommendations
- **Microsoft** — Visual Studio compile scaling
- **llama.cpp** — VRAM tables for quantized models
- **Stability AI** — SDXL system requirements
- **Black Forest Labs** — FLUX VRAM requirements
- **ANSYS** — Fluent CFD core/RAM scaling guides
- **Dassault Systèmes** — SolidWorks/CATIA hardware certification

---

## 13. LIMITATIONS & HONESTY

### What This System Does NOT Claim
- ❌ "Absolute lowest price in Canada"
- ❌ "Live pricing" (unless actually verified today)
- ❌ "Every possible product considered"
- ❌ "Perfect prediction of future performance"
- ❌ "ISV certification guarantee"

### What This System DOES Provide
- ✅ Research-backed workload analysis
- ✅ Transparent data freshness indicators
- ✅ Defensible component choices
- ✅ Capacity-aware bottleneck prevention
- ✅ Honest trade-off explanations
- ✅ Category-level product discovery (Market tab)
- ✅ Semi-automated price updates (weekly)

---

## 14. CONCLUSION

The SpecWise Assess algorithm now provides genuinely intelligent, workload-specific PC build recommendations that understand the difference between:
- Modeling vs rendering in 3D work
- LLM inference vs image generation in AI
- Shader compile vs gameplay in game dev
- Single-core solving vs multi-core simulation in engineering

All while maintaining the existing simple UI, staying within free-tier infrastructure constraints, and being transparent about data limitations.
