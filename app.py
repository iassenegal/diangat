import re

import justext
import nltk
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from nltk.tokenize import sent_tokenize
from PyPDF2 import PdfReader

nltk.download("punkt")
nltk.download("wordnet")


# Function to scrape content from URL
def scrape_content_url(url):
    try:
        response = requests.get(url)
        paragraphs = justext.justext(response.content, justext.get_stoplist("French"))
        scraped_content = []

        for i, paragraph in enumerate(paragraphs):
            if not paragraph.is_boilerplate:
                scraped_content.append(paragraph.text)

        content_text = " ".join(scraped_content)

        return content_text
    except Exception as e:
        st.write(f"Error scraping content: {str(e)}")
        return None


# Function to scrape content from PDF
def scrape_content_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        extracted_text = []

        for i in range(total_pages):
            page = pdf_reader.pages[i]
            extracted_text.append(page.extract_text())

        content_text = " ".join(extracted_text)
        st.write(
            f"Nombre de pages dans le document '{pdf_file.name}': {total_pages}"
        )  # Print number of pages
        return content_text
    except Exception as e:
        st.write(f"Error extracting text from PDF: {str(e)}")
        return None


# Function to find subject occurrences in text
def find_subject_occurrences(text, selected_subjects):
    # ... (your existing code for remove_apostrophes, correct_text, lemmatize_text)

    subjects = selected_subjects
    occurrences = {subject: set() for subject in subjects}
    subject_count = {subject: 0 for subject in subjects}

    sentences = sent_tokenize(text)

    for subject in subjects:
        pattern = re.compile(r"\b" + re.escape(subject) + r"\b", re.IGNORECASE)
        for sentence in sentences:
            if re.search(pattern, sentence):
                occurrences[subject].add(sentence)
                subject_count[subject] += 1

    total_subjects = sum(subject_count.values())

    proportions_count = {}
    if total_subjects != 0:
        proportions_count = {
            subject: count / total_subjects for subject, count in subject_count.items()
        }

    return occurrences, proportions_count


# Streamlit app
st.write("Analyse thématique des propositions des candidats aux élections présidentielles")

option = st.sidebar.selectbox(
    "Choisir une source de données:", ("Article web : URL", "Document PDF")
)

selected_subjects = [
    "plan politique",
    "santé",
    "emploi",
    "agriculture",
    "numérique",
    "sécurité",
    "émigration",
    "justice",
    "démocratie",
    "technologie",
    "industrialisation",
    "jeunesse",
    "formation professionnelle",
    "éducation",
    "économie",
    "énergie",
    "environnement",
    "développement durable",
    "décentralisation",
    "développement local",
    "développement humain",
    "développement économique",
    "développement social",
    "rural",
]

selected_subjects = st.sidebar.multiselect(
    "Selectionner un ou plusieurs sujets", selected_subjects
)

if option == "Article web : URL":
    url = st.text_input("Enter URL:")
    if st.button("Scrape"):
        sample_text = scrape_content_url(url)
        if sample_text:
            try:
                result_occurrences, result_count_proportions = find_subject_occurrences(
                    sample_text, selected_subjects
                )
                # st.write(result_occurrences)
                for subject, sentences in result_occurrences.items():
                    st.write(f"Occurrences of '{subject}':")
                    for sentence in sentences:
                        st.write(f"'{sentence}'")

                for subject, proportion in result_count_proportions.items():
                    st.write(f"Proportion of times '{subject}' appears: {proportion}")

                # Calculate proportions for plotting
                proportions_df = pd.DataFrame(
                    result_count_proportions.items(), columns=["Thématiques", "Proportions"]
                )

                # Plotting using Plotly Express
                fig = px.bar(
                    proportions_df,
                    x="Proportions",
                    y="Thématiques",
                    orientation="h",
                    text=proportions_df["Proportions"].apply(lambda x: f"{x * 100:.2f}%"),
                    labels={"Proportions": "Proportions (%)", "Thématiques": "Thématiques"},
                    title="Proportion de thématiques liées au développement dans le programme du candidat",
                    color=proportions_df["Proportions"],
                    color_continuous_scale=px.colors.qualitative.Safe,
                    width=800,
                    height=600,
                )

                st.plotly_chart(fig)

            except ZeroDivisionError:
                st.write("Division by zero occurred during proportion calculation.")
        else:
            st.write("Failed to retrieve content from the URL.")

elif option == "Document PDF":
    pdf_files = st.file_uploader("Upload two PDF files", type=["pdf"], accept_multiple_files=True)
    pdf_files_names = [pdf_file.name for pdf_file in pdf_files]
    if st.button("Analyser"):
        if pdf_files is not None and len(pdf_files) == 2:
            sample_texts = []
            for pdf_file in pdf_files:
                sample_text = scrape_content_pdf(pdf_file)
                if sample_text:
                    sample_texts.append(sample_text)
                else:
                    st.write("Failed to retrieve content from one of the PDF files.")
                    break

            if len(sample_texts) == 2:
                try:
                    col1, col2 = st.columns(2)

                    for idx, sample_text in enumerate(sample_texts):
                        with col1 if idx == 0 else col2:
                            (
                                result_occurrences,
                                result_count_proportions,
                            ) = find_subject_occurrences(sample_text, selected_subjects)

                            # Calculate proportions for plotting
                            proportions_df = pd.DataFrame(
                                result_count_proportions.items(),
                                columns=["Thématiques", "Proportions"],
                            )

                            # Plotting using Plotly Express
                            fig = px.bar(
                                proportions_df,
                                x="Proportions",
                                y="Thématiques",
                                orientation="h",
                                text=proportions_df["Proportions"].apply(
                                    lambda x: f"{x * 100:.2f}%"
                                ),
                                labels={
                                    "Proportions": "Proportions (%)",
                                    "Thématiques": "Thématiques",
                                },
                                # title=f"Proportion de thématiques dans le document PDF {idx + 1}",
                                title=pdf_files_names[
                                    idx
                                ],  # f"Proportion de thématiques dans le document PDF '{pdf_files_names[idx]}'",
                                color=proportions_df["Proportions"],
                                color_continuous_scale=px.colors.qualitative.Safe,
                                width=600,
                                height=600,
                            )

                            st.plotly_chart(fig)

                            st.markdown(
                                f"Propositions phares par thématique dans : {pdf_files_names[idx]}:"
                            )
                            for subject, sentences in result_occurrences.items():
                                st.markdown(f"**Thématique: {subject}**")
                                if sentences:
                                    sentences_list = "<br>".join(
                                        f"'{sentence}'" for sentence in list(sentences)[:2]
                                    )
                                    st.markdown(sentences_list, unsafe_allow_html=True)
                                else:
                                    st.write("Aucune proposition trouvée pour cette thématique.")

                except ZeroDivisionError:
                    st.write("Division by zero occurred during proportion calculation.")
        else:
            st.write("Please upload exactly two PDF files.")
