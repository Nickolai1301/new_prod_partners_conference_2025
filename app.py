
import streamlit as st
from evaluation import PromptEvaluator
from openai import OpenAI
import os
from dotenv import load_dotenv
import sys
from io import StringIO
import contextlib
import pandas as pd
from db import init_db, update_team_score, get_leaderboard

# Load environment variables
load_dotenv()

# Access OpenAI API key from Streamlit secrets
# if "OPENAI_API_KEY" in st.secrets:
#     # Running on Streamlit Cloud or with .streamlit/secrets.toml
#     OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
# else:
#     # Running locally, get from .env
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)
# test

st.set_page_config(page_title="Competition Team App", page_icon="🤖", layout="wide")

# Team selection and navigation state
if "team" not in st.session_state:
    st.session_state["team"] = None
if "main" not in st.session_state:
    st.session_state["main"] = False
if "submissions_left" not in st.session_state:
    st.session_state["submissions_left"] = 3
if "show_case_study" not in st.session_state:
    st.session_state["show_case_study"] = False
if "show_leaderboard" not in st.session_state:
    st.session_state["show_leaderboard"] = False
if "evaluator" not in st.session_state:
    st.session_state["evaluator"] = PromptEvaluator()
if "terminal_output" not in st.session_state:
    st.session_state["terminal_output"] = []
if "last_evaluation" not in st.session_state:
    st.session_state["last_evaluation"] = None
if "last_ai_response" not in st.session_state:
    st.session_state["last_ai_response"] = None

# Initialize the SQLite database (only once)
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state["db_initialized"] = True

# Case Study Demo Content
case_study_content = """
# 📊 Demo Case Study: TechCorp Acquisition

## Background
TechCorp is a mid-sized fintech company specializing in digital payment solutions for small and medium enterprises (SMEs). The company has shown consistent growth over the past 3 years and is now considering strategic acquisition opportunities.

## Your Challenge
As a senior consultant, you've been asked to analyze the following acquisition scenario:

### Target Company: PayFlow Solutions
- **Industry**: Financial Technology
- **Revenue**: $45M annually (growing 25% YoY)
- **Employees**: 180 people
- **Key Product**: AI-powered invoice management platform
- **Market Position**: #3 in SME invoice automation space

"""

def generate_ai_response(user_prompt: str, industry: str) -> str:
    """Generate AI response using the case study context and user prompt"""
    try:
        # Combine case study with user prompt for context
        full_context = f"""
CASE STUDY CONTEXT:
{case_study_content}

USER PROMPT:
{user_prompt}

INDUSTRY CONTEXT: {industry}

Please provide a comprehensive business analysis response based on the case study context and the user's specific prompt above. Focus on actionable insights and professional recommendations suitable for a consulting environment.
"""
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {"role": "system", "content": "You are a senior M&A consultant providing expert analysis. Use the case study context to inform your response and provide detailed, actionable business insights."},
                {"role": "user", "content": full_context}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating AI response: {str(e)}"

