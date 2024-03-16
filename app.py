import streamlit as st
import pandas as pd
import plotly.express as px
from PyPDF2 import PdfReader
import requests
import justext
import re
from nltk.tokenize import sent_tokenize
import nltk
# Assuming nltk has been previously downloaded and set up
nltk.download("punkt")
nltk.download("wordnet")

# Define the subjects of interest with their synonyms
selected_subjects = selected_subjects = {'Économie': ['économie',
  'économies',
  'économies',
  'finances',
  'marché',
  'marchés',
  'marchés',
  'croissance',
  'croissances',
  'croissances',
  'investissement étranger',
  'investissement étrangers',
  'investissement étrangers',
  'politique économique',
  'politique économiques',
  'politique économiques'],
 'Finance': ['finance',
  'finances',
  'finances',
  'investissement',
  'investissements',
  'investissements',
  'banque',
  'banques',
  'banques',
  'budget',
  'budgets',
  'budgets',
  'finances'],
 'Gaz': ['gaz naturel',
  'gaz naturels',
  'gaz naturels',
  'énergie fossile',
  'énergie fossiles',
  'énergie fossiles',
  'exploitation gazière',
  'exploitation gazières',
  'exploitation gazières',
  'gazoduc',
  'gazoducs',
  'gazoducs'],
 'Éducation': ['éducation',
  'éducations',
  'éducations',
  'scolarité',
  'scolarités',
  'scolarités',
  'apprentissage',
  'apprentissages',
  'apprentissages',
  'formation',
  'formations',
  'formations'],
 'Agriculture': ['agriculture',
  'agricultures',
  'agricultures',
  'cultures',
  'agroalimentaire',
  'agroalimentaires',
  'agroalimentaires',
  'cultivateurs'],
 'Industrialisation': ['industrialisation',
  'industrialisations',
  'industrialisations',
  'manufacture',
  'manufactures',
  'manufactures',
  'production',
  'productions',
  'productions',
  'usine',
  'usines',
  'usines'],
 'Pêche': ['pêche',
  'pêches',
  'pêches',
  'pisciculture',
  'piscicultures',
  'piscicultures',
  'aquaculture',
  'aquacultures',
  'aquacultures',
  'maritime',
  'maritimes',
  'maritimes'],
 'Emploi': ['emploi',
  'emplois',
  'emplois',
  'travail',
  'travails',
  'travails',
  'marché du travail',
  'marché du travails',
  'marché du travails',
  'chômage',
  'chômages',
  'chômages'],
 'Gouvernance': ['gouvernance',
  'gouvernances',
  'gouvernances',
  'administration',
  'administrations',
  'administrations',
  'politique',
  'politiques',
  'politiques',
  'leadership',
  'leaderships',
  'leaderships'],
 'Transparence': ['transparence',
  'transparences',
  'transparences',
  'responsabilité',
  'responsabilités',
  'responsabilités',
  'ouverture',
  'ouvertures',
  'ouvertures',
  'intégrité',
  'intégrités',
  'intégrités'],
 'Justice': ['justice',
  'justices',
  'justices',
  'tribunal',
  'tribunals',
  'tribunals',
  'légal',
  'légals',
  'légals',
  'droits'],
 'Sécurité': ['sécurité',
  'sécurités',
  'sécurités',
  'défense',
  'défenses',
  'défenses',
  'protection',
  'protections',
  'protections',
  'sûreté',
  'sûretés',
  'sûretés'],
 'Numérique': ['numérique',
  'numériques',
  'numériques',
  'technologie',
  'technologies',
  'technologies',
  'informatique',
  'informatiques',
  'informatiques',
  'innovation',
  'innovations',
  'innovations'],
 'Santé': ['santé',
  'santés',
  'santés',
  'soins médicaux',
  'soins médicauxs',
  'soins médicauxs',
  'hôpital',
  'hôpitals',
  'hôpitals',
  'prévention',
  'préventions',
  'préventions',
  'médecine',
  'médecines',
  'médecines'],
 'Infrastructure': ['infrastructure',
  'infrastructures',
  'routes',
  'ponts',
  'transports'],
 'Environnement': ['environnement',
  'environnements',
  'écologie',
  'écologies',
  'développement durable',
  'développement durables',
  'protection de la nature',
  'protection de la natures'],
 'Énergie': ['énergie',
  'énergies',
  'renouvelable',
  'renouvelables',
  'solaire',
  'solaires',
  'éolienne',
  'éoliennes',
  'hydroélectrique',
  'hydroélectriques'],
 'Santé Publique': ['santé publique',
  'santé publiques',
  'prévention',
  'préventions',
  'vaccination',
  'vaccinations',
  'politiques de santé',
  'politiques de santés'],
 'Technologie et Innovation': ['technologie',
  'technologies',
  'innovation',
  'innovations',
  'startup',
  'startups',
  'numérique',
  'numériques',
  'futur',
  'futurs'],
 'Culture': ['culture',
  'cultures',
  'patrimoine',
  'patrimoines',
  'arts',
  'traditions'],
 'Sport': ['sport',
  'sports',
  'activités physiques',
  'infrastructures sportives',
  'événements sportifs'],
 'Tourisme': ['tourisme',
  'tourismes',
  'promotion',
  'promotions',
  'sites touristiques',
  'culture et patrimoine',
  'culture et patrimoines'],
 'Politique Sociale': ['politique sociale',
  'politique sociales',
  'inclusion',
  'inclusions',
  'solidarité',
  'solidarités',
  'aide sociale',
  'aide sociales'],
 'Droits Humains': ['droits humains',
  'libertés fondamentales',
  'égalité',
  'égalités',
  'justice sociale',
  'justice sociales']}

