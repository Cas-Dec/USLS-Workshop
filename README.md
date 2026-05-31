# Data Science for Biology Workshop

This repository contains materials for a 3-day hands-on workshop in **data science for biology**, hosted at USLS, Bacolod, Philippines.

The workshop is designed for students with **little to no prior programming experience**. The goal is not to turn everyone into a software engineer, but to show how computational tools can make biological data easier to understand, analyze, and communicate.

---

## 🌍 Why This Workshop?

Modern biology is deeply connected to data science.

Understanding environmental change, biodiversity loss, and ecological systems; from climate change and biodiversity loss to epidemiology and ecosystem monitoring, biological questions today are often answered through:

* data collection
* data analysis
* visualization
* simple modeling

This workshop focuses on the idea that:

> Programming is not the goal — it is a tool for understanding biological systems.

These skills are accessible to everyone. Using Python, we can:

* analyze large datasets
* discover new findings
* communicate results effectively

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

### Day 1 — Seeing the Climate Through Data

* PART I: From raw numbers to global and local patterns and trends
* PART II: Temperature on Earth is changing. What is driving these changes?
* PART III: Climate in Negros and the Philippines

### Day 2 — ...

* ...

### Day 3 — ...

* ...

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
   https://colab.research.google.com/github/yourname/workshop/blob/main/notebooks/intro.ipynb
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

These are stored in your personal Google Drive under:

```
MyDrive/USLS-Workshop/
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

## License

This material is provided for educational use.
You are free to reuse or adapt it for teaching purposes with attribution.

---

## Instructor Notes

This workshop is intentionally designed for accessible and easy handling for people with little to zero programming experience. Through relevant scientific and biological storylines, it aims to gently introduce the power of programming tools.

Feedback and improvements are welcome!