if not st.session_state["main"] and not st.session_state["show_leaderboard"]:
    st.title("🎯 Welcome to the Prompt-Off: The Battle for Budget! 💥")


    # Insert homepage.txt content here, formatted for Streamlit
    homepage_content = """
<p>Think your industry group deserves a bigger slice of the pie? Ready to make the case for why your team should get extra investment from leadership?</p>
<p>Here’s your chance to prove it—<b>prompt-style</b>.</p>

<div style='margin-bottom:1em;'></div>
<h3 style='margin-bottom:0.2em;'>What is this?</h3>
<ul>
  <li>This is no ordinary pitch session. It’s a competitive, high-stakes, slightly sassy prompt showdown.</li>
  <li>Battle it out with your fellow Partners to craft the <b>strongest business case</b> for additional funding.</li>
</ul>

<h3 style='margin-bottom:0.2em;'>🔄 The Format</h3>
<ul>
  <li><b>Three chances</b> to write your business case prompt.</li>
  <li>After each of your first two submissions, you’ll receive <b>sassy, unfiltered feedback</b> to sharpen your thinking.</li>
  <li>On the third round, you’ll submit your <b>final prompt</b>—the one that hits the mark.</li>
</ul>

<h3 style='margin-bottom:0.2em;'>🧠 What’s the Ask?</h3>
<ul>
  <li>Craft a compelling prompt that answers:</li>
</ul>
<blockquote style='font-size:1.1em; color:#36a8f5; border-left:4px solid #36a8f5; margin:0 0 1em 0; padding:0.5em 1em;'>
  Why should your industry group receive additional investment from our leader?
</blockquote>
<ul>
  <li>Think <b>innovation</b>, <b>impact</b>, and <b>intention</b>.</li>
</ul>
"""

    homepage_content2 = """

<p>Think your industry group deserves a bigger slice of the pie? Ready to make the case for why your team should get extra investment from leadership?</p>
<p>Here’s your chance to prove it—<b>prompt-style</b>.</p>

<h3>What is this?</h3>
<ul>
    <li>This is no ordinary pitch session. It’s a competitive, high-stakes, slightly sassy prompt showdown.</li>
    <li>Battle it out with your fellow Partners to craft the <b>strongest business case</b> for additional funding.</li>
</ul>

<h3>🔄 The Format</h3>
<ul>
    <li><b>Three chances</b> to write your business case prompt.</li>
    <li>After each of your first two submissions, you’ll receive <b>sassy, unfiltered feedback</b> to sharpen your thinking.</li>
    <li>On the third round, you’ll submit your <b>final prompt</b>—the one that hits the mark.</li>
</ul>

<h3>🧠 What’s the Ask?</h3>
<ul>
    <li>Craft a compelling prompt that answers:</li>
</ul>
<blockquote style='font-size:1.1em; color:#36a8f5; border-left:4px solid #36a8f5; margin:0 0 1em 0; padding:0.5em 1em;'>
    Why should our industry group receive additional investment from our leader?
</blockquote>
<ul>
    <li>Your prompt should outline a clear, innovative, and impact-driven opportunity that will:</li>
    <ul>
        <li>Strengthen M&A services and relationships with key client accounts</li>
        <li>Unlock growth potential for your industry</li>
        <li>Position your group as a leader in delivering differentiated, future-focused M&A value</li>
    </ul>
</ul>

<h3>🏆 What Makes a Winning Prompt?</h3>
<ul>
    <li><b>Specific.</b> <b>Bold.</b> Grounded in reality—but aspirational.</li>
    <li>Shows how funding will turn strategy into action.</li>
    <li>Makes leadership sit up and say: “Now that’s something I want to back.”</li>
</ul>

<h3>💡 Bonus Tip</h3>
<ul>
    <li>Have fun with it—but don’t forget the real goal: winning hearts, minds, and budgets.</li>
</ul>

<p>Game on. Let’s see which industry brings the strongest case to the table. 🔥</p>
<p><b>Ready… set… PROMPT!</b></p>

"""

    st.markdown(homepage_content2, unsafe_allow_html=True)
    get_started = """<h3>🏃‍♂️Enter a team name and let's get started!</h3><p>Enter your team name and select your industry below, then click 'Get Started' to begin.</p>"""
    st.markdown(get_started, unsafe_allow_html=True)
    industry_list = ["Health", "Technology", "Gas", "Finance", "Retail", "Manufacturing", "Energy"]
    team_name = st.text_input("Custom Team Name:", max_chars=30, placeholder="e.g. Team_1")
    selected_industry = st.selectbox("Select your industry:", industry_list)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Get Started", type="primary", use_container_width=True):
            if not team_name.strip():
                st.warning("Please enter a team name before starting.")
            else:
                st.session_state["main"] = True
                st.session_state["team"] = f"{team_name.strip()} ({selected_industry})"
                st.session_state["show_leaderboard"] = False
    with col2:
        if st.button("🏆 Leaderboard Page", type="secondary", use_container_width=True):
            st.session_state["show_leaderboard"] = True
            st.session_state["main"] = False

    st.markdown("---")
    st.markdown("Built for the seminar competition.")

elif st.session_state["show_leaderboard"]:
    st.title("🏆 Competition Leaderboard")
    st.markdown("### Current standings for all teams across industries")

    # Back button
    if st.button("← Back to Home", type="secondary"):
        st.session_state["show_leaderboard"] = False
        st.session_state["main"] = False
        st.rerun()

    st.markdown("---")

    # Fetch leaderboard from SQLite DB
    leaderboard = get_leaderboard()
    leaderboard_rows = [
        {"Team": row[0], "Best Score": row[1], "Last Submission": row[2]} for row in leaderboard
    ]
    df = pd.DataFrame(leaderboard_rows)
    st.dataframe(df, use_container_width=True, height=400)

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Teams", len(df))
    with col2:
        st.metric("Average Score", f"{df['Best Score'].mean():.0f}" if not df.empty else "0")
    with col3:
        st.metric("Most Recent Submission", str(df['Last Submission'].max()) if not df.empty else "-")

    st.markdown("---")
    st.markdown("*Leaderboard updates in real-time during the competition*")
    st.markdown("Built for the seminar competition.")

