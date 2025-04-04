import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

# Load dataset
df = pd.read_csv("india_e_waste_prediction_dataset.csv")

# Train models for each state
models = {}
for state in df["State"]:
    state_data = df[df["State"] == state].drop(columns=["State"]).T
    years = state_data.index.astype(int).values.reshape(-1, 1)
    e_waste = state_data.values.flatten()
    
    model = LinearRegression()
    model.fit(years, e_waste)
    models[state] = model

# Save trained models
joblib.dump(models, "e_waste_models.pkl")

print("Model training complete! Saved as 'e_waste_models.pkl'.")
