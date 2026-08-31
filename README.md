# SpecWise

### Workload-Aware PC Configuration & Hardware Recommendation Platform

**SpecWise** is a PC configuration and recommendation platform designed to answer a more useful question than *“What are the best PC parts?”*

> **“What PC should I actually build for the work I do, with the budget I have?”**

Instead of relying primarily on generic benchmark rankings, SpecWise analyzes the user's **software, workloads, performance requirements, budget, memory requirements, GPU VRAM requirements, CPU characteristics, hardware compatibility, and multiple-use scenarios** to generate a tailored PC configuration.

It is designed for everyone from casual PC users and gamers to professionals working in **3D, game development, AI, programming, CAD, simulation, VFX, rendering, and engineering**.

---

## What Makes SpecWise Different?

A powerful GPU isn't automatically the right GPU.

A newer GPU isn't automatically better.

A 64GB system isn't automatically better than a 32GB system.

And a CPU with more cores isn't automatically better for every professional application.

SpecWise attempts to account for these differences.

For example:

* An **RTX 3090 24GB** can be a better recommendation than a newer GPU with less VRAM for local LLM inference.
* A 3D artist primarily modeling complex scenes may benefit more from strong **CPU single-core performance** than simply buying the most expensive GPU.
* A Houdini simulation workload can place significantly greater importance on **multi-core CPU performance and system RAM**.
* Blender Cycles rendering can shift the recommendation toward **GPU performance, CUDA/OptiX compatibility, and VRAM**.
* Professional workloads may justify allocating more of the budget toward **32GB, 64GB, 96GB, or 128GB system memory** rather than overspending on other components.
* A user combining gaming, Unreal Engine, Blender, local AI, and programming may need a **balanced configuration** instead of a component optimized for only one workload.

The goal is not to recommend the newest parts.

The goal is to recommend the **right parts**.

---

# Core Features

## 🧠 Workload-Aware PC Recommendation

SpecWise uses a multi-dimensional recommendation system that considers what the user actually intends to do with the computer.

The assessment can take into account workloads such as:

### Gaming

* Resolution
* Target FPS
* Ray tracing
* Graphics settings
* GPU requirements

### 3D & Digital Content Creation

* Blender
* Maya
* Cinema 4D
* Substance Painter
* Rendering
* Modeling
* Sculpting
* Animation
* Texturing

### Rendering

Different rendering workloads can favor very different hardware.

Examples include:

* Blender Cycles
* Octane
* Redshift
* V-Ray
* CPU rendering
* GPU rendering

The recommendation system considers factors such as:

* CPU vs GPU rendering
* NVIDIA requirements
* CUDA
* OptiX
* VRAM
* CPU single-core performance
* CPU multi-core performance

### Game Development

* Unreal Engine 5
* Unity
* Shader compilation
* Asset processing
* Editor viewport performance
* Lighting
* Packaging/build workloads

### AI & Local AI

* Local LLM inference
* Image generation
* ComfyUI
* AI workloads requiring large VRAM capacity
* Model size
* Quantization
* GPU compute
* System RAM

For AI workloads, **VRAM capacity can take priority over GPU generation**.

For example, an older GPU with substantially more VRAM can be a better choice than a newer GPU that cannot load the user's intended model.

### Programming / Software Development

* Software engineering
* Visual Studio
* Development environments
* Compilation
* Virtual machines
* General productivity

### CAD / Engineering

* SolidWorks
* CATIA
* Siemens NX
* Engineering applications
* CAD viewport workloads

These workloads can have different requirements for:

* CPU single-thread performance
* GPU viewport performance
* Professional GPU compatibility
* RAM capacity

### Simulation

* Houdini
* CFD
* ANSYS
* Other computational workloads

Simulation workloads can significantly increase the importance of:

* CPU multi-core performance
* CPU architecture
* RAM capacity
* Memory bandwidth
* GPU compute where applicable

---

# Multi-Workload Optimization

Real users rarely have only one workload.

A user might need:

> Gaming + Blender + Unreal Engine + Local AI + Programming

SpecWise attempts to find a configuration that performs well across the entire workload profile rather than optimizing exclusively for one application.

The recommendation engine therefore considers:

**Primary workload → Secondary workloads → Hardware requirements → Budget allocation → Overall system balance**

If one workload has a hard hardware requirement, that requirement can take priority over generic benchmark performance.

---

# Hardware Recommendation Logic

SpecWise evaluates hardware across multiple dimensions rather than using a single performance score.

## CPU

CPU selection can consider:

