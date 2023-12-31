import justext
import matplotlib.pyplot as plt
import openai
import pandas as pd
import requests
import streamlit as st
import yake
from PyPDF2 import PdfReader
from pytube import YouTube
from wordcloud import WordCloud
from youtube_transcript_api import YouTubeTranscriptApi


class WebApp:
    def extract_keywords(
        self, text, num_keywords, visualize_wordcloud=True, visualize_barchart=True
    ):
        kw_extractor = yake.KeywordExtractor()
        language = "french"
        max_ngram_size = 3
        deduplication_threshold = 0.9
        custom_kw_extractor = yake.KeywordExtractor(
            lan=language,
            n=max_ngram_size,
            dedupLim=deduplication_threshold,
            top=num_keywords,
            features=None,
        )
        keywords = custom_kw_extractor.extract_keywords(text)

        top_keywords = [keyword[0] for keyword in keywords[:num_keywords]]

        df_keywords = pd.DataFrame(
            {"Keyword": top_keywords, "Score": [keyword[1] for keyword in keywords[:num_keywords]]}
        )

        if visualize_wordcloud:
            st.subheader(f"Word Cloud for Top {num_keywords} Keywords")
            stop_words = ["d'un", "du", "un", "des"]
            fig_wc, ax_wc = plt.subplots(figsize=(20, 20))
            wordcloud = WordCloud(
                stopwords=stop_words, background_color="white", width=800, height=400
            ).generate(" ".join(top_keywords))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)

        if visualize_barchart:
            st.subheader(f"Bar Chart for Top {num_keywords} Keywords")
            fig_bc, ax_bc = plt.subplots(figsize=(10, 6))
            df_keywords.plot(kind="barh", x="Keyword", y="Score", ax=ax_bc, color="skyblue", rot=0)
            ax_bc.set_ylabel("Score")
            ax_bc.set_title(f"Top {num_keywords} Keywords and Their Scores")

        st.write(top_keywords)

        words_to_count = [
            "numérique",
            "société",
            "révolution",
            "développement",
            "Valeurs",
            "Institutions",
            "Fortes",
            "Projets",
        ]
        selected_words = st.multiselect("Choose data source:", words_to_count)

        if selected_words:
            word_counts = {
                word: text.lower().split().count(word.lower()) for word in words_to_count
            }

            selected_word_counts = {
                word: count for word, count in word_counts.items() if word in selected_words
            }

            if visualize_barchart and selected_word_counts:
                df_word_counts = pd.DataFrame(
                    list(selected_word_counts.items()), columns=["Word", "Count"]
                )
                st.subheader("Bar Chart for Word Occurrences")
                fig_word_counts, ax_word_counts = plt.subplots(figsize=(10, 6))
                df_word_counts.plot(
                    kind="barh", x="Word", y="Count", ax=ax_word_counts, colormap="viridis"
                )
                ax_word_counts.set_ylabel("Count")
                ax_word_counts.set_title("Proposition phares ")
                st.pyplot(fig_word_counts)
            elif visualize_barchart and not selected_word_counts:
                st.write("No occurrences found for the selected words.")
        else:
            st.write("Please select at least one word to visualize.")

    def download_transcript(self, video_url, num_keywords):
        try:
            video_id = YouTube(video_url).video_id
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["fr"])
            transcript_text = "\n".join([entry["text"] for entry in transcript])
            keywords = self.extract_keywords(transcript_text, num_keywords)
            st.subheader("YouTube Transcript:")
            st.write(transcript_text)
            if keywords:
                self.extract_keywords(transcript_text, num_keywords)
        except Exception as e:
            st.error(f"Error downloading transcript: {str(e)}")

    def scrape_content_url(self, url, num_keywords):
        try:
            response = requests.get(url)
            paragraphs = justext.justext(response.content, justext.get_stoplist("French"))
            total_paragraphs = len(paragraphs)
            scraped_content = []

            with st.progress(0):
                for i, paragraph in enumerate(paragraphs):
                    if not paragraph.is_boilerplate:
                        scraped_content.append(paragraph.text)

                    progress = (i + 1) / total_paragraphs
                    st.progress(progress)

            content_text = " ".join(scraped_content)
            keywords = self.extract_keywords(content_text, num_keywords)

            return content_text, keywords
        except Exception as e:
            st.error(f"Error scraping content: {str(e)}")
            return None, None

    def scrape_content_pdf(self, pdf_file, num_keywords):
        try:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            extracted_text = []

            with st.progress(0):
                for i in range(total_pages):
                    page = pdf_reader.pages[i]
                    extracted_text.append(page.extract_text())

                    progress = (i + 1) / total_pages
                    st.progress(progress)

            content_text = " ".join(extracted_text)
            keywords = self.extract_keywords(content_text, num_keywords)

            return content_text, keywords
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return None, None

    def about_page(self):
        st.markdown("<h2>A propos de cette application</h2>", unsafe_allow_html=True)
        st.write(
            """Cette application web est conçue pour analyser du contenu provenant de diverses sources, telles que des sites web, facebook, linkedin, des PDF et des vidéos YouTube."""
        )
        st.write(
            "Utilisez la barre latérale pour choisir la source de données et définir le nombre de mots-clés à analyser."
        )

    def analysis_page(self):
        st.markdown("<h2>Analysis Page</h2>", unsafe_allow_html=True)

        num_keywords = st.number_input(
            "Number of Keywords (up to 20):", min_value=1, max_value=200, value=20
        )

        action_button = st.button("Run Analysis")

        option = st.selectbox("Choose data source:", ("URL", "PDF", "YouTube"))

        if option == "URL":
            url = st.text_input("Enter the URL to scrape:", "")
            if action_button:
                if url:
                    st.info("Scraping content... Please wait.")
                    scraped_content, keywords = self.scrape_content_url(url, num_keywords)

                    if scraped_content:
                        st.subheader("Scraped Content:")
                        st.write(scraped_content)

                        if keywords:
                            self.extract_keywords(scraped_content, num_keywords)
                    else:
                        st.warning("Failed to scrape content. Check the URL and try again.")

        elif option == "PDF":
            pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
            if action_button:
                if pdf_file:
                    st.info("Extracting text... Please wait.")
                    extracted_text, keywords = self.scrape_content_pdf(pdf_file, num_keywords)

                    if extracted_text:
                        st.subheader("Extracted Text:")
                        if keywords:
                            self.extract_keywords(extracted_text, num_keywords)
                    else:
                        st.warning(
                            "Failed to extract text from PDF. Check the file and try again."
                        )

        elif option == "YouTube":
            youtube_url = st.text_input("Enter the YouTube URL:", "")
            if action_button:
                if youtube_url:
                    st.info("Downloading transcript... Please wait.")
                    self.download_transcript(youtube_url, num_keywords)
                else:
                    st.warning("Please enter a valid YouTube URL.")

    def get_insights_from_text(self, text, max_tokens=50):
        api_key = "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"
        openai.api_key = api_key

        max_context_tokens = 4096
        text = text[:100]
        chunks = [
            text[i : i + max_context_tokens] for i in range(0, len(text), max_context_tokens)
        ]

        insights = []
        total_chunks = len(chunks)
        progress_bar = st.progress(0)

        for i, chunk in enumerate(chunks):
            prompt = f"Extract 5 main topics from the following text:\n{chunk}\n\nInsights:"
            response = openai.completions.create(
                model="gpt-3.5-turbo",  # text-davinci-003",
                prompt=prompt,
                max_tokens=max_tokens,
                stop=None,
                temperature=0.5,
            )
            insights.append(response.choices[0].text.strip())

            progress_bar.progress((i + 1) / total_chunks)

        return "\n".join(insights)

    def run(self):
        st.markdown(
            """
            <style>
                """
            + open("style.css").read()
            + """
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<h1 style='font-size:1.5em;'>Institut des Algorithmes du Sénégal - Diangat Web App</h1>",
            unsafe_allow_html=True,
        )

        page_option = st.sidebar.radio("Choose page:", ("A propos", "Analyse"))

        if page_option == "A propos":
            self.about_page()
        elif page_option == "Analyse":
            self.analysis_page()


if __name__ == "__main__":
    web_app = WebApp()
    web_app.run()
