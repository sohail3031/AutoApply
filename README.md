# 🚀 AutoApply – Automated Job Application Assistant

**👋 Welcome to AutoApply, your personal job application assistant!**
This tool automates the tedious process of applying to jobs on platforms like Glassdoor, helping you save time and focus on preparing for interviews.

No more endless scrolling or repetitive clicks – just smart, efficient, and customizable job applications tailored to your preferences.

---

# ✨ Features

- **🤖 Automated Job Applications** – Fills in job applications for you on Glassdoor (more platforms coming soon).
- **📝 Smart Screener Question Handling** – Answers required and optional questions dynamically from JSON input.
- **🎯 Semantic Matching** – Uses SentenceTransformer embeddings to understand and match questions with stored answers.
- **📜 Customizable Input Data** – Store your answers in a structured JSON file.
- **⏳ Lazy Loading & Dynamic Elements** – Handles infinite scrolling and dynamically loaded questions using Selenium.
- **🎨 Color-Coded CLI** – User-friendly terminal interface with colorized messages for better readability.
- **🔒 Error Handling** – Gracefully manages missing elements, incorrect inputs, and timeouts.
- **📊 Application Tracker** – Keep a log of applied jobs and track statuses.

---

# 🚀 Upcoming Features

- **🔍 Multi-Platform Support** – Extend automation to LinkedIn, Indeed, and more job boards.
- **🌐 Headless Mode** – Faster, resource-friendly execution without opening a visible browser window.
- **🌐 More Security Questions** – Different job applications having different screener questions on GlassDoor/Indeed.

---

# 🛠️ Tech Stack

- Python 3.10+
- Selenium WebDriver (browser automation)
- SentenceTransformers (semantic question matching)
- Colorama (beautiful CLI experience)
- JSON-based Configs (user input and question/answer storage)

---

# ⚙️ Setup Instructions

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/AutoApply.git
cd AutoApply
```

## 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

## 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## 4️⃣ Configure Input Data
Edit **.json** and provide answers for the questions.

---

# ▶️ Usage

Run the tool:

```bash
python auto_apply.py
```

---

# 🐞 Troubleshooting

- **Element not found errors** → increase WEB_DRIVER_TIMEOUT in config.py.
- **Lazy loading issues** → AutoApply already scrolls, but you may need to increase SLEEP_TIMEOUT.
- **Browser compatibility** → Tested on Firefox with latest drivers.

---

# 🤝 Contributing

Contributions are welcome!

- Fork the repo
- Create a new branch (feature/my-feature)
- Submit a pull request 🚀

---

# 📜 License

**MIT License** – free to use, modify, and distribute.

---

# 🙌 Acknowledgements

- [**Selenium**](https://www.selenium.dev/) – for browser automation
- [**SentenceTransformers**](https://www.sbert.net/) – for semantic text similarity
- [**Colorama**](https://pypi.org/project/colorama/) – for colorful CLI