* Single-core performance
* Multi-core performance
* Core count
* Thread count
* Architecture/generation
* Workload-specific performance
* Price/performance
* Budget allocation

For example:

**3D modeling / viewport work**

→ stronger single-core performance may receive greater weight.

**Simulation / rendering / compilation**

→ multi-core performance may receive greater weight.

**Mixed workloads**

→ the algorithm attempts to balance both.

---

# GPU

GPU selection can consider:

* Rasterization performance
* Ray tracing
* Compute performance
* VRAM capacity
* Architecture
* CUDA / OptiX compatibility
* Software compatibility
* AI performance
* Rendering performance
* Price/performance
* Generation

Importantly, SpecWise does **not** automatically assume that the newest GPU is the best choice.

A previous-generation GPU may be recommended when its characteristics better match the user's workload.

For example:

> Local AI workload requiring large VRAM
> → RTX 3090 24GB may be preferable to a newer 12GB GPU.

This allows the recommendation system to optimize around **actual workload constraints**, rather than simply hardware generation.

---

# RAM Recommendations

System RAM is treated as a workload-dependent component rather than a fixed default.

Depending on the user's requirements, SpecWise can prioritize:

* 16GB
* 32GB
* 48GB
* 64GB
* 96GB
* 128GB

Professional workloads can receive higher RAM requirements than casual workloads.

Examples:

| Workload                        | Potential RAM Priority |
| ------------------------------- | ---------------------- |
| General use                     | Lower                  |
| Gaming                          | Moderate               |
| Programming                     | Moderate               |
| 3D creation                     | High                   |
| Professional VFX                | High                   |
| Simulation                      | Very High              |
| Large AI workflows              | Very High              |
| Multiple professional workloads | Very High              |

The final recommendation is determined by the overall workload rather than this table alone.

---

# Budget Optimization

SpecWise treats the budget as a **system-level constraint**.

It doesn't simply select the most expensive CPU and GPU possible.

The algorithm attempts to distribute the available budget according to the user's actual needs.

For example:

```text
Budget
   ↓
Determine workload priorities
   ↓
Identify hard requirements
   ↓
Allocate RAM / VRAM requirements
   ↓
Allocate CPU performance
   ↓
Allocate GPU performance
   ↓
Balance remaining components
   ↓
Evaluate complete system cost
   ↓
Select best configuration
```

The system may prioritize:

**More RAM**

when the workload requires it.

**More VRAM**

when AI or rendering requires it.

**Better GPU**

when GPU rendering or gaming dominates.

**More CPU cores**

when simulation or CPU rendering dominates.

**Higher single-core performance**

when CAD, modeling, or software behavior benefits from it.

---

# System Component Budgeting

The recommendation engine also accounts for the rest of the PC instead of pretending that the CPU and GPU consume the entire budget.

Typical baseline allocations include:

* Motherboard
* PSU
* CPU cooler
* Case
* Storage

For example, a mid-range configuration may use approximately:

```text
Motherboard: ~CA$220
PSU:         ~CA$130
Air cooler:  ~CA$50
Case:        ~CA$120
```

Higher-budget systems can allocate more toward:

* Higher-end motherboards
* Higher-quality PSUs
* Larger cases
* Better cooling
* Higher-end CPU cooling solutions

The actual component selection remains dependent on the complete build and available hardware database.

---

# Cooling Logic

CPU cooling is workload and CPU dependent.

Lower-power CPUs can use appropriate air cooling.

Higher-end CPUs such as:

* Ryzen 9
* Core i7 / i9
* Core Ultra 7 / Ultra 9

may justify substantially stronger cooling, particularly under sustained rendering, simulation, compilation, or other heavy workloads.

Higher-budget systems can allocate approximately:

```text
Air cooling:
~CA$50–80

Higher-end liquid cooling:
~CA$150–200
```

These are budget targets rather than hard product requirements.

---

# Power Supply Recommendation

SpecWise includes a PSU wattage calculation system.

The recommendation considers:

* CPU power requirements
* GPU power requirements
* Other system components
* Estimated system consumption
* Safety margin

The system maintains a power margin rather than selecting a PSU that merely matches estimated consumption.

This helps avoid configurations where the PSU is operating too close to the system's expected maximum load.

---

# Canadian Hardware Pricing

SpecWise is designed around the Canadian PC hardware market.

The Market system is intended to track pricing across Canadian retailers, including:

* Amazon.ca
* Canada Computers
* Memory Express
* Newegg Canada
* PC-Canada

The goal is not simply to find the cheapest listing for one specific product.

Instead, SpecWise can identify the lowest-priced suitable product within a **capacity category**.

For example:

