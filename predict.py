import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, r2_score


df = pd.read_csv("product.csv")  


X = df[["Age", "Condition", "Original Price"]]
y = df["Resale Price"]


categorical_features = ["Condition"]
numeric_features = ["Age", "Original Price"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(), categorical_features)
    ]
)


model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model.fit(X_train, y_train)


y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model Evaluation:")
print(f"Mean Absolute Error (MAE): ₹{mae:.2f}")
print(f"R² Score: {r2:.4f}")

sample_input = pd.DataFrame([[3, "Good", 50000]], columns=["Age", "Condition", "Original Price"])
predicted_price = model.predict(sample_input)
print(f"Predicted Resale Price: ₹{predicted_price[0]:.2f}")

# Save the trained model
# joblib.dump(model, "used_electronics_price_model.pkl")
# print("Model saved as 'used_electronics_price_model.pkl'")

# Load model for future use
# loaded_model = joblib.load("used_electronics_price_model.pkl")
