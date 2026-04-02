# TrackerX Live

TrackerX Live is a small Streamlit web app version of the expense tracker in this folder.

## Run locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Deploy for a public link

### Option 1: Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Go to `https://share.streamlit.io/`.
3. Choose the repo and set the main file to `app.py`.
4. Deploy and copy the public link.

### Option 2: Render

1. Push this folder to GitHub.
2. Create a new Web Service on Render.
3. Use these settings:

```text
Build command: pip install -r requirements.txt
Start command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Files

- `app.py`: web app
- `expenses.csv`: data file
- `TrackerX`: original Tkinter desktop app
