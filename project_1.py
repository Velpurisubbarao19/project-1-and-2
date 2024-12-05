# -*- coding: utf-8 -*-
"""project_1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1i7TmVq3alZ06msJWiYhtA6ScvaRk53Ax
"""

# Import Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ydata_profiling import ProfileReport  # Updated to ydata_profiling
import sweetviz as sv
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Load the Telco customer churn dataset into a DataFrame
data = pd.read_csv('telco-customer-churn.csv')

# 1. Data Preparation
# Check for missing values
missing_values = data.isnull().sum()
print("Missing values per column:\n", missing_values)

# Handle missing values (example: fill or drop)
data['TotalCharges'] = pd.to_numeric(data['TotalCharges'], errors='coerce')
data.dropna(inplace=True)  # Dropping rows with missing values in 'TotalCharges'

print("Columns in the dataset:", data.columns)

# Check if 'Tenure' exists, otherwise correct or skip this step
numerical_features = ['Tenure', 'MonthlyCharges', 'TotalCharges']
for feature in numerical_features:
    if feature in data.columns:  # Ensure the feature exists in the dataset
        z_scores = np.abs((data[feature] - data[feature].mean()) / data[feature].std())
        data = data[z_scores < 3]
    else:
        print(f"Feature '{feature}' not found in the dataset.")

# We filter out any values where Z-score is greater than 3 (beyond 3 standard deviations from the mean)
for feature in numerical_features:
    z_scores = np.abs((data[feature] - data[feature].mean()) / data[feature].std())
    data = data[z_scores < 3]  # Keeping only rows where z_score < 3

# Convert categorical features to numerical using one-hot encoding
# This ensures that categorical data like 'gender' or 'InternetService' is handled correctly
data = pd.get_dummies(data, drop_first=True)

# 2. Data Types

# Let's take a quick look at the data types of each column after our transformations
data_types = data.dtypes
print("Data types:\n", data_types)

numeric_data = data.select_dtypes(include=[np.number])

corr_matrix = numeric_data.corr()
print(corr_matrix)

plt.figure(figsize=(10, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Matrix')
plt.show()

# Feature Importance using Logistic Regression
# We'll fit a logistic regression model to get an understanding of which features are most important in predicting churn

X = data.drop('Churn_Yes', axis=1)  # 'Churn_Yes' is our target (dependent variable)
y = data['Churn_Yes']

# Instantiate and fit the model
log_model = LogisticRegression(max_iter=1000)
log_model.fit(X, y)

# Extracting the coefficients (importance) of each feature and sorting them
feature_importance = pd.Series(log_model.coef_[0], index=X.columns).sort_values(ascending=False)
print("Feature importance:\n", feature_importance)

# Instantiate and train the Logistic Regression model
model = LogisticRegression(max_iter=1000)  # Ensure max_iter is high to avoid convergence issues
model.fit(X, y)  # X is your feature set, y is the target variable

# Extract and sort feature importance
feature_importance = pd.Series(model.coef_[0], index=X.columns).sort_values(ascending=False)
print(feature_importance)  # Check if this prints the correct values

# Plot the top 20 features by importance
top_n = 20
plt.figure(figsize=(10, 6))
feature_importance.head(top_n).plot(kind='bar', color='teal')
plt.title(f'Top {top_n} Feature Importance from Logistic Regression')
plt.xlabel('Features')
plt.ylabel('Importance')
plt.xticks(rotation=45)
plt.show()

# 4. Data Splitting and SweetViz Comparison Report
# Split the dataset into training and testing sets (80% training, 20% testing)
train, test = train_test_split(data, test_size=0.2, random_state=42)

print(train.columns)
print(test.columns)

# Clean column names by stripping whitespace and replacing special characters
train.columns = train.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)
test.columns = test.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)

# Step 4: Check the actual columns in both datasets before attempting to drop
print("Training Data Columns:")
print(train.columns.tolist())

print("\nTest Data Columns:")
print(test.columns.tolist())

# Use errors='ignore' to avoid KeyError
train_filtered = train.drop(columns=["customerid"], errors='ignore')
test_filtered = test.drop(columns=["customerid"], errors='ignore')

# Verify columns after dropping
print("Columns in Training Data after drop:")
print(train_filtered.columns.tolist())

print("\nColumns in Test Data after drop:")
print(test_filtered.columns.tolist())

# Replace 'Churn_Yes' with the exact name found in Step 3
X_train = train.drop('churn_yes', axis=1)  # Adjust if different
y_train = train['churn_yes']                 # Adjust if different
X_test = test.drop('churn_yes', axis=1)     # Adjust if different
y_test = test['churn_yes']                   # Adjust if different

# Check for NaN or infinite values
print("Checking for NaN values:")
print(X_train.isna().sum())

print("\nChecking for infinite values:")
print(np.isinf(X_train).sum())

# Summary statistics of the training set
print(X_train.describe())

# Option 1: Fill NaN values with the mean or median
X_train.fillna(X_train.mean(), inplace=True)
X_test.fillna(X_test.mean(), inplace=True)

# Option 2: Drop rows with NaN or infinite values
# X_train.dropna(inplace=True)
# X_test.dropna(inplace=True)

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Re-train the logistic regression model on the scaled training data
log_reg = LogisticRegression(max_iter=1000)
log_reg.fit(X_train_scaled, y_train)

logreg = LogisticRegression(max_iter=1000, C=1e-4)
log_reg.fit(X_train_scaled, y_train)

log_reg = LogisticRegression(max_iter=2000, solver='lbfgs')
log_reg.fit(X_train_scaled, y_train)

X_train = X_train.astype(np.float64)
X_test = X_test.astype(np.float64)

# Scale the test set using the same scaler
X_test_scaled = scaler.transform(X_test)

# Convert X_test_scaled to NumPy array if necessary (but it usually won't be needed)
y_pred = log_reg.predict(X_test_scaled)

# Assuming you have already fitted the model with X_train (as a NumPy array)
y_pred = log_reg.predict(X_test.to_numpy())  # Convert DataFrame to NumPy array

print(y_train.value_counts())

from sklearn.linear_model import LogisticRegression

log_reg = LogisticRegression(max_iter=2000, class_weight='balanced')
log_reg.fit(X_train_scaled, y_train)

# Initialize Logistic Regression with class weights
log_reg = LogisticRegression(max_iter=2000, class_weight='balanced')

# Fit the model
log_reg.fit(X_train_scaled, y_train)

# Predict on the test set
y_pred = log_reg.predict(X_test_scaled)

# Evaluate the model
print("Classification Report:\n", classification_report(y_test, y_pred))
print("Accuracy Score:", accuracy_score(y_test, y_pred))