### RAM

DDR4:

* 16GB
* 32GB
* 64GB
* 128GB

DDR5:

* 16GB
* 32GB
* 48GB
* 64GB
* 96GB
* 128GB

### SSD

* 512GB
* 1TB
* 2TB
* 4TB
* 8TB

This allows the Market system to answer questions such as:

> "What is the cheapest 64GB DDR5 desktop memory kit available?"

rather than only:

> "What is the price of this particular RAM model?"

---

# Price Data Architecture

Market pricing is stored separately from the website interface.

The current architecture uses:

```text
GitHub Repository
       │
       ├── index.html
       ├── ram-prices.json
       └── price collection scripts
                 │
                 ▼
          GitHub Actions
                 │
                 ▼
       Periodic price update
                 │
                 ▼
          ram-prices.json
                 │
                 ▼
          Cloudflare deployment
```

The intended system uses automated periodic collection where retailer access permits it, while preserving previously verified data when a retailer blocks automated requests.

Retailer anti-bot systems, CAPTCHA challenges, rate limits, and JavaScript-rendered pages can prevent reliable automated collection from certain stores.

SpecWise therefore avoids falsely claiming that blocked retailer data is live.

---

# Data Transparency

Price information should distinguish between:

* Automatically collected data
* Previously verified data
* Manually verified data
* Last-known pricing

Market data should include an appropriate verification timestamp whenever possible.

The goal is to provide useful pricing information without pretending that unavailable data is real-time.

---

# Recommendation Philosophy

SpecWise follows several principles.

### 1. Workload before benchmark

A benchmark score alone does not determine whether hardware is appropriate.

### 2. Requirements before generation

A newer component is not automatically better.

### 3. Capacity can be a hard constraint

Insufficient VRAM or RAM can make an otherwise faster component unsuitable.

### 4. Software matters

Different applications have different hardware preferences and limitations.

### 5. Professional workloads deserve professional configurations

A workstation used for CAD, simulation, VFX, rendering, AI, or engineering should not be configured like a basic gaming PC.

### 6. Optimize the complete system

The CPU, GPU, RAM, storage, motherboard, cooling, PSU, and case must work together.

### 7. Maximize the budget intelligently

The objective is not simply to spend the entire budget.

The objective is to spend it **where it produces the greatest benefit for the user's workload**.

### 8. Used hardware can be correct

Used or older hardware can be recommended when its capabilities provide a meaningful advantage.

For example:

> A 24GB GPU can be more useful for local AI than a newer 12GB GPU.

The algorithm therefore evaluates hardware based on **fitness for purpose**, not age alone.

---

# Technology

SpecWise is currently implemented as a lightweight web application with a static frontend and data-driven recommendation system.

Current project components include:

* HTML
* CSS
* JavaScript
* JSON hardware/pricing data
* Python-based price collection tools
* GitHub
* GitHub Actions
* Cloudflare

The project is intentionally lightweight and does not require a traditional always-on application server for the core website.

---

# Project Structure

```text
specwise/
│
├── index.html
├── ram-prices.json
├── package.json
├── package-lock.json
├── wrangler.jsonc
│
├── scripts/
│   └── update_market_prices.py
│
└── .github/
    └── workflows/
        └── ...
```

The exact repository structure may evolve as the recommendation and pricing systems develop.

---

# Development Goals

SpecWise is an ongoing project.

Future improvements may include:

* More comprehensive application-specific hardware data
* More detailed CPU workload characterization
* More detailed GPU compute compatibility
* Better VRAM requirement modeling
* Better RAM capacity modeling
* More sophisticated multi-workload optimization
* Improved Canadian price tracking
* Historical price tracking
* Price/performance analysis
* Used-market consideration
* Better professional workstation recommendations
* More detailed explanations for why a component was selected
* Build comparison
* Upgrade recommendations

---

# Disclaimer

Hardware performance varies by application, workload, configuration, driver version, operating system, and software version.

Professional applications can also change their hardware support over time.

SpecWise recommendations are intended as a decision-support tool rather than a guarantee of a particular application's performance.

Pricing is also subject to change, availability, promotions, taxes, shipping costs, and retailer policies.

Always verify final pricing and compatibility before purchasing hardware.

---

# Philosophy

PC building should not be:

> **"Pick the newest CPU + newest GPU and fill in the rest."**

It should be:

> **"Understand what the person actually does, identify what the software actually needs, determine the real constraints, and spend the budget where it matters."**

That's what SpecWise is built to do.

---

## SpecWise

**Build for the workload.
Spend where it matters.
Get the performance you actually need.**
