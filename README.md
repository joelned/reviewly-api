```markdown
# 🚀 Running Reviewly Locally

## Prerequisites

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)

## Step-by-Step Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/reviewly.git
cd reviewly
```

### 2. Create a Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv

# On Windows
python -m venv venv
```

### 3. Activate the Virtual Environment

```bash
# On macOS/Linux
source venv/bin/activate

# On Windows (Command Prompt)
venv\Scripts\activate

# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

You'll know it's activated when you see `(venv)` in your terminal prompt.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root and add:

```env
DATABASE_URL="sqlite+aiosqlite:///./reviewly.db"
SECRET_KEY="your-secret-key-here"
ENVIRONMENT="development"
```

### 6. Create the Database

```bash
python scripts/create_tables.py
```

### 7. Run the Application

```bash
uvicorn app.main:app --reload
```

## Access the App

Open your browser and go to:

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **App Root**: [http://localhost:8000](http://localhost:8000)

Press `Ctrl + C` to stop the server when you're done.
```
