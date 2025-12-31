# 📜 LegalLens

**AI-powered contract analysis that turns legal jargon into plain English — spot red flags, understand risks, and know what to ask before you sign.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://legallens.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Gemini](https://img.shields.io/badge/Powered%20by-Gemini%202.5%20Flash-4285F4.svg)

---

## 🎯 What is LegalLens?

LegalLens is a free, AI-powered tool that helps everyday people understand legal documents before signing them. Simply upload a contract, lease, employment agreement, or any legal document — and get:

- **📝 Plain-Language Summary** — What you're actually agreeing to, explained like a friend would
- **⚠️ Risk Assessment** — Overall risk level (Low/Medium/High) with explanation
- **🚩 Red Flags** — Clauses that could hurt you, with quotes and explanations
- **✅ Good Parts** — Clauses that protect you
- **📚 Key Terms** — Legal jargon translated to simple English
- **❓ Questions to Ask** — What to clarify before signing
- **🌐 18+ Languages** — Instant translation to Hindi, Spanish, French, Chinese, and more

## 🖼️ Screenshots

| Upload & Analyze | Results |
|------------------|---------|
| Upload PDF, image, or paste text | Get instant AI analysis |

## 🚀 Try It Now

**Live Demo:** [legallens.streamlit.app](https://legallens.streamlit.app)

No sign-up required. No data stored. Free to use.

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io) — Fast, beautiful Python web apps
- **AI Model:** [Google Gemini 2.5 Flash](https://ai.google.dev/) — Fast, accurate, multilingual
- **PDF Processing:** Native Gemini PDF support (no text extraction needed)
- **Image OCR:** Gemini vision for scanned documents

## 📦 Installation (Local Development)

```bash
# Clone the repo
git clone https://github.com/httperry/LegalLens.git
cd LegalLens

# Install dependencies
pip install -r requirements.txt

# Add your Gemini API key
mkdir .streamlit
echo 'GEMINI_API_KEY = "your-api-key-here"' > .streamlit/secrets.toml

# Run the app
streamlit run app.py
```

Get your free Gemini API key at [aistudio.google.com](https://aistudio.google.com/app/apikey)

## 📁 Project Structure

```
LegalLens/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── secrets.toml    # API keys (not committed)
├── sampledata/         # Sample contracts for testing
├── .gitignore
└── README.md
```

## 🔑 Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Your Google Gemini API key |

## 🌍 Supported Languages

English, Hindi, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese (Simplified), Chinese (Traditional), Japanese, Korean, Arabic, Bengali, Tamil, Telugu, Marathi, Gujarati

## ⚠️ Disclaimer

**LegalLens is for educational purposes only and is NOT legal advice.**

- Always consult a qualified attorney before signing important documents
- AI analysis may contain errors or miss important details
- Do not rely solely on this tool for legal decisions

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for the powerful AI model
- [Streamlit](https://streamlit.io) for the amazing web framework
- All the people who need to understand contracts but can't afford a lawyer

---

**Made with ❤️ to help people understand what they're signing**
