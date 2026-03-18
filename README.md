# Bug Severity Predictor

Python | Machine Learning | NLP | Flask | Random Forest | Full Stack | REST API

## Project Overview

Bug Severity Predictor is a Machine Learning based web application that automatically predicts the severity level of software bugs using bug reports and related metadata. This system helps developers prioritize critical bugs efficiently and improves software maintenance workflows.

The project combines Natural Language Processing (TF-IDF) with structured bug metadata and uses a Random Forest classifier to generate accurate severity predictions through an interactive web dashboard.

## Features

• Machine learning based bug severity prediction  
• NLP analysis of bug descriptions  
• Metadata based prediction support  
• REST API backend using Flask  
• Interactive web dashboard  
• Real time prediction results  
• Bug severity analytics visualization  
• Prediction history tracking  
• Model pipeline integration  

## Tech Stack

### Backend
• Python  
• Flask  
• Scikit-learn  
• Pandas  
• NumPy  
• Joblib  

### Machine Learning
• TF-IDF Vectorizer  
• Random Forest Classifier  
• One Hot Encoding  
• StandardScaler  
• Scikit-learn Pipeline  

### Frontend
• HTML  
• CSS  
• JavaScript  
• Bootstrap  
• Chart.js  

### Tools
• Git  
• GitHub  
• VS Code  

## Methodology

### Data Collection & Cleaning

Bug reports are collected and preprocessed by removing duplicate entries, handling missing values, and cleaning textual descriptions. Both text and structured metadata are prepared for model training.

### Text Feature Extraction

TF-IDF Vectorizer converts bug descriptions into numerical vectors by identifying important keywords and reducing noise.

### Feature Engineering

Categorical data such as product name, component, status, and resolution are encoded using One Hot Encoding. Numerical features such as votes and comments are normalized using StandardScaler.

### Model Training

A Random Forest Classifier is trained using processed features to learn patterns and classify bug severity levels accurately.

### Backend Integration

The trained ML pipeline is deployed using Flask APIs to process prediction requests.

### Frontend Visualization

A web dashboard collects user inputs and displays predictions instantly. Chart.js is used for severity analytics visualization.

## System Architecture

User Input → Frontend Dashboard → Flask API → ML Pipeline → Severity Prediction → Analytics Dashboard

## API Endpoints

### Predict Severity

POST /predict

Example input:
{
"product_name": "FIREFOX",
"component_name": "UI",
"resolution_category": "fixed",
"status_category": "closed",
"short_description": "App crashes when saving",
"long_description": "Click Save causes crash",
"quantity_of_votes": 0,
"quantity_of_comments": 1
}
Response:


{
"status": "success",
"predicted_severity": "major"
}


## Installation Guide

### Clone repository


git clone 


### Backend setup


cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python app.py


### Frontend setup


cd frontend

python -m http.server 8000


Open:


http://127.0.0.1:8000


## Model Training

To retrain model:


cd backend

python train_model.py


## Testing


python test_predict.py


## Future Scope

• Add Deep Learning models like BERT  
• Improve accuracy using hyperparameter tuning  
• Cloud deployment  
• Integration with Jira/GitHub bug trackers  
• Real time bug monitoring  
• CI/CD integration  

## Learning Outcomes

• Built end-to-end ML pipeline  
• Learned NLP feature extraction  
• Backend API integration  
• Frontend visualization  
• Model deployment basics  
• Full stack ML application development  



## Author

Samrudhi Chougule

If you like this project feel free to star the repository.