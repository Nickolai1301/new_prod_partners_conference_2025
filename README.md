# Partners Conference 2025 - GenAI Competition App

Application for 2025 partners conference demonstrating GenAI prompt engineering and M&A analysis capabilities.

## 🚀 Overview

This Streamlit application provides an interactive learning environment where partners can practice prompt engineering skills using realistic M&A case studies. The app combines AI-powered business analysis with intelligent prompt evaluation to create a comprehensive learning experience.

## 📋 How It Works

### 1. **User Journey**
- **Team Selection**: Users select their industry (Health, Technology, Gas, Finance, Retail, Manufacturing, Energy)
- **Case Study Access**: View detailed M&A case study (TechCorp acquisition scenario)
- **Prompt Submission**: Enter prompts to analyze the business case (3 submissions per session)
- **AI Analysis**: Receive professional M&A analysis based on their prompt + case study context
- **Prompt Evaluation**: Get detailed feedback on prompt quality and improvement suggestions
- **Leaderboard**: View competition standings across all teams

### 2. **Backend Workflow**
```
User Prompt + Case Study → OpenAI GPT-4 → AI Business Analysis
              ↓
User Prompt → Evaluation System → Quality Scores & Feedback
```

## 🏗️ Architecture

### **Core Files:**

#### `app.py` - Main Application
- **Streamlit Interface**: Handles UI, navigation, and user interactions
- **AI Integration**: Combines user prompts with case study context for OpenAI analysis
- **Session Management**: Tracks submissions, teams, and application state
- **Results Display**: Shows AI responses and evaluation feedback side-by-side

**Key Functions:**
- `generate_ai_response()`: Sends prompt + case study to OpenAI for business analysis
- Session state management for multi-page navigation
- Real-time terminal output capture and display

#### `evaluation.py` - Prompt Quality Assessment
- **LLM-Powered Evaluation**: Uses OpenAI to assess prompt quality
- **Scoring System**: Evaluates 4 criteria (25% each):
  - **Clarity**: How understandable is the prompt?
  - **Specificity**: How detailed are the requirements?
  - **Context**: How well does it provide background?
  - **Structure**: How well-organized is it?
- **Feedback Generation**: Provides actionable improvement suggestions

**Key Classes:**
- `PromptEvaluator`: Main evaluation engine
- `PromptEvaluation`: Data structure for storing results

#### `feedback_tone.txt` - Evaluation Personality
- **Tone Configuration**: Defines the evaluation feedback style
- **Encouraging Approach**: Makes learning feel positive and achievable
- **Dynamic Loading**: Automatically loaded by evaluation system
- **Customizable**: Easy to modify feedback personality

**Current Tone**: Cheerful, encouraging, confidence-building coach style

## 🎯 Features

### **For Participants:**
- **Interactive Case Study**: Realistic M&A acquisition scenario
- **AI-Powered Analysis**: Professional business insights using GPT-4
- **Instant Feedback**: Real-time prompt quality evaluation
- **Learning Support**: Constructive suggestions for improvement
- **Competition Element**: Leaderboard and scoring system

### **For Administrators:**
- **Session Tracking**: Monitor user activity and submissions
- **System Logs**: Background process visibility
- **Easy Customization**: Modify case study, tone, or evaluation criteria
- **Scalable**: Supports multiple teams and industries

## 🛠️ Setup & Installation

### **Prerequisites:**
```bash
python 3.10+
OpenAI API key
```

### **Installation:**
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
# Edit .env file and add: OPENAI_API_KEY=your_key_here

# Run application
streamlit run app.py
```

### **Environment Variables:**
- `OPENAI_API_KEY`: Required for AI analysis and evaluation

## 📊 Technical Details

### **Data Flow:**
1. **User Input** → Streamlit interface captures prompt
2. **AI Generation** → `app.py` sends prompt + case study to OpenAI
3. **Evaluation** → `evaluation.py` assesses original prompt quality
4. **Feedback Tone** → `feedback_tone.txt` styles the evaluation response
5. **Display** → Results shown in split-screen format

### **Session State Management:**
- Team selection and navigation tracking
- Submission counting (3 per session)
- AI response and evaluation storage
- Terminal output capture
- Leaderboard data persistence

### **Error Handling:**
- Graceful OpenAI API failure management
- Fallback evaluation responses
- Missing file handling (feedback tone)

## 🎨 Customization

### **Modify Case Study:**
Edit the `case_study_content` variable in `app.py`

### **Change Evaluation Tone:**
Update `feedback_tone.txt` with new personality guidelines

### **Adjust Scoring:**
Modify evaluation criteria weights in `evaluation.py`

### **UI Styling:**
Update HTML/CSS in Streamlit markdown sections

## 🏆 Competition Features

- **Industry-based Teams**: 7 different industry contexts
- **Scoring System**: 0-100 point evaluation scale
- **Leaderboard**: Real-time competition standings
- **Limited Submissions**: 3 attempts per session to encourage quality
- **Professional Context**: Realistic M&A business scenarios

## 📈 Benefits

- **Skill Development**: Improves prompt engineering capabilities
- **Business Context**: Realistic consulting scenarios
- **Immediate Feedback**: Learn and iterate quickly
- **Competitive Element**: Engaging gamification
- **Professional Growth**: Relevant to consulting work

---

*Built for Deloitte Partners Conference 2025 - Demonstrating the power of GenAI in business analysis and learning.*
