# Data Science for Biology Workshop

This repository contains materials for a 3-day hands-on workshop in **data science for biology**, hosted at USLS, Bacolod, Philippines.

The workshop is designed for students with **little to no prior programming experience**. The goal is not to turn everyone into a software engineer, but to show how computational tools can make biological data easier to understand, analyze, and communicate.

---

## 🌱 Workshop Philosophy

Modern biology is increasingly a data-driven science.

From climate change and biodiversity loss to epidemiology and ecosystem monitoring, biological questions today are often answered through:

* data collection
* data analysis
* visualization
* simple modeling

This workshop focuses on the idea that:

> Programming is not the goal — it is a tool for understanding biological systems.

We emphasize intuition, interpretation, and visual storytelling over technical complexity.

---

## 🎯 Learning Goals

By the end of this workshop, students will be able to:

* Load and manipulate real-world datasets using Python
* Create clear and informative data visualizations
* Understand basic trends in environmental and biological data
* Recognize common pitfalls in data interpretation
* Apply simple models to explore biological or environmental systems
* Communicate insights using plots and data summaries

---

## 🧭 Workshop Structure

The workshop is divided into three progressive modules:

### Day 1 — Introduction to Data & Climate Signals

* Basic Python data handling
* Global temperature trends
* Local climate comparison (Bacolod)
* Introduction to “hockey stick” style visualizations

### Day 2 — Patterns in Environmental Systems

* Seasonal cycles (rainfall, wind, monsoons)
* Working with geospatial and time series data
* Introduction to structured datasets (e.g. climate reanalysis products)

### Day 3 — From Data to Insight

* Combining multiple variables (temperature, rainfall, wind)
* Simple modeling and interpretation
* Identifying patterns, correlations, and limitations of data

---

## 📁 Repository Structure

```text
workshop/
├── notebooks/         # Main workshop notebooks (Day 1–3)
├── src/               # Helper Python utilities (hidden complexity)
├── data/              # Datasets (raw + processed)
├── figures/           # Generated plots (optional)
├── behind-the-scenes/ # Data preparation notebooks
└── pyproject.toml     # Python package configuration
```

---

## 🚀 How to Use This Repository (Google Colab)

All notebooks are designed to run in **Google Colab**.

1. Open the Day 1 notebook:

   ```
   https://colab.research.google.com/github/yourname/workshop/blob/main/notebooks/day1.ipynb
   ```

2. Run the first setup cell, which will:

   * download the repository
   * install required dependencies
   * mount Google Drive for saving outputs

3. Follow the instructions inside the notebook.

No local installation is required.

---

## 💾 Data Storage

During the workshop, students will generate outputs such as:

* processed datasets
* plots and figures
* intermediate results

These are stored in Google Drive under:

```
MyDrive/biology-workshop/
```

This ensures that work persists across sessions and between workshop days.

---

## ⚙️ Technical Notes (For Instructors / Advanced Users)

The repository uses a lightweight Python package structure located in `src/workshop_utils/` to keep notebooks clean and focused on learning outcomes.

Utility functions handle:

* data downloading
* preprocessing
* plotting helpers
* reusable analysis routines

Students are not expected to interact with this layer directly unless instructed.

---

## 🌍 Why This Workshop Exists

Biology today is deeply connected to data science.

Understanding environmental change, biodiversity loss, and ecological systems requires the ability to:

* analyze large datasets
* visualize trends clearly
* communicate results effectively

This workshop aims to lower the barrier to entry and show that these skills are accessible to everyone.

---

## 📜 License

This material is provided for educational use.
You are free to reuse or adapt it for teaching purposes with attribution.

---

## 👨‍🏫 Instructor Notes

This workshop is intentionally designed to:

* minimize setup friction
* avoid installation issues
* prioritize conceptual understanding over syntax memorization
* gradually introduce computational thinking through biology-relevant examples

Feedback and improvements are welcome.