# CBT Practice App 💻

A lightweight, high-performance Streamlit application designed to parse PDF past questions (including text blocks and diagrams) into a clean, randomized Computer-Based Test (CBT) practice interface.

Built to solve the common trap of photographic memory—where users accidentally cram the answers instead of learning the concepts. The application flexibly supports two major PDF answer layouts: **Inline** (answers placed immediately below each question) and **End of Document** (an answer key listing located at the end of the file).

still in beta stage and open to question

---

## Features

* **Smart Spatial Parsing**: Uses PyMuPDF (`fitz`) to extract text blocks and images in strict top-to-bottom order (`y0` coordinate sorting), ensuring network diagrams map correctly to their respective questions.
* **Robust Question Detection**: Handles variations in PDF numbering formats (e.g., standard numbers like `1.` as well as layout anomalies like `82.[R1]` or `190.According`).
* **Flexible Answer Modes**: Toggle seamlessly between inline answers and end-of-document answer key mapping right from the UI.
* **Interactive Testing Environment**:
* Randomized question shuffling on session start.
* Single-choice (`radio`) and multiple-choice (`multiselect`) question handling.
* Instant grading with immediate success/error feedback.
* Smooth navigation between questions to prevent answer memorization and build true technical competence.

---

## Prerequisites

Make sure you have Python installed on your system. You will need the following libraries:

* Streamlit
* PyMuPDF

---

## Installation & Setup Guide

1. **Clone or download** this repository to your local machine:
```bash
git clone git@github.com:stephen-oni/cbt-practice-app.git
cd cbt-practice-app

```


2. **Install dependencies** via your terminal or command prompt:
```bash
pip install streamlit pymupdf

```


3. **Run the application**:
```bash
streamlit run app.py

```


4. Open the local URL provided in your terminal (usually `http://localhost:8501`) to launch the app in your browser.

---

5. To close the localhost web go to your python environment and and use ctrl + c to stop the mahcine

---

## Usage

1. Launch the app using the command above.
2. Select your PDF answer format from the sidebar settings (**Inline** or **End of Document**).
3. Upload your PDF past questions file using the file uploader (supports large files up to 200MB).
4. Select your options and click **Submit Answer** to grade your work, then navigate through the question bank using the **Next/Previous** buttons to test your knowledge thoroughly.