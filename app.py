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

st.set_page_config(
    page_title="Jàngat - App",
    page_icon="https://thumb.ac-illust.com/41/4137d1a06f24fba4ad746d7672551894_t.jpeg",
)

# Updated selected_subjects
selected_subjects = {
    "plan politique": ["plan politique", "politique"],
    "santé": ["bien-être", "médical", "santé", "soins médicaux"],
    "emploi": ["recrutement", "marché du travail", "emploi"],
    "agriculture": ["cultures vivirières", "agriculture"],
    "numérique": ["technologique", "informatique", "numérique"],
    "sécurité": ["protection", "défense", "sécurité"],
    "émigration": ["migrations", "diaspora", "émigration"],
    "justice": ["légal", "tribunal", "justice"],
    "démocratie et liberté": [
        "participation",
        "élections",
        "démocratie",
        "liberté d'expréssion",
        "liberté",
    ],
    "technologie innovation": ["innovation", "recherche scientifique", "technologie"],
    "industrialisation": ["manufacture", "production", "industrialisation"],
    "jeunesse": ["adolescence", "enfance" "jeunesse", "jeunes"],
    "formation professionnelle": ["formation", "formation professionnelle"],
    "éducation": ["scolarité", "apprentissage", "éducation"],
    "économie et croissance": [
        "finances",
        "marché",
        "économie",
        "financement",
        "croissance économique",
        "prospérité",
    ],
    "énergie": ["puissance", "énergies renouvelables", "énergie renouvelable", "énergie"],
    "environnement": ["écologie", "nature", "environnement"],
    "décentralisation": ["localisation", "territorial", "décentralisation"],
    "rural": ["village", "agricole", "rural"],
}


# Function to scrape content from URL
def scrape_content_url(url):
    try:
        response = requests.get(url)
        paragraphs = justext.justext(response.content, justext.get_stoplist("French"))
        scraped_content = [
            paragraph.text for paragraph in paragraphs if not paragraph.is_boilerplate
        ]
        content_text = " ".join(scraped_content)
        return content_text
    except Exception as e:
        st.error(f"Error scraping content: {str(e)}")
        return None


# Function to scrape content from PDF
def scrape_content_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        extracted_text = [pdf_reader.pages[i].extract_text() for i in range(total_pages)]
        content_text = " ".join(extracted_text)
        st.info(
            f"Nombre de pages dans le document '{pdf_file.name.replace('.pdf', '')}': {total_pages}"
        )
        return content_text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None


# Updated function to find subject occurrences in text
def find_subject_occurrences(text, selected_subjects):
    occurrences = {subject: set() for subject in selected_subjects.keys()}
    subject_count = {subject: 0 for subject in selected_subjects.keys()}

    sentences = sent_tokenize(text)

    for subject, synonyms in selected_subjects.items():
        pattern = re.compile(
            r"\b(?:{})\b".format("|".join(map(re.escape, synonyms))), re.IGNORECASE
        )
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
st.title("Comparateur de programmes")
st.write("Analyse thématique des propositions des candidats aux élections présidentielles")

option = st.sidebar.radio("Choisir une source de données:", ("Article web : URL", "Document PDF"))

selected_subjects_list = list(selected_subjects.keys())
# Adding the "Select all" checkbox

all_subjects_checkbox = st.checkbox("Sélectionner toutes les thématiques")

# Updated selection of subjects
if all_subjects_checkbox:
    selected_subjects_multiselect = selected_subjects_list
else:
    selected_subjects_multiselect = st.multiselect(
        "Selectionner une ou plusieurs thématiques", selected_subjects_list
    )

if option == "Article web : URL":
    url = st.text_input("Enter URL:")
    if st.button("Scrape"):
        sample_text = scrape_content_url(url)
        if sample_text:
            try:
                result_occurrences, result_count_proportions = find_subject_occurrences(
                    sample_text,
                    {
                        subject: selected_subjects[subject]
                        for subject in selected_subjects_multiselect
                    },
                )

                # Display occurrences
                for subject, sentences in result_occurrences.items():
                    st.subheader(f"Occurrences de '{subject}':")
                    for sentence in sentences:
                        st.write(f"'{sentence}'")

                # Display proportions
                for subject, proportion in result_count_proportions.items():
                    st.write(f"Proportion de '{subject}': {proportion:.2%}")

                # Plotting
                proportions_df = pd.DataFrame(
                    result_count_proportions.items(), columns=["Thématiques", "Proportions"]
                )
                fig = px.bar(
                    proportions_df,
                    x="Proportions",
                    y="Thématiques",
                    orientation="h",
                    text=proportions_df["Proportions"].apply(lambda x: f"{x:.2%}"),
                    labels={"Proportions": "Proportions (%)", "Thématiques": "Thématiques"},
                    title="Proportion de thématiques liées au développement dans le programme du candidat",
                    color=proportions_df["Proportions"],
                    color_continuous_scale=px.colors.qualitative.Safe,
                    width=800,
                    height=600,
                )
                st.plotly_chart(fig)

            except ZeroDivisionError:
                st.error("Une division par zéro s'est produite lors du calcul de la proportion.")
        else:
            st.warning("Échec de récupération du contenu depuis l'URL.")

elif option == "Document PDF":
    pdf_files = st.file_uploader(
        "Charger deux fichers PDF", type=["pdf"], accept_multiple_files=True
    )
    pdf_files_names = [pdf_file.name for pdf_file in pdf_files]
    if st.button("Analyser"):
        if pdf_files is not None and len(pdf_files) == 2:
            sample_texts = [scrape_content_pdf(pdf_file) for pdf_file in pdf_files]
            if all(sample_texts):
                try:
                    col1, col2 = st.columns(2)

                    for idx, sample_text in enumerate(sample_texts):
                        with col1 if idx == 0 else col2:
                            (
                                result_occurrences,
                                result_count_proportions,
                            ) = find_subject_occurrences(
                                sample_text,
                                {
                                    subject: selected_subjects[subject]
                                    for subject in selected_subjects_multiselect
                                },
                            )

                            # Display proportions
                            proportions_df = pd.DataFrame(
                                result_count_proportions.items(),
                                columns=["Thématiques", "Proportions"],
                            )

                            # Plotting
                            fig = px.bar(
                                proportions_df,
                                x="Proportions",
                                y="Thématiques",
                                orientation="h",
                                text=proportions_df["Proportions"].apply(lambda x: f"{x:.2%}"),
                                labels={
                                    "Proportions": "Proportions (%)",
                                    "Thématiques": "Thématiques",
                                },
                                title=pdf_files_names[idx].replace(
                                    ".pdf", ""
                                ),  # Remove '.pdf' from title
                                color=proportions_df["Proportions"],
                                color_continuous_scale=px.colors.qualitative.Safe,
                                width=800,
                                height=600,
                            )

                            st.plotly_chart(
                                fig, use_container_width=True
                            )  # Set use_container_width to True

                except ZeroDivisionError:
                    st.error(
                        "Une division par zéro s'est produite lors du calcul de la proportion."
                    )
            else:
                st.warning("Échec de récupération du contenu depuis l'un des fichiers PDF.")
        else:
            st.warning("Veuillez télécharger exactement deux fichiers PDF.")
