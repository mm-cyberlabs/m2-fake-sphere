[//]: # (<h1 align="left">♾️ M<sup>2</sup> Fake Sphere: Synthetic Data Generator ♾️</h1>)

[//]: # (<div style="display: inline-block; padding: 5px; border-radius: 50px;">)

[//]: # (  <img src="assets/fake_sphere_app_logo.png" alt="logo" width="200" style="box-shadow: 10px 10px 20px rgba&#40;0,0,0,0.4&#41;; border-radius: 40px;">)

[//]: # (</div>)

---

<div style="display: inline-block; padding: 5px;">
  <img src="assets/fake_sphere_app_logo_w_text.png" alt="logo" width="600">
</div>

> _“We are living in a computer-programmed reality, and the only clue we have to it is when some variable is changed,
> and some alteration in our reality occurs.”_
> <br> — Philip K. Dick, 1977 Metz Sci-Fi Convention

## ♾️ About Fake Sphere

**Fake Sphere** is a **CLI-first, terminal-native synthetic data engine** built to simulate real-world data interactions across diverse systems — without compromising real data or privacy.

It supports:

- 🧪 **Databases** – Generate realistic datasets into Postgres, MySQL, SQLite, and more  
- 📡 **RESTful & GraphQL APIs** – Simulate live API payloads and test mutators  
- 🔁 **Streaming platforms** – Emit events to Kafka, Pulsar, or your own custom streams  
- 📂 **Files & data lakes** – Populate CSVs, JSONs, or cloud buckets with structured data  
- 🤖 **Agent flows** – Model personas and behavior for advanced system simulations  

---

### 🎯 Who is this for?

Fake Sphere is made for:

- **Developers** building data-driven apps  
- **QA Engineers** need consistent, realistic test environments  
- **ML Engineers** looking to train or test models with curated synthetic datasets  
- **API Designers** who want to simulate request/response payloads  
- **Data Architects** designing ETL pipelines without production risk  

> ⚠️ No more relying on outdated seeds or real customer data.  
> 🧬 Just pure simulation — fast, smart, and tunable.

```shell
  simulation core online  
  preparing SYNTHETIC DATA INGESTION INTO: [`DBs`] [`APIs`] [`STREAMS`] [`FILES`]  
  booting FAKE SPHERE 1.0...
```

---

## ▓▌ MISSION

> Simulate everything. Feed the system.  
> Fake Sphere is a CLI-first, terminal-native engine to spawn synthetic data across:

- 🧪 Local & remote **databases**
- 📡 Web & **RESTful/GraphQL APIs**
- 🔁 Real-time **streaming platforms**
- 📂 Flat files & **data lakes**
- 🤖 Simulated **agents & behavior flows**

---

## **Components**
## _Intelligence_ 
## 💿 **Data Scraper & Markdown Converter**: 
Scrapes the data from the different documentation and libraries to generate the synthetic data. Microsoft's Markitdown is the chosen for HTML to Markdown converter. This is needed to make LLM fine-tune easier.   
- _**Scraper: trafilatura**_: [GH Link](https://github.com/adbar/trafilatura) Used as a scraper of the framework documentation. It cleans the HTML from header and footers.
- _**Markdown Creator: Microsoft Markitdown**_: [GH Link](https://github.com/microsoft/markitdown) MarkItDown is a lightweight Python utility for converting various files to Markdown for use with LLMs and related text analysis pipelines.

## 🥸 **Synthetic Data Models**:
- _**Faker & Mimesis**_: contains predefined templates of data with randomization.
- _**SDV (Synthetic Data Vault)**_: ML-based modeling, trained on probabilistic models of real data. It generates samples similar to real data.
- _**Scikit-Learn Statistical Distribution for ML**_: uses mathematical functions to generate features, useful for simulating classification, regression and clustering

| 📚 `Library`  | ⚙️ `Generation Method` | 🎯 `Data Realism` | 🔗 `Structured Relationships` |
|---------------|------------------------|-------------------|-------------------------------|
| Faker/Mimesis | Templates + Randomness | LOW-MEDIUM        | ❌                             |
| SDV           | ML-based Prob. Models  | HIGH              | ✅                             |
| scikit-learn  | Statistical Simulation | MEDIUM            | ❌                             |

## 🧠 **LLM Fine-Tune with Phi-2** 
The llm of choice for a tie-breaker agent is **[Phi-2](https://huggingface.co/microsoft/phi-2)**. Is a 2.7B parameters that easily run in Apple Silicon and have local fast response times.

| `Criteria`                 | `Phi-2 Strength`                                                                                                                                                     |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ✅ Code-aware understanding | Trained with synthetic Python, NumPy, and ML-related code snippets.                                                                                                  |
| ✅ Low Memory footprint     | **~3~4GB RAM** usage in quantized mode (Q4_0 or Q8_0). Compresses the model by reducing the precision of its weight from 32-bit of floats to 4-bit or 8-bit integers |
| ✅ Fine-tunable locally     | Easily fine-tuned with **QLoRA** + **Axolotl** or **PEFT** methods.                                                                                                  |
| ✅ Structured reasoning     | Great at picking between similar options, ideal for tie-breaking in mappings.                                                                                        |
| ✅ Data-efficient           | Performs well with small fine-tunes (e.g. 100-1,000 examples)                                                                                                        |
| ✅ Fast inference on CPU    | Doesn't required a high-end GPU.                                                                                                                                     |

> **🧪 QLoRA**  
> "Quantized Low-Rank Adaptation: fine-tune large models in 4-bit precision using LoRA adapters — minimal memory, maximum performance."

> **🦎 Axolotl**  
> "A training orchestrator that wraps QLoRA, PEFT, and Hugging Face into one YAML-configurable tool — great for fast, local fine-tuning."

> **🧩 PEFT**  
> "Parameter-Efficient Fine-Tuning: only updates small subsets of model weights (like LoRA) to reduce resource needs during fine-tuning."

### ✅ Which Fine-Tune strategy? 🏆 _**QLoRA + Axolotl**_ 🏆

**Why QLoRA?**
- ♻️Quantized -> uses 4-bit weights, reducing memory usage drastically
- 🧠 LoRA adapters -> inject changes via low-rank matrices instead of updating all weights
- 🔧 Firs on local machines -> fine-tune Phi-2 on CPU or low-VRAM GPUs
- 🧪 Ideal for: small custom training sets (~500–1,000 high-quality examples)

> **QLoRA** is surgical and efficient, perfect for making Phi-2 better at tiebreak without bloating your RAM.

**Why Axolotl?**
- 🦎 Built on top of QLoRA, PEFT and Transformers
- ✅ YAML config driven - minimal code, maximum control
- ✅ Handles prompt formatting, tokenization, training, eval in one package
- ✅ Works seamlessly with Phi-2, TinyLlama, Mistral, etc.

> **Axolotl** makes the whole pipeline stupid simple: write a config, drop your dataset, run the script.

## _User Configuration and Needs_


## _CLI & Monitoring_

---

## 👨🏻‍💻In Progress & ✅ Done

[✔] - Build dynamic scraper to scrap documentation directly from the source website. It converts from HTML to Markdown
files to help the LLM training to better understanding. <br>
[⟳] - Build a LLM Fine-tune process for the tie-breaker Agent.  
[⟳] - Create the training code using Torch and create the small LLM based on the downloaded
documentation. <br>
[⟳] - Generate the LLM <br>
[⟳] - Adapt the Fake Sphere code to use output from the LLM based on context, to assign a faker function to an attribute
from the provided configuration. <br>

## Features

I. Database Full Fake Data

II. Single table Fake Data

## ▓▌ INSTALLATION {`COMING SOON`}

```shell
  git clone https://github.com/yourname/fake-sphere.git
  cd fake-sphere
  chmod +x sphere
  ./sphere --init
```

```doctest
docker run --rm -it yourname/fake-sphere
```

[✔] Static record generation <br>
[✔] Stream emitter <br>
[✔] Terminal menu <br>
[⟳] Agent flow simulation <br>
[⟳] TUI replay engine <br>
[ ] GraphQL mutator <br>
[ ] AI-tuned personas <br>