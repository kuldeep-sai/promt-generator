import streamlit as st
from content_parser import parse_article
from prompt_templates import (
    FAQ_PROMPT,
    AI_OVERVIEW_PROMPT,
    PAA_PROMPT,
    ENTITY_PROMPT
)
from llm import generate

st.set_page_config(page_title="LLM Prompt Generator", layout="wide")

st.title("🧠 Article → LLM Prompt Generator")

article_html = st.text_area(
    "Paste Article HTML or Content",
    height=300,
    placeholder="Paste full article HTML or text here"
)

if st.button("Generate Prompts"):
    parsed = parse_article(article_html)

    st.subheader("Detected Article Info")
    st.write(parsed["title"])
    st.write(parsed["headings"])

    faq_prompt = FAQ_PROMPT.format(
        faq_count=4,
        title=parsed["title"],
        headings=", ".join(parsed["headings"]),
        summary=parsed["summary"]
    )

    ai_prompt = AI_OVERVIEW_PROMPT.format(summary=parsed["summary"])
    paa_prompt = PAA_PROMPT.format(summary=parsed["summary"])
    entity_prompt = ENTITY_PROMPT.format(summary=parsed["summary"])

    with st.spinner("Generating prompts via OpenAI..."):
        faq_output = generate(faq_prompt)
        ai_output = generate(ai_prompt)
        paa_output = generate(paa_prompt)
        entity_output = generate(entity_prompt)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["FAQs", "AI Overview", "PAA Questions", "Entities"]
    )

    with tab1:
        st.text_area("FAQ Output", faq_output, height=300)

    with tab2:
        st.text_area("AI Overview Output", ai_output, height=200)

    with tab3:
        st.text_area("People Also Ask Output", paa_output, height=200)

    with tab4:
        st.text_area("Entity Understanding Output", entity_output, height=250)
