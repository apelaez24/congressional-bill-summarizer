# Congressional Bill Summarizer

This project fetches, inspects, and logs detailed U.S. Congressional bill data from the [Congress.gov API](https://api.congress.gov/). It is designed for transparency, debugging, and eventually scraping missing content when API access is incomplete.

---

## 🔧 Features

- Retrieves recent bills from the House or Senate
- Extracts full bill metadata (title, sponsor, latest action, subjects)
- Logs sponsor and cosponsor details with party breakdown
- Shows bill text or summary if available
- Handles and logs amendments and related bills
- Automatically queues missing summaries for scraping (coming soon)
- Robust error handling and log file creation for each run

---

## 📁 Directory Structure

```
📁 congressional-bill-summarizer/
│
├── data_pipeline/
│   └── explore_api_data.py          # Main script for API exploration
│
├── logs/
│   └── explore_YYYY-MM-DD_HHMMSS.log   # Run-by-run logs
│
├── requirements.txt   # Dependencies for the environment
├── .gitignore         # Ignore rules for Git
├── README.md          # Project documentation
├── CHANGELOG.md       # List of changes by version
└── .env               # Stores your GOV_API_KEY (not committed)
```
---

## 🛠 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/congressional-bill-summarizer.git
   cd congressional-bill-summarizer
2. **Create a virtual environment**
   conda create --name congress_env python=3.10
   conda activate congress_env
3. **Install dependencies**
    pip install -r requirements.txt
4. **Set your API Key**
    Create a .env file in the root directory and add:
    GOV_API_KEY=your_api_key_here
5. **Run the Script**
    python data_pipeline/explore_api_data.py

📦 Dependencies
Stored in requirements.txt, but core libraries include:

requests

pandas

python-dotenv

beautifulsoup4

🚧 Coming Soon
HTML scraping fallback for missing summaries

Persistent database storage

Frontend to explore bills interactively

Daily bill tracker dashboard

📜 License
MIT License — see LICENSE (coming soon)



