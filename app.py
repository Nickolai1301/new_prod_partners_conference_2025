import streamlit as st
from evaluation import PromptEvaluator
from openai import OpenAI
import os

# from dotenv import load_dotenv
import sys
from io import StringIO
import contextlib
import pandas as pd
from db import init_db, update_team_score, get_leaderboard

# Load environment variables
# load_dotenv()

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

st.set_page_config(page_title="PROMPT ARENA", page_icon="🤖", layout="wide")

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
if "last_trump_tweet" not in st.session_state:
    st.session_state["last_trump_tweet"] = None
if "leaderboard_data" not in st.session_state:
    st.session_state["leaderboard_data"] = [
        {
            "Rank": 1,
            "Team": "Alpha Consultants",
            "Industry": "Technology",
            "Score": 2450,
            "Submissions": 8,
        }
    ]

# Initialize the SQLite database (only once)
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state["db_initialized"] = True


# Case Study Demo Content
case_study_content = """
# YOUR CHALLENGE

Draft up a compelling business case, that clearly articulates why your industry group should receive additional funding from AI Agent Lee. 

Think innovation, impact, and intention.

"""


def generate_ai_response_streaming(user_prompt: str, industry: str, placeholder):
    """Generate AI response using streaming with structured markdown output"""
    try:
        # Combine case study with user prompt for context
        full_context = f"""
USER PROMPT:
{user_prompt}

INDUSTRY CONTEXT: {industry}

IMPORTANT: Format your response as well-structured markdown with clear headings, bullet points, and sections. Use proper markdown syntax including:
- # for main headings
- ## for subheadings  
- ### for sub-subheadings
- * or - for bullet points
- **bold** for emphasis
- Tables where appropriate
- Clear paragraph breaks

Structure your analysis professionally with logical sections and clear formatting.
"""

        stream = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {
                    "role": "system",
                    "content": "You are a M&A Partner providing expert analysis. Use the case study context to inform your response and provide detailed, actionable business insights. Always format your response as well-structured markdown with clear headings, bullet points, and professional formatting.",
                },
                {"role": "user", "content": full_context},
            ],
            temperature=0.7,
            max_tokens=15000,
            stream=True,
        )

        # Stream the response
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                chunk_text = chunk.choices[0].delta.content
                full_response += chunk_text
                placeholder.markdown(full_response + "▌")  # Show cursor while streaming

        # Final update without cursor
        placeholder.markdown(full_response)
        return full_response

    except Exception as e:
        error_msg = f"**Error generating AI response:** {str(e)}"
        placeholder.markdown(error_msg)
        return error_msg


