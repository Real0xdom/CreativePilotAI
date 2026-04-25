# CreativePilot AI

A creative automation tool that generates dealer-branded advertising visuals using a background image you upload. The AI automatically adjusts panel placement and logo color based on the image's brightness no manual design work needed.

Built with a **Next.js** frontend and a **Flask** backend using **Pillow** for image composition.

---

## How It Works

You upload a background photo (car shoot, lifestyle, etc.), pick a brand and a dealer, and the app does the rest. Under the hood it:

- Crops and scales your image to the target output size (1080×1080 by default)
- Pastes the dealer's panel template on top using alpha compositing
- Analyzes the image brightness and picks either the light or dark version of the logo accordingly
- Saves the final creative as a PNG and gives you a download link or a ZIP if you're generating for multiple dealers at once

---

## Project Structure

```
CreativePilot AI/
├── backend/
│   ├── app.py            ← Flask API server
│   ├── generator.py      ← Image composition pipeline
│   ├── ai_layout.py      ← Brightness detection + panel placement logic
│   ├── requirements.txt
│   ├── assets/           ← Put your dealer assets folder here
│   │   └── Dealership-panels/
│   │       ├── VW-dealers/
│   │       │   ├── VW-Dehradun/
│   │       │   │   ├── template.png
│   │       │   │   ├── logo-light.png
│   │       │   │   └── logo-dark.png
│   │       │   └── VW-Haldawani/
│   │       │       └── ...
│   │       └── Tata-dealers/
│   │           └── ...
│   ├── static/           ← Auto-created. Generated PNGs land here
│   └── uploads/          ← Auto-created. Uploaded background images go here
└── frontend/
    ├── app/
    │   ├── page.tsx      ← Main UI
    │   ├── layout.tsx
    │   └── globals.css
    ├── package.json
    └── next.config.ts
```

---

## Local Setup

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- npm

---

### 1. Clone the repo

```bash
git clone https://github.com/your-username/creativepilot-ai.git
cd creativepilot-ai
```

---

### 2. Add your assets

The backend expects a folder called `assets` inside the `backend/` directory with the dealer panels and logos. The structure should look like this:

```
backend/assets/Dealership-panels/VW-dealers/VW-Dehradun/
    template.png
    logo-light.png
    logo-dark.png
```

If you received an `assets.zip`, just extract it inside `backend/`:

```bash
cd backend
unzip assets.zip
```

Make sure the final path resolves to `backend/assets/Dealership-panels/...` that's where the code looks.

---

### 3. Backend setup

```bash
cd backend

# create a virtual environment
python -m venv venv

# activate it
# on Windows:
venv\Scripts\activate
# on Mac/Linux:
source venv/bin/activate

# install the dependencies (just three packages)
pip install -r requirements.txt

# start the server
python app.py
```

The Flask server starts at `http://127.0.0.1:5000`. You'll see a message confirming the working directory in the terminal. The `uploads/` and `static/` folders are created automatically on first run you don't need to do anything.

---

### 4. Frontend setup

Open a second terminal window and run:

```bash
cd frontend

# install dependencies
npm install

# start the dev server
npm run dev
```

The app opens at `http://localhost:3000`.

---

### 5. Use the app

1. Go to `http://localhost:3000`
2. Choose a brand (Volkswagen or Tata)
3. Select a dealer from the list
4. Upload a background image (JPG or PNG)
5. Click **Generate Creative**
6. Preview the output click the image to download it, or use **Download All (ZIP)** if you generated for multiple dealers

---

## Deploying to Vercel

The **frontend** deploys to Vercel as a standard Next.js app. The **backend** (Flask) needs to run separately since Vercel only handles Node-based runtimes the simplest free option is **Render**.

---

### Deploy the Backend to Render

1. Go to [https://render.com](https://render.com) and create a free account
2. Click **New → Web Service**
3. Connect your GitHub repo and set the **Root Directory** to `backend`
4. Fill in the following settings:

   | Field | Value |
   |---|---|
   | Environment | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app` |

5. Add `gunicorn` to your `requirements.txt` before deploying:

   ```
   flask
   flask-cors
   pillow
   gunicorn
   ```

6. Hit **Create Web Service** Render gives you a public URL like `https://creativepilot-backend.onrender.com`

> **Important:** Render's free tier will spin down after 15 minutes of inactivity. The first request after that takes ~30 seconds to wake up. That's fine for demos just click Generate and wait a moment if it's cold starting.

---

### Update the Frontend API URL

Before you deploy the frontend, update the API base URL in `frontend/app/page.tsx`. Look for the line where the fetch call points to `127.0.0.1:5000` and replace it with your Render URL:

```ts
// change this:
const response = await fetch("http://127.0.0.1:5000/generate", { ... })

// to this:
const response = await fetch("https://your-render-app.onrender.com/generate", { ... })
```

---

### Deploy the Frontend to Vercel

1. Go to [https://vercel.com](https://vercel.com) and sign in with GitHub
2. Click **Add New → Project**
3. Import your repository
4. Set the **Root Directory** to `frontend`
5. Vercel will auto-detect it as a Next.js project leave the build settings as-is
6. Click **Deploy**

Your app will be live at something like `https://creativepilot-ai.vercel.app` in about a minute.

---

### Environment Variables (optional)

If you want to avoid hardcoding the backend URL, you can use a Next.js environment variable instead. Create a file called `.env.local` inside the `frontend/` folder:

```
NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com
```

Then in your code, reference it as:

```ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000"
```

On Vercel, go to **Settings → Environment Variables** and add `NEXT_PUBLIC_API_URL` with the Render URL so it picks it up during build.

---

## AI Features

**Brightness-based logo selection** before placing the logo, the backend converts the background image to grayscale and computes the average pixel value. If it's below 128 (darker image), it uses the light-colored logo. Otherwise it uses the dark one. This avoids logos disappearing into the background.

**Panel placement detection** the app splits the image into top and bottom thirds, checks the variance (how visually busy each region is), and places the dealer panel in the cleaner, less busy area. This keeps the panel from overlapping the car or the main subject.

**Center-crop scaling** when resizing to the target format, the image is scaled up so it fills the frame entirely, then center-cropped. This means no white bars, no stretching the photo always fills the canvas.

---

## Dependencies

**Backend**
- Flask: API server
- Flask-CORS: handles cross-origin requests from the frontend
- Pillow: all image operations (resize, crop, paste, brightness analysis)

**Frontend**
- Next.js 15 with the App Router
- TypeScript
- Tailwind CSS

No database. No external AI APIs. Everything runs locally or on the two free hosting services above.
