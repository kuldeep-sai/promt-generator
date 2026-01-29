import streamlit as st
from bs4 import BeautifulSoup
import openai
from openai import OpenAI

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="LLM Prompt Generator", layout="wide")
st.title("🧠 Article → LLM Prompt Generator")

# ---------- FRONTEND API KEY INPUT ----------
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.text_input(
    "Enter your OpenAI API Key",
    type="password",
    placeholder="sk-xxxx...",
    value=st.session_state.api_key
).strip()

if api_key_input:
    st.session_state.api_key = api_key_input

if not st.session_state.api_key:
    st.warning("Please enter your OpenAI API Key to continue.")
    st.stop()

# ---------- INITIALIZE OPENAI CLIENT ----------
client = OpenAI(api_key=st.session_state.api_key)

# ---------- VALIDATE API KEY ----------
try:
    client.models.list()  # simple test call
except openai.error.AuthenticationError:
    st.error("❌ Invalid OpenAI API Key. Please check and try again.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error connecting to OpenAI: {e}")
    st.stop()

st.success("✅ API Key is valid!")

# ---------- PROMPT TEMPLATES ----------
FAQ_PROMPT = """
Generate 4 SEO-compliant FAQs based on the article below.

Rules:
- Questions must reflect real user intent
- Answers must be 50–80 words
- Neutral, factual tone
- No marketing language

Context:
Title: {title}
Key Topics: {headings}
Summary: {summary}

Format:
Q: ...
A: ...
"""

AI_OVERVIEW_PROMPT = """
Explain the core topic of this article in a way suitable for AI-generated answers.
Under 120 words.

Context:
{summary}
"""

PAA_PROMPT = """
List common informational questions users may ask after reading this article.
Questions only.

Context:
{summary}
"""

ENTITY_PROMPT = """
Extract key entities and explain their relationships clearly.

Context:
{summary}
"""

# ---------- HELPER FUNCTIONS ----------
def parse_article(content):
    soup = BeautifulSoup(content, "html.parser")
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Untitled"
    headings = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])][:8]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    summary = " ".join(paragraphs[:5])[:1500]
    return title, headings, summary

def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert SEO editor and knowledge architect."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except openai.error.AuthenticationError:
        st.error("❌ Authentication error with OpenAI API Key. Please check it.")
        st.stop()
    except openai.error.OpenAIError as e:
        st.error(f"❌ OpenAI request error: {e}")
        st.stop()

# ---------- ARTICLE INPUT ----------
article_input = st.text_area(
    "Paste Article HTML or Content",
    height=300,
    placeholder="Paste full article HTML or plain text here"
)

faq_count = st.slider("Number of FAQs to generate", 1, 10, 4)

if st.button("Generate Prompts"):
    if not article_input.strip():
        st.warning("Please paste article content.")
        st.stop()

    title, headings, summary = parse_article(article_input)

    faq_prompt = FAQ_PROMPT.format(
        title=title,
        headings=", ".join(headings),
        summary=summary
    )
    ai_prompt = AI_OVERVIEW_PROMPT.format(summary=summary)
    paa_prompt = PAA_PROMPT.format(summary=summary)
    entity_prompt = ENTITY_PROMPT.format(summary=summary)

    with st.spinner("Generating prompts via OpenAI..."):
        faq_output = call_llm(faq_prompt)
        ai_output = call_llm(ai_prompt)
        paa_output = call_llm(paa_prompt)
        entity_output = call_llm(entity_prompt)

    tab1, tab2, tab3, tab4 = st.tabs(["FAQs", "AI Overview", "PAA", "Entities"])

    with tab1:
        st.text_area("FAQs", faq_output, height=300)
    with tab2:
        st.text_area("AI Overview", ai_output, height=200)
    with tab3:
        st.text_area("People Also Ask", paa_output, height=200)
    with tab4:
        st.text_area("Entities", entity_output, height=250)