def generate_trump_tweet(score: float, ai_response: str, team_name: str) -> str:
    """Generate a Trump-style tweet based on the evaluation score and AI response"""
    try:
        # Load Trump prompt style from file
        with open("trump_prompt.txt", "r", encoding="utf-8") as file:
            trump_style_prompt = file.read()

        # Create the prompt for generating Trump tweet
        tweet_prompt = f"""
{trump_style_prompt}

You are Donald Trump commenting on a business prompt competition where teams submit prompts and get scored. 

CONTEXT:
- Team: {team_name}
- Their prompt got a score of {score:.1f}/100
- The AI generated this response: {ai_response[:500]}...

Generate a single Trump-style tweet (max 280 characters) that:
1. Comments on their score and performance 
2. Uses Trump's signature style (ALL CAPS for emphasis, exclamation points, superlatives)
3. Be either congratulatory (if score >= 80), mildly critical (60-79), or harsh (below 60)
4. Keep it business/competition focused
5. Make it authentic to Trump's tweeting style

IMPORTANT: 
- Only return the tweet text, nothing else
- Stay under 280 characters
- Use Trump's signature phrases and style
- Be entertaining but not offensive
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {
                    "role": "system",
                    "content": "You are a tweet generator that creates authentic Donald Trump-style tweets. Focus on his business/competition commentary style with signature capitalization and phrases.",
                },
                {"role": "user", "content": tweet_prompt},
            ],
            temperature=0.8,
            max_tokens=100,
        )

        tweet = response.choices[0].message.content.strip()
        # Remove quotes if they exist
        if tweet.startswith('"') and tweet.endswith('"'):
            tweet = tweet[1:-1]

        return tweet

    except Exception as e:
        # Fallback tweet if generation fails
        if score >= 80:
            return f"GREAT work {team_name}! {score:.0f} points - that's what I call WINNING! Keep it up! #MAGA"
        elif score >= 60:
            return f"{team_name} scored {score:.0f} - not bad, but could be MUCH better. Step it up! #Competition"
        else:
            return f"{team_name} got {score:.0f} points. SAD! Need to work harder. Much harder! #LosingBigly"


if not st.session_state["main"] and not st.session_state["show_leaderboard"]:
    st.title("🎯 Welcome to the Prompt-Off: The Battle for Budget! 💥")

    # Homepage content
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

    industry_list = ["TMT", "FSI", "Health", "Infra", "PE", "Consumer"]
    team_name = st.text_input(
        "Custom Team Name:", max_chars=30, placeholder="e.g. Team_1"
    )
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

    if leaderboard:
        # Use real data from database
        leaderboard_rows = [
            {
                "Team": row[0],
                "Score": row[1],
                "Last Submission": row[2],
                "Submissions": 1,
            }
            for row in leaderboard
        ]
        df = pd.DataFrame(leaderboard_rows)
    else:
        # Fallback to demo data if no real data exists
        df = pd.DataFrame(st.session_state["leaderboard_data"])
        # Remove Rank column as it's not needed for display
        if "Rank" in df.columns:
            df = df.drop("Rank", axis=1)

    # Create a styled dataframe
    st.markdown("#### 📊 Team Rankings")

    # Highlight top 3 teams
    def highlight_top_teams(row):
        if row.name == 0:  # First place
            return ["background-color: #FFD700; font-weight: bold"] * len(row)  # Gold
        elif row.name == 1:  # Second place
            return ["background-color: #C0C0C0; font-weight: bold"] * len(row)  # Silver
        elif row.name == 2:  # Third place
            return ["background-color: #CD7F32; font-weight: bold"] * len(row)  # Bronze
        else:
            return [""] * len(row)

    styled_df = df.style.apply(highlight_top_teams, axis=1)
    st.dataframe(styled_df, use_container_width=True, height=400)

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Teams", len(df))
    with col2:
        if "Submissions" in df.columns:
            st.metric("Total Submissions", df["Submissions"].sum())
        else:
            st.metric("Total Submissions", "N/A")
    with col3:
        st.metric("Average Score", f"{df['Score'].mean():.0f}" if not df.empty else "0")

    st.markdown("---")
    st.markdown("*Leaderboard updates in real-time during the competition*")

    # Button to clear leaderboard results (admin use)
    from db import clear_leaderboard

    if st.button("🗑️ Clear Leaderboard (Admin)", type="secondary"):
        clear_leaderboard()
        st.success("Leaderboard cleared!")
        st.rerun()

elif st.session_state["main"] and not st.session_state["show_leaderboard"]:
    st.title(f"PROMPT ARENA - {st.session_state['team']}")
    st.markdown("---")
    st.markdown(case_study_content)
    st.markdown("---")
    st.markdown("Enter your prompt below and submit to see the AI response.")
    st.info(f"Submissions left: {st.session_state['submissions_left']}")
    user_prompt = st.text_area(
        "Prompt:", height=100, placeholder="Type your question or prompt here..."
    )
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

            # Step 1: Generate AI response using case study + user prompt with streaming
            st.markdown("### 🤖 AI Response")
            st.markdown("*Based on your prompt:*")

            # Create placeholder for streaming response
            response_placeholder = st.empty()

            with capture_terminal_output() as (stdout_capture, stderr_capture):
                ai_response = generate_ai_response_streaming(
                    user_prompt, st.session_state["team"], response_placeholder
                )

            # Store AI response
            st.session_state["last_ai_response"] = ai_response

            # Capture terminal output from AI generation
            terminal_output = stdout_capture.getvalue() + stderr_capture.getvalue()
            if terminal_output.strip():
                st.session_state["terminal_output"].append(
                    f"[AI Generation] {terminal_output.strip()}"
                )

            # Step 2: Evaluate the AI-generated response
            with st.spinner("📊 Evaluating AI response quality..."):
                with capture_terminal_output() as (stdout_capture, stderr_capture):
                    evaluation = st.session_state["evaluator"].evaluate_prompt(
                        ai_response, st.session_state["team"]
                    )

                # Store evaluation
                st.session_state["last_evaluation"] = evaluation

                # Capture terminal output from evaluation
                terminal_output = stdout_capture.getvalue() + stderr_capture.getvalue()
                if terminal_output.strip():
                    st.session_state["terminal_output"].append(
                        f"[Prompt Evaluation] {terminal_output.strip()}"
                    )

            # Step 3: Generate Trump tweet based on score and AI response
            trump_tweet = None
            if evaluation:
                with st.spinner("🐦 Generating Trump tweet..."):
                    trump_tweet = generate_trump_tweet(
                        evaluation.overall_score, ai_response, st.session_state["team"]
                    )
                    st.session_state["last_trump_tweet"] = trump_tweet

            # Display results
            st.success(
                "✅ AI response generated, prompt evaluated, and Trump tweet created!"
            )

            # Single column for evaluation (full width)
            st.markdown("### 📊 Prompt Evaluation")
            st.markdown("*Quality assessment of your original prompt:*")

            if evaluation:
                # Overall score with color coding
                score_color = (
                    "#28a745"
                    if evaluation.overall_score >= 80
                    else "#ffc107" if evaluation.overall_score >= 60 else "#dc3545"
                )
                st.markdown(
                    f"""
                        <div style='padding:15px;background:#f8f9fa;border-radius:8px;border-left:4px solid {score_color};'>
                        <h4 style='color:{score_color};margin:0;'>Overall Score: {evaluation.overall_score:.1f}/100</h4>
                        </div>
                        """,
                    unsafe_allow_html=True,
                )

                # Individual scores
                st.markdown("**📋 Detailed Scores:**")
                score_data = {
                    "Criterion": [
                        "Strategic Fit & Objectives",
                        "Audience & Relationships",
                        "Commercials & Resourcing",
                        "Outcomes, Measurement & Activation",
                    ],
                    "Score": [
                        f"{evaluation.strategic_fit_score:.1f}",
                        f"{evaluation.audience_score:.1f}",
                        f"{evaluation.commercials_score:.1f}",
                        f"{evaluation.outcomes_score:.1f}",
                    ],
                }
                df_scores = pd.DataFrame(score_data)
                st.dataframe(df_scores, use_container_width=True, hide_index=True)
            else:
                st.error("⚠️ Evaluation failed. Please try again.")

            # Display Trump Tweet
            if trump_tweet:
                st.markdown("---")
                st.markdown("### 🐦 Trump Tweet Response")
                st.markdown("*What would Trump tweet about your performance?*")

                # Style the tweet to look like a real tweet
                st.markdown(
                    f"""
                    <div style='padding:15px;background:#1DA1F2;color:white;border-radius:15px;font-family:system-ui;'>
                    <div style='display:flex;align-items:center;margin-bottom:10px;'>
                    <strong>@realDonaldTrump</strong>
                    <span style='color:#8ED0FF;margin-left:5px;'>✓</span>
                    </div>
                    <div style='font-size:16px;line-height:1.4;'>{trump_tweet}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Update leaderboard in SQLite DB with highest score for this team
            if evaluation:
                team_name = st.session_state["team"]
                score = evaluation.overall_score
                update_team_score(team_name, score)

            # Show original prompt for reference
            st.markdown("---")
            st.markdown("### 📝 Your Original Prompt")
            with st.expander("Show submitted prompt", expanded=False):
                st.code(user_prompt, language="text")

    elif submit_disabled:
        st.warning("No more submissions available.")
    else:
        st.info("Submit a prompt to see the AI response here.")
    st.markdown("---")
