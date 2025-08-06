import streamlit as st

st.set_page_config(page_title="Competition Team App", page_icon="🤖", layout="wide")

# Team selection and navigation state
if "team" not in st.session_state:
    st.session_state["team"] = None
if "main" not in st.session_state:
    st.session_state["main"] = False
if "submissions_left" not in st.session_state:
    st.session_state["submissions_left"] = 3

if not st.session_state["main"]:
    st.title("Welcome to the Competition Seminar App")
    st.markdown("Select your team below and click 'Get Started' to begin.")
    industry_list = ["Health", "Technology", "Gas", "Finance", "Retail", "Manufacturing", "Energy"]
    selected_team = st.selectbox("Select your industry:", industry_list)
    if st.button("Get Started", type="primary"):
        st.session_state["main"] = True
        st.session_state["team"] = selected_team
        # No rerun needed; state will update on next interaction
    st.markdown("---")
    st.markdown("Built for the seminar competition.")
else:
    st.title(f"Main Page - {st.session_state['team']}")
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
            st.success("Response received!")
            st.markdown(
                f"""
                <div style='min-height:200px;overflow-y:auto;overflow-x:hidden;padding:10px;background:#f9f9f9;border-radius:8px;max-width:400px;margin:0 auto;'>
                <h4>AI Response:</h4>
                <div style='white-space:pre-wrap;'>This is a sample AI response.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    elif submit_disabled:
        st.warning("No more submissions available.")
    else:
        st.info("Submit a prompt to see the AI response here.")
    st.markdown("---")
    st.markdown("Built for the seminar competition.")
