import streamlit as st
from bs4 import BeautifulSoup
from openai import OpenAI

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Article → LLM Prompt Generator", layout="wide")
st.title("🧠 Article → LLM Prompt Generator")

# ---- Frontend API Key Input ----
api_key = st.text_input(
    "Enter your OpenAI API Key",
    type="password",
    placeholder="sk-xxxx..."
)

if not api_key:
    st.warning("Please enter your OpenAI API Key to continue.")
    st.stop()

# ---------- Initialize OpenAI ----------
client = OpenAI(api_key=api_key)

# ---------- Prompt Templates ----------
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

# ---------- Helpers ----------
def parse_article(content):
    soup = BeautifulSoup(content, "html.parser")
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Untitled"
    headings = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])][:8]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    summary = " ".join(paragraphs[:5])[:1500]
    return title, headings, summary

def call_llm(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert SEO editor and knowledge architect."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# ---------- Article Input ----------
article_input = st.text_area(
    "Paste Article HTML or Content",
    height=300,
    placeholder="Paste full article HTML or plain text here"
)

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

    with st.spinner("Generating prompts via OpenAI..."):
        faq = call_llm(faq_prompt)
        overview = call_llm(AI_OVERVIEW_PROMPT.format(summary=summary))
        paa = call_llm(PAA_PROMPT.format(summary=summary))
        entities = call_llm(ENTITY_PROMPT.format(summary=summary))

    tab1, tab2, tab3, tab4 = st.tabs(["FAQs", "AI Overview", "PAA", "Entities"])

    with tab1:
        st.text_area("FAQs", faq, height=300)
    with tab2:
        st.text_area("AI Overview", overview, height=200)
    with tab3:
        st.text_area("People Also Ask", paa, height=200)
    with tab4:
        st.text_area("Entities", entities, height=250)
