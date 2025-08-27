# InsightAI - AI-Powered Data Analytics SaaS Platform

 **Production-ready AI SaaS Starter Kit** for data science teams, analytics dashboards, and business intelligence platforms.

## Features

### Core Functionality
- 🔐 **JWT Authentication** - Secure user management
- 📊 **CSV Data Upload** - Drag & drop interface with previews
- 🤖 **AutoML Pipeline** - Classification, Regression, Clustering
- 📈 **Interactive Visualizations** - Charts, confusion matrices, ROC curves
- 🧠 **AI-Generated Insights** - GPT-4 powered analysis
- 📄 **Report Export** - PDF and CSV downloads
- 🌙 **Dark Mode** - Responsive design with theme toggle

### Advanced Features
- 🔍 **Data Preprocessing** - Auto-detect types, handle missing values
- 📊 **Model Performance** - Accuracy, RMSE, Silhouette scores
- 🎯 **Best Model Selection** - Scikit-learn and LazyPredict integration
- 📱 **Mobile Responsive** - Modern UI with Tailwind CSS

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Pandas** - Data manipulation and analysis
- **Scikit-learn** - Machine learning algorithms
- **LazyPredict** - Automated model selection
- **Pydantic** - Data validation
- **SQLite** - Database (easily switchable to PostgreSQL)
- **JWT** - Authentication

### Frontend
- **React** - Modern UI framework
- **Tailwind CSS** - Utility-first styling
- **Chart.js** - Interactive visualizations
- **Axios** - HTTP client

### AI & Analytics
- **OpenAI GPT-4** - Insight generation
- **Plotly** - Advanced charts
- **PyMuPDF** - PDF report generation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd InsightAI
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Configuration**
```bash
# Backend (.env)
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./insightai.db

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

5. **Run the Application**
```bash
# Backend (Terminal 1)
cd backend
uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd frontend
npm run dev
```

Visit `http://localhost:5173` to access the application.

## 📁 Project Structure

```
InsightAI/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── upload.py
│   │   │   ├── ml.py
│   │   │   └── reports.py
│   │   ├── services/
│   │   │   ├── ml_service.py
│   │   │   ├── report_service.py
│   │   │   └── llm_service.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── dataset.py
│   │   └── utils/
│   │       ├── auth.py
│   │       └── data_processing.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── assets/
│   ├── package.json
│   └── .env
└── README.md
```

## 🎯 Use Cases

- **No-code AutoML Dashboards** - Enable non-technical users to run ML models
- **Internal Analytics SaaS** - Business intelligence for teams
- **Freelancer Toolkit** - Client reporting and analysis
- **AI-powered BI Platforms** - Enterprise analytics solutions

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Data Management
- `POST /upload/csv` - Upload CSV dataset
- `GET /datasets` - List user datasets
- `GET /datasets/{id}` - Get dataset details

### Machine Learning
- `POST /ml/train` - Train ML model
- `GET /ml/results/{id}` - Get model results
- `GET /ml/insights/{id}` - Get AI-generated insights

### Reports
- `GET /reports/{id}/pdf` - Download PDF report
- `GET /reports/{id}/csv` - Download CSV results

## 🎨 UI Components

- **Dashboard** - Overview of datasets and models
- **Upload Interface** - Drag & drop CSV upload with preview
- **Model Selection** - Interactive task and algorithm selection
- **Results Visualization** - Charts, metrics, and insights
- **Report Generation** - Export functionality

## 🔐 Security Features

- JWT-based authentication
- Input validation and sanitization
- Rate limiting
- CORS configuration
- Secure file upload handling

## 📊 ML Pipeline

1. **Data Upload** - CSV parsing and validation
2. **Preprocessing** - Type detection, missing value handling
3. **Task Selection** - Classification, Regression, Clustering
4. **Model Training** - Automated algorithm selection
5. **Evaluation** - Performance metrics calculation
6. **Visualization** - Charts and plots generation
7. **Insight Generation** - AI-powered analysis
8. **Report Export** - PDF/CSV download

## 🚀 Deployment

### Backend (FastAPI)
```bash
# Production with Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend (React)
```bash
# Build for production
npm run build

# Serve with nginx or similar
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support, email webcodelabb@gmail.com or create an issue in the repository.

---

**Built with ❤️ for the AI/ML community** 