st.set_page_config(page_title="Jàngat - App", page_icon="https://thumb.ac-illust.com/41/4137d1a06f24fba4ad746d7672551894_t.jpeg")

# Function to scrape content from PDF
def scrape_content_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        extracted_text = [pdf_reader.pages[i].extract_text() for i in range(total_pages)]
        content_text = " ".join(extracted_text)
        ###st.info(f"Nombre de pages dans le document '{pdf_file.name.replace('.pdf', '')}': {total_pages}")
        return content_text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

# Updated function to find subject occurrences in text
def find_subject_occurrences(text, subject_terms):
    occurrences = 0
    sentences = sent_tokenize(text, language='french')

    pattern = re.compile(r"\b(?:{})\b".format("|".join(map(re.escape, subject_terms))), re.IGNORECASE)

    for sentence in sentences:
        if re.search(pattern, sentence):
            occurrences += 1

    return occurrences, len(sentences)

# Streamlit UI
st.title("Comparateur de programmes")
st.write("Analyse thématique des propositions des candidats aux élections présidentielles")

# Select a thematic area
selected_subject = st.selectbox("Sélectionner une thématique", list(selected_subjects.keys()))

# PDF file uploader
pdf_files = st.file_uploader("Charger jusqu'à cinq fichiers PDF", type=["pdf"], accept_multiple_files=True)

if st.button("Analyser"):
    if pdf_files and len(pdf_files) <= 17:
        result_counts = []
        file_names = []
        
        for pdf_file in pdf_files:
            sample_text = scrape_content_pdf(pdf_file)
            if sample_text:
                occurrences, total_sentences = find_subject_occurrences(
                    sample_text, selected_subjects[selected_subject]
                )
                proportion = occurrences / total_sentences if total_sentences else 0
                result_counts.append(proportion)
                file_names.append(pdf_file.name.replace(".pdf", ""))
                
        # Visualization
        proportions_df = pd.DataFrame({
            "Candidats": file_names,
            "Proportion": result_counts
        })
        title_map = {
      'Numérique': "Poids du numérique dans chaque programme",
      'Économie': "Poids de l'économie dans chaque programme",
      'Agriculture': "Poids de l'agriculture dans chaque programme",
      # Ajoutez d'autres mappages de titres pour les thématiques restantes si nécessaire
  }
        # Utilisez `selected_subject` pour déterminer le titre spécifique
        specific_title = title_map.get(selected_subject, f"Proportion de '{selected_subject}' dans chaque programme")
        fig = px.bar(
            proportions_df,
            x="Candidats",
            y="Proportion",
            text=proportions_df["Proportion"].apply(lambda x: f"{x:.2%}"),
            ##labels={"Proportion": "Proportion de la thématique", "Fichier": ""},
            title=specific_title,
            color="Proportion",
            color_continuous_scale=px.colors.qualitative.Safe,
        )
        st.plotly_chart(fig)
    else:
        st.error("Veuillez télécharger entre 1 et 5 fichiers PDF.")

