# SecureVault - Zero-Knowledge Password Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

SecureVault is a secure, open-source password manager built with Python (Flask) and JavaScript. It features a zero-knowledge architecture, meaning your master password never leaves your device, and only encrypted data is stored on the server.

## ✨ Features

- 🔒 **Zero-knowledge architecture** - Client-side AES-256-GCM encryption
- 🎨 **Clean, minimal UI** with authentic feel
- 🔑 **Register/Login** with JWT session handling
- 📝 **Add, edit, delete** password entries
- 🔐 **Local, secure decryption** using master password
- 🎲 **Password generator** and strength indicator
- 🔍 **Search** across saved entries
- 🔔 **Toast notifications** and loading states
- 🛡️ **CSP-compliant** (no inline scripts/handlers)

## 🚀 Quick Start

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/jaykumarpatil314-ux/Password-Manager.git
cd Password-Manager/backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials and secret keys

# Run the server
python app.py
```

### Frontend Setup

```bash
# Navigate to the frontend directory
cd ../frontend

# Load the extension in Chrome
1. Open Chrome and navigate to chrome://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked" and select the frontend directory
```

## 🏗️ Architecture

SecureVault follows a client-server architecture with end-to-end encryption:

```
┌─────────────────┐      ┌────────────────┐      ┌─────────────────┐
│                 │      │                │      │                 │
│  Chrome         │ HTTPS│  Flask Backend │ SQL/ │  Database       │
│  Extension      │──────│  API           │──────│  (PostgreSQL/   │
│  (Frontend)     │      │                │      │   MongoDB)      │
│                 │      │                │      │                 │
└─────────────────┘      └────────────────┘      └─────────────────┘
```

### Key Components

1. **Frontend**: Chrome extension with client-side encryption/decryption
2. **Backend API**: Flask server handling authentication and encrypted data storage
3. **Database**: Flexible storage with PostgreSQL or MongoDB support

## 🔐 Security

SecureVault implements multiple layers of security:

- **Master Password**: Never transmitted to the server
- **Key Derivation**: Argon2id with high memory and iteration parameters
- **Encryption**: AES-256-GCM for all sensitive data
- **Authentication**: JWT with short expiration and refresh token rotation
- **Transport**: HTTPS with TLS 1.3
- **Database**: Encrypted connection and at-rest encryption

### Zero-Knowledge Design

Your master password is used to derive an encryption key locally. Only encrypted data is sent to the server, ensuring that even in case of a server breach, your passwords remain secure.

## 📁 Project Structure

```
├── backend/
│   ├── app.py                      # Main Flask application
│   ├── auth.py                     # Authentication logic
│   ├── config.py                   # Configuration settings
│   ├── crypto_utils.py             # Server-side cryptography
│   ├── database/
│   │   ├── base_repository.py
│   │   ├── db_factory.py
│   │   ├── mongodb_repository.py
│   │   └── postgres_repository.py
│   ├── models/                     # Data models
│   └── requirements.txt            # Python dependencies
│
└── frontend/
    ├── api.js                      # API communication
    ├── background.js               # Extension background script
    ├── crypto.js                   # Client-side encryption
    ├── manifest.json               # Extension manifest
    ├── popup.html                  # Extension UI
    ├── popup.css                   # Styling
    └── popup.js                    # UI logic
```

## 🛠️ Development

### Prerequisites

- Python 3.9+
- Chrome browser
- PostgreSQL or MongoDB

### Testing

```bash
# Run backend tests
cd backend
python -m pytest test_all.py

# Frontend tests (coming soon)
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Crypto.js](https://github.com/brix/crypto-js) for client-side encryption
- [Flask](https://flask.palletsprojects.com/) for the backend framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM
- [PyMongo](https://pymongo.readthedocs.io/) for MongoDB integration

---

<div align="center">
  <sub>Built with ❤️ for security and privacy</sub>
</div>
