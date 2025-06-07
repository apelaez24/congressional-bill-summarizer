# 🏛️ Congressional Bill Summarizer Project

## 📌 Project Overview
This project pulls daily U.S. Congressional bill data using a government API key and summarizes the content and sponsors using NLP. It stores data in a PostgreSQL database and provides a Flask-based interface to help people stay informed on legislation in a simple, accessible way.

---

## ✅ Phase 1: API Key Testing & Exploration

1. **Test API Key with Postman**
   - Confirm authentication method (query param or Bearer token).
   - Test endpoints for bills, sponsors, actions.
   - Understand response structure and rate limits.

2. **Explore API Capabilities**
   - Retrieve:
     - Bill title, summary, full text
     - Sponsors, cosponsors
     - Legislative actions and committees
   - Filter by chamber, date, sponsor, topic, etc.

---

## 🛠 Phase 2: Database Design & Setup

3. **Design PostgreSQL Schema**

   Tables:
   - `bills (id, title, summary, date_introduced, status)`
   - `sponsors (id, name, party, state, chamber)`
   - `bill_sponsors (bill_id, sponsor_id)`
   - `actions (id, bill_id, date, action_text)`

4. **Set Up PostgreSQL**
   - Use pgAdmin or CLI to create DB and tables.
   - Consider using Flask-SQLAlchemy for ORM.

---

## 🧠 Phase 3: Data Extraction & Summarization

5. **Write Python Extraction Script**
   - Use `requests` to pull data.
   - Modularize: `get_bills()`, `get_sponsors()`, etc.
   - Insert/update into PostgreSQL.

6. **Summarize Using spaCy**
   - Extract:
     - Main subject of bill
     - Key actions and named entities
   - Save outputs like `summary_nlp`, `key_terms`.

---

## 🧪 Phase 4: Testing & Validation

7. **Write Tests Using `pytest`**
   - Validate:
     - API response structure
     - JSON parsing
     - DB operations
     - NLP summaries
   - Use fixtures or mock responses for stability.

---

## 🌐 Phase 5: Web Interface & Chatbot

8. **Build Flask Web App**
   - Routes:
     - Homepage with daily bills
     - Search/filter by date, sponsor, topic
     - Detail view per bill
   - Use Flask-SQLAlchemy for DB integration.

9. **Add Chatbot/NLP Interface**
   - Use spaCy or custom rule-based bot.
   - Accept questions like:
     - “What did Congress do today?”
     - “Who sponsored bills about healthcare?”
   - Return concise summaries.

---

## 🚀 Phase 6: Deployment & Showcase

10. **Deploy to GitHub**
   - Include:
     - `README.md` with screenshots
     - Setup instructions
     - Demo video or GIF

11. **(Optional) Deploy to Azure Later**
   - Containerize with Docker (optional)
   - Use Azure App Service and Azure PostgreSQL when ready

---

## 🗂️ Future Features (Wishlist)
- User logins and saved preferences
- Email summaries of daily bills
- Vote tracking and outcome prediction
