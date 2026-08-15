# ChurnGuard — Customer Churn Intelligence Platform

A web-based analytics platform for predicting and analyzing customer churn in the telecommunications industry. Built with Flask and scikit-learn, it provides an interactive dashboard, a churn prediction tool, and a data explorer — enabling data-driven customer retention decisions.

## Key Features

- **Analytics Dashboard** — KPI cards and interactive charts visualizing churn patterns by contract type, internet service, tenure, and payment method
- **Churn Prediction** — Form-based prediction tool using a Random Forest Classifier with real-time confidence scoring and risk assessment
- **Data Explorer** — Browse, filter, sort, and paginate through 7,000+ customer records with CSV export
- **Feature Importance** — Visual breakdown of the top factors driving customer churn
- **Input Validation** — Server-side validation with meaningful error messages for all prediction inputs
- **Responsive Design** — Mobile-friendly layout with collapsible sidebar navigation
- **Modular Architecture** — Clean separation of ML model, data service, routes, and templates

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| ML Model | scikit-learn (Random Forest Classifier) |
| Data Processing | pandas, NumPy |
| Frontend | HTML5, CSS3 (custom design system), JavaScript |
| Charts | Chart.js |
| Configuration | python-dotenv |

## Project Architecture

```
ChurnGuard/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Environment-based configuration
│   ├── routes.py            # Route handlers & API endpoints
│   ├── ml_model.py          # ML model wrapper with validation
│   ├── data_service.py      # Dataset analytics & filtering
│   ├── static/
│   │   ├── css/style.css    # Custom CSS design system
│   │   └── js/main.js       # Chart rendering & UI interaction
│   └── templates/
│       ├── base.html        # Base layout with navigation
│       ├── dashboard.html   # Analytics dashboard
│       ├── predict.html     # Churn prediction form
│       └── explorer.html    # Data explorer with filters
├── data/
│   └── telco_churn.csv      # IBM Telco Customer Churn dataset
├── model/
│   ├── train_model.py       # Model training script
│   └── churn_model.pkl      # Trained model artifact
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
└── .gitignore
```

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/churnguard.git
cd churnguard

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | Flask session secret key | `dev-secret-key-...` |
| `MODEL_PATH` | Path to trained model file | `model/churn_model.pkl` |
| `DATA_PATH` | Path to dataset CSV | `data/telco_churn.csv` |

## Usage

```bash
# Retrain the model (optional — pre-trained model is included)
python model/train_model.py

# Run the application
python run.py

# Open in browser
# http://127.0.0.1:5000
```

## Dataset

IBM Telco Customer Churn dataset — 7,043 customer records with 21 attributes including demographics, services subscribed, account information, and churn status.

## Future Improvements

- Batch prediction via CSV file upload
- User authentication and role-based access
- Model comparison dashboard (Random Forest vs. Logistic Regression vs. XGBoost)
- Customer segmentation using clustering algorithms
- REST API with Swagger documentation for external integrations

---

Built by **Rakesh** | BCA — Artificial Intelligence & Data Science
