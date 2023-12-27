import justext
import matplotlib.pyplot as plt
import openai
import pandas as pd
import requests
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
            stop_words = ["d'un", "du", "un", "des"]
            wordcloud = WordCloud(
                stopwords=stop_words, background_color="white", width=800, height=400
            ).generate(" ".join(top_keywords))
            plt.figure(figsize=(10, 6))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.show()

        if visualize_barchart:
            plt.figure(figsize=(10, 6))
            df_keywords.plot(kind="barh", x="Keyword", y="Score", color="skyblue", legend=False)
            plt.ylabel("Score")
            plt.title(f"Top {num_keywords} Keywords and Their Scores")
            plt.show()

        print(top_keywords)

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

        word_counts = {word: text.lower().split().count(word.lower()) for word in words_to_count}

        if visualize_barchart:
            df_word_counts = pd.DataFrame(list(word_counts.items()), columns=["Word", "Count"])
            plt.figure(figsize=(10, 6))
            df_word_counts.plot(kind="barh", x="Word", y="Count", colormap="viridis", legend=False)
            plt.xlabel("Count")
            plt.title("Proposition phares ")
            plt.show()

    def download_transcript(self, video_url, num_keywords):
        try:
            video_id = YouTube(video_url).video_id
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["fr"])
            transcript_text = "\n".join([entry["text"] for entry in transcript])
            keywords = self.extract_keywords(transcript_text, num_keywords)
            print("YouTube Transcript:")
            print(transcript_text)
            if keywords:
                self.extract_keywords(transcript_text, num_keywords)
        except Exception as e:
            print(f"Error downloading transcript: {str(e)}")

    def scrape_content_url(self, url, num_keywords):
        try:
            response = requests.get(url)
            paragraphs = justext.justext(response.content, justext.get_stoplist("French"))
            total_paragraphs = len(paragraphs)
            scraped_content = []

            for i, paragraph in enumerate(paragraphs):
                if not paragraph.is_boilerplate:
                    scraped_content.append(paragraph.text)

            content_text = " ".join(scraped_content)
            keywords = self.extract_keywords(content_text, num_keywords)

            insights = self.get_insights_from_text(content_text)
            print("Insights from Extracted Content:")
            print(insights)

            return content_text, keywords
        except Exception as e:
            print(f"Error scraping content: {str(e)}")
            return None, None

    def scrape_content_pdf(self, pdf_file, num_keywords):
        try:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            extracted_text = []

            for i in range(total_pages):
                page = pdf_reader.pages[i]
                extracted_text.append(page.extract_text())

            content_text = " ".join(extracted_text)
            keywords = self.extract_keywords(content_text, num_keywords)

            insights = self.get_insights_from_text(content_text)
            print("Insights from Extracted Content:")
            print(insights)

            return content_text, keywords
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return None, None

    def about_page(self):
        print("A propos de cette application")
        print(
            """Cette application web est conçue pour analyser du contenu provenant de diverses sources, telles que des sites web, facebook, linkedin, des PDF et des vidéos YouTube."""
        )
        print(
            "Utilisez les fonctions pour choisir la source de données et définir le nombre de mots-clés à analyser."
        )

    def get_insights_from_text(self, text, max_tokens=50):
        api_key = "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"
        openai.api_key = api_key

        max_context_tokens = 4096
        chunks = [
            text[i : i + max_context_tokens] for i in range(0, len(text), max_context_tokens)
        ]

        insights = []

        for i, chunk in enumerate(chunks):
            prompt = f"Extract 5 main topics from the following text:\n{chunk}\n\nInsights:"
            response = openai.completions.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=max_tokens,
                stop=None,
                temperature=0.5,
            )
            insights.append(response.choices[0].text.strip())

        return "\n".join(insights)

    def run(self):
        print("Institut des Algorithmes du Sénégal - Diangat Web App")

        page_option = input("Choose page (A propos/Analyse): ")

        if page_option == "A propos":
            self.about_page()
        elif page_option == "Analyse":
            num_keywords = int(input("Number of Keywords (up to 20): "))
            option = input("Choose data source (URL/PDF/YouTube): ")

            if option == "URL":
                url = input("Enter the URL to scrape: ")
                if url:
                    print("Scraping content... Please wait.")
                    scraped_content, keywords = self.scrape_content_url(url, num_keywords)

                    if scraped_content:
                        print("Scraped Content:")
                        print(scraped_content)

                        if keywords:
                            self.extract_keywords(scraped_content, num_keywords)
                    else:
                        print("Failed to scrape content. Check the URL and try again.")

            elif option == "PDF":
                print("Upload a PDF file")
                pdf_file = input("Enter PDF file path: ")
                if pdf_file:
                    print("Extracting text... Please wait.")
                    extracted_text, keywords = self.scrape_content_pdf(pdf_file, num_keywords)

                    if extracted_text:
                        print("Extracted Text:")
                        if keywords:
                            self.extract_keywords(extracted_text, num_keywords)
                    else:
                        print("Failed to extract text from PDF. Check the file and try again.")

            elif option == "YouTube":
                youtube_url = input("Enter the YouTube URL: ")
                if youtube_url:
                    print("Downloading transcript... Please wait.")
                    self.download_transcript(youtube_url, num_keywords)
                else:
                    print("Please enter a valid YouTube URL.")


if __name__ == "__main__":
    web_app = WebApp()
    web_app.run()
