# Resume Analyzer AI

An intelligent resume analysis system that leverages multiple AI models to provide comprehensive insights, scoring, and improvement suggestions for resumes against specific job descriptions.

## Features

### **Smart Resume Analysis**
- **AI-Powered Scoring**: Overall fit score (0-100) based on job requirements
- **Skills Gap Analysis**: Identifies missing and matching skills
- **Experience Evaluation**: Analyzes experience relevance and gaps
- **ATS Optimization**: Provides recommendations for Applicant Tracking Systems

### **Advanced Document Processing**
- **PDF Text Extraction**: Supports text-based PDF parsing with PyMuPDF
- **OCR Integration**: Extracts text from image-based PDFs using Tesseract
- **Intelligent Chunking**: Sections resume by categories (Experience, Skills, Education)
- **Multi-format Support**: PDF, DOC, TXT, and image files

### **LLM Integration**
- **OpenRouter API**: Access to AI models (Gemini Flash, Qwen, etc.)
- **Fallback System**: Primary and backup LLM configuration
- **Structured Responses**: Pydantic models for consistent output formatting

### **Modern User Interface**
- **Responsive Design**: Built with React and Tailwind CSS
- **Drag & Drop Upload**: Intuitive file upload experience
- **Real-time Feedback**: Progress indicators and status updates
- **Professional UI**: ShadCN components for polished interface

## Tech Stack

### **Backend**
- **Framework**: FastAPI
- **AI Integration**: LangChain, OpenRouter API
- **Document Processing**: PyMuPDF, Tesseract OCR
- **Language**: Python 3.8+

### **Frontend**
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Components**: ShadCN UI library
- **Icons**: Lucide React
- **Markdown**: React Markdown with GFM support

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn package manager


## Backend Setup

### Clone the repository
git clone <repository-url>
cd resume-analyzer

### Navigate to backend directory
cd backend

### Create virtual environment
python -m venv venv

### Activate virtual environment
On Windows:
venv\Scripts\activate

On macOS/Linux:
source venv/bin/activate

### Install dependencies
pip install -r requirements.txt

### Set up environment variables
cp .env.example .env


## Frontend Setup

### Navigate to frontend directory
cd frontend

### Install dependencies
npm install

### Start development server
npm run dev


Application runs on `http://localhost:5173`

**Upload & Analyze**
- Drag and drop a resume PDF file
- Enter the job description in the text area
- Click "Analyze Resume" to get AI insights

## API Endpoints

### `POST /analyze-resume`
Analyzes resume against job description

**Request:**
- `file`: Resume file (PDF, DOC, TXT)
- `job_description`: Job posting text (Form field)

**Response:**
{
"analysis": {
"overall_fit_score": 75,
"missing_skills": ["Docker", "CI/CD"],
"matching_skills": ["Python", "FastAPI"],
"experience_gap": "Analysis text...",
"improvement_suggestions": ["Suggestion 1", "Suggestion 2"],
"suggested_bullet_points": {...},
"ats_optimization": ["Tip 1", "Tip 2"],
"confidence_score": "High"
}

## Project Structure
```
resume-analyzer/
├── backend/
│ ├── main.py # FastAPI application
│ ├── LLM.py # AI model integration
│ ├── RAG.py # Document processing
│ ├── requirements.txt # Python dependencies
│ └── uploads/ # Uploaded files storage
├── frontend/
│ ├── src/
│ │ ├── App.jsx # Main React component
│ │ ├── components/ui/ # ShadCN UI components
│ │ └── assets/ # Static assets
│ ├── package.json # Node.js dependencies
│ └── vite.config.js # Vite configuration
└── README.md
```


## Key Components

### **Resume Analysis Pipeline**
1. **Document Upload**: File validation and storage
2. **Text Extraction**: PyMuPDF + OCR fallback
3. **Content Chunking**: Section-based text organization
4. **AI Analysis**: Multi-LLM processing with structured prompts
5. **Results Formatting**: User-friendly output generation

### **AI Models Used**
- **Primary**: Google Gemini Flash 1.5 (via OpenRouter)
- **Fallback**: Qwen 3-14B (via OpenRouter)
- **Temperature**: 0.0 for deterministic analysis

## Features in Detail

### **Resume Scoring Algorithm**
- Skills matching percentage
- Experience relevance scoring
- Education alignment
- Keyword density analysis
- ATS compatibility rating

### **Improvement Suggestions**
- Missing skills identification
- Experience gap recommendations
- Resume formatting tips
- ATS optimization advice
- Industry-specific improvements

## Error Handling

- **File Upload Errors**: Size limits, format validation
- **API Failures**: Fallback model switching
- **Network Issues**: Retry mechanisms
- **User Feedback**: Clear error messages and status updates

## Performance Features

- **Async Processing**: Non-blocking file uploads
- **Progress Tracking**: Real-time upload progress
- **Efficient Parsing**: Optimized PDF processing
- **Responsive UI**: Fast user interactions







