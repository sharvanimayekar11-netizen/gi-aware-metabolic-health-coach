# GI-Aware Metabolic Health Coach

A rule-based Streamlit app that predicts metabolic risk (prediabetes, fatty liver,
metabolic syndrome) and generates a personalized, Glycemic-Index-aware diet and
exercise plan for sedentary tech workers.

## Project Structure
```
metabolic_coach/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── data/
│   ├── food_db.csv        # GI-tagged Indian food database
│   └── exercise_db.csv    # Desk-worker exercise database
└── README.md
```

## Run It Locally

1. Install Python 3.9+ if you don't have it.
2. Open a terminal in this folder and install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run app.py
   ```
4. It opens automatically at `http://localhost:8501`.

## How to Extend This Project

- **Grow the food database:** add more rows to `data/food_db.csv`. Keep the same
  columns. You can pull more items from Kaggle's "Indian Food Nutrition Dataset" or
  the IFCT (Indian Food Composition Tables) for accurate GI values.
- **Grow the exercise database:** add more rows to `data/exercise_db.csv`.
- **Tune the risk score:** edit the `calculate_risk_score()` function in `app.py` —
  add/remove weighted factors as you like.
- **Add more conditions:** the risk score currently returns one overall band. You can
  add separate scoring functions per condition (e.g. `fatty_liver_score()`,
  `hypertension_score()`) and show them as separate cards on the dashboard.

## Deploy It Live (Step 4 of your project)

1. **Create a GitHub repo** and push this whole folder to it:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
3. Click **"New app"**, select your repository, branch (`main`), and set the main file
   path to `app.py`.
4. Click **Deploy**. Within ~2 minutes you'll get a public URL like
   `your-metabolic-app.streamlit.app` — this is the link you put in your project
   presentation.

## Notes for Your Submission

- The `Meal_Type` column (Breakfast/Lunch/Dinner/Snack) was added to the food CSV
  beyond the original spec so the meal-matching logic can reliably build a full
  1-day plan — mention this as a design decision if asked.
- The app includes a disclaimer that it's an educational tool, not medical advice —
  good practice to keep for any health-related project.
