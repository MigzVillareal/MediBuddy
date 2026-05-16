# MediBuddy

## Setup

### 1. Clone the repository

```
git clone https://github.com/MigzVillareal/MediBuddy.git
cd MediBuddy
```

---

### 2. Setup Python backend

```
cd backend
python -m venv venv
```

#### Activate virtual environment

**Windows:**

```
venv\Scripts\activate
```

**Mac/Linux:**

```
source venv/bin/activate
```

#### Install dependencies

```
pip install -r requirements.txt
```

---

### 3. Run migrations

```
cd backend
python -m flask db upgrade
```

---

### 4. Start Flask backend

```
cd backend
python run.py
```

Backend runs at:
http://127.0.0.1:5000

---

### 5. Setup Vue frontend

Open a new terminal:

```
cd frontend
npm install
npm run dev
```

Frontend runs at:
http://localhost:5173

---

### 6. Use the app

Open the Vue URL in your browser.
