# 🌿 Plant Disease Detection — Backend API

A production-ready Flask REST API serving AI-powered plant disease detection for the Flutter mobile app.

## Tech Stack

- **Python 3.10+** / **Flask 3.1**
- **MongoDB Atlas** via PyMongo
- **TensorFlow / Keras** — 38-class plant disease classifier
- **JWT** authentication (PyJWT + bcrypt)
- **Cloudinary** (optional) for image storage

## Project Structure

```
backend/
├── app.py                  # Flask app factory + entry point
├── config.py               # Environment config
├── seed.py                 # DB seed (38 diseases, 14 plants)
├── test_api.py             # End-to-end API tests
├── requirements.txt
│
├── middleware/
│   └── auth.py             # JWT auth decorators
│
├── models/                 # MongoDB document helpers
│   ├── db.py               # Mongo client + indexes
│   ├── user.py
│   ├── scan.py
│   ├── disease.py
│   ├── plant.py
│   └── diagnosis.py
│
├── routes/                 # Flask blueprints
│   ├── auth.py             # /api/auth/*
│   ├── scans.py            # /api/scans/*
│   ├── diseases.py         # /api/diseases/*
│   ├── users.py            # /api/users/*
│   └── admin.py            # /api/admin/*
│
└── services/
    ├── ai_service.py       # TF model loader + predict()
    └── storage_service.py  # Cloudinary / local upload
```

## Quick Start

```bash
cd backend

# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI and secrets

# 4. Seed the database (38 diseases + 14 plants)
python seed.py

# 5. Run the server
python app.py
# → http://127.0.0.1:5000

# 6. Run tests
python test_api.py
```

## API Endpoints

### Auth — `/api/auth`

| Method | Endpoint    | Auth | Description    |
| ------ | ----------- | ---- | -------------- |
| POST   | `/register` | ❌   | Create account |
| POST   | `/login`    | ❌   | Get JWT token  |
| GET    | `/me`       | ✅   | Current user   |

### Scans — `/api/scans`

| Method | Endpoint | Auth | Description                 |
| ------ | -------- | ---- | --------------------------- |
| POST   | `/`      | ✅   | Upload image → AI diagnosis |
| GET    | `/`      | ✅   | Scan history (paginated)    |
| GET    | `/:id`   | ✅   | Scan detail                 |

### Diseases — `/api/diseases`

| Method | Endpoint | Auth | Description          |
| ------ | -------- | ---- | -------------------- |
| GET    | `/`      | ❌   | List all 38 diseases |
| GET    | `/:id`   | ❌   | Disease detail       |

### Users — `/api/users`

| Method | Endpoint    | Auth | Description       |
| ------ | ----------- | ---- | ----------------- |
| GET    | `/profile`  | ✅   | Profile + stats   |
| PUT    | `/profile`  | ✅   | Update name/email |
| PUT    | `/password` | ✅   | Change password   |

### Admin — `/api/admin`

| Method | Endpoint        | Auth | Description      |
| ------ | --------------- | ---- | ---------------- |
| GET    | `/users`        | 🔒   | List all users   |
| POST   | `/diseases`     | 🔒   | Create disease   |
| PUT    | `/diseases/:id` | 🔒   | Update disease   |
| DELETE | `/diseases/:id` | 🔒   | Delete disease   |
| GET    | `/analytics`    | 🔒   | System dashboard |

> ✅ = JWT required | 🔒 = Admin JWT required

## AI Model

Place `trained_plant_disease_model.keras` in the `backend/` directory.
The model classifies plant leaf images into 38 classes (128×128 input).

## Notes

- **Cloudinary**: Set `CLOUDINARY_*` env vars for cloud image storage. Without them, images save locally to `backend/uploads/`.
- **Admin**: Set a user's `role` to `"admin"` in MongoDB to access admin routes.