elif st.session_state["main"] and not st.session_state["show_leaderboard"]:
    st.title(f"Main Page - {st.session_state['team']}")
    st.markdown("---")
    st.markdown(case_study_content)
    st.markdown("---")
    
    # # Show Case Study button at the top of main page
    # col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    #     if st.button("📚 Show Case Study", type="secondary", use_container_width=True):
    #         st.session_state["show_case_study"] = True

    # # Case Study Modal/Popup
    # if st.session_state["show_case_study"]:
    #     with st.container():
    #         st.markdown("---")
    #         col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    #         with col2:
    #             st.markdown(
    #                 """
    #                 <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 2px solid #36a8f5; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
    #                 """,
    #                 unsafe_allow_html=True
    #             )
    #             st.markdown(case_study_content)
    #             if st.button("❌ Close Case Study", type="primary"):
    #                 st.session_state["show_case_study"] = False
    #                 st.rerun()
    #             st.markdown("</div>", unsafe_allow_html=True)
    #         st.markdown("---")
    
    st.markdown("Enter your prompt below and submit to see the AI response.")
    st.info(f"Submissions left: {st.session_state['submissions_left']}")
    user_prompt = st.text_area("Prompt:", height=100, placeholder="Type your question or prompt here...")
    submit_disabled = st.session_state["submissions_left"] == 0
    submit = st.button("Submit Prompt", type="primary", disabled=submit_disabled)
    if submit:
        if not user_prompt.strip():
            st.warning("Please enter a prompt before submitting.")
        else:
            st.session_state["submissions_left"] -= 1
            
            # Capture terminal output during processing
            @contextlib.contextmanager
            def capture_terminal_output():
                stdout_backup = sys.stdout
                stderr_backup = sys.stderr
                stdout_capture = StringIO()
                stderr_capture = StringIO()
                try:
                    sys.stdout = stdout_capture
                    sys.stderr = stderr_capture
                    yield stdout_capture, stderr_capture
                finally:
                    sys.stdout = stdout_backup
                    sys.stderr = stderr_backup
            
            # Step 1: Generate AI response using case study + user prompt
            with st.spinner("🤖 Generating AI response based on case study..."):
                with capture_terminal_output() as (stdout_capture, stderr_capture):
                    ai_response = generate_ai_response(user_prompt, st.session_state["team"])
                
                # Store AI response
                st.session_state["last_ai_response"] = ai_response
                
                # Capture terminal output from AI generation
                terminal_output = stdout_capture.getvalue() + stderr_capture.getvalue()
                if terminal_output.strip():
                    st.session_state["terminal_output"].append(f"[AI Generation] {terminal_output.strip()}")
            
            # Step 2: Evaluate the AI-generated response
            with st.spinner("📊 Evaluating AI response quality..."):
                with capture_terminal_output() as (stdout_capture, stderr_capture):
                    evaluation = st.session_state["evaluator"].evaluate_prompt(
                        ai_response,
                        st.session_state["team"]
                    )
                
                # Store evaluation
                st.session_state["last_evaluation"] = evaluation
                
                # Capture terminal output from evaluation
                terminal_output = stdout_capture.getvalue() + stderr_capture.getvalue()
                if terminal_output.strip():
                    st.session_state["terminal_output"].append(f"[Prompt Evaluation] {terminal_output.strip()}")
            
            # Display results
            st.success("✅ AI response generated and prompt evaluated!")
            
            # Create two columns for AI response and evaluation
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 🤖 AI Response")
                st.markdown("*Based on the case study context and your prompt:*")
                
                if ai_response and not ai_response.startswith("Error"):
                    st.markdown(
                        f"""
                        <div style='min-height:250px;overflow-y:auto;overflow-x:hidden;padding:15px;background:#23292e;border-radius:8px;border-left:4px solid #36a8f5;'>
                        <div style='white-space:pre-wrap;line-height:1.6;color:#ffffff;'>{ai_response}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.error(f"⚠️ {ai_response}")
            
            with col2:
                st.markdown("### 📊 AI Response Evaluation")
                st.markdown("*Quality assessment of the AI-generated response:*")
                
                if evaluation:
                    # Overall score with color coding
                    score_color = "#28a745" if evaluation.overall_score >= 80 else "#ffc107" if evaluation.overall_score >= 60 else "#dc3545"
                    st.markdown(
                        f"""
                        <div style='padding:15px;background:#f8f9fa;border-radius:8px;border-left:4px solid {score_color};'>
                        <h4 style='color:{score_color};margin:0;'>Overall Score: {evaluation.overall_score:.1f}/100</h4>
                        <p style='margin:5px 0;'><strong>{st.session_state["evaluator"].get_score_interpretation(evaluation.overall_score)}</strong></p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Individual scores
                    st.markdown("**📋 Detailed Scores:**")
                    score_data = {
                        "Criterion": ["Strategic Fit & Objectives", "Audience & Relationships", "Commercials & Resourcing", "Outcomes, Measurment & Activation"],
                        "Score": [f"{evaluation.clarity_score:.1f}", f"{evaluation.specificity_score:.1f}", 
                                f"{evaluation.context_score:.1f}", f"{evaluation.structure_score:.1f}"]
                    }
                    df_scores = pd.DataFrame(score_data)
                    st.dataframe(df_scores, use_container_width=True, hide_index=True)
                    
                    # Feedback
                    st.markdown("**💭 AI Feedback:**")
                    st.info(evaluation.feedback)
                    
                    # ...removed strengths and areas for improvement boxes...
                else:
                    st.error("⚠️ Evaluation failed. Please try again.")
            
            # Update leaderboard in SQLite DB with highest score for this team
            if evaluation:
                team_name = st.session_state["team"]
                score = evaluation.overall_score
                update_team_score(team_name, score)
    elif submit_disabled:
        st.warning("No more submissions available.")
    else:
        st.info("Submit a prompt to see the AI response here.")
    st.markdown("---")
    st.markdown("Built for the seminar competition.")
