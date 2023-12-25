import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from keybert import KeyBERT
from pandas import DataFrame
from wordcloud import WordCloud

# For Flair (Keybert)
# For download buttons
from functionforDownloadButtons import download_button


class BERTKeywordExtractor:
    def __init__(self):
        st.set_page_config(
            page_title="BERT Keyword Extractor",
            page_icon="🎈",
        )

    @staticmethod
    def _max_width_():
        max_width_str = "max-width: 1400px;"
        st.markdown(
            f"""
        <style>
        .reportview-container .main .block-container{{
            {max_width_str}
        }}
        </style>
        """,
            unsafe_allow_html=True,
        )

    def run(self):
        self._max_width_()

        c30, c31, c32 = st.columns([2.5, 1, 3])

        with c30:
            # st.image("logo.png", width=400)
            st.title("🔑 BERT Keyword Extractor")
            st.header("")

        with st.expander("ℹ️ - About this app", expanded=True):
            st.write(
                """
        -   The *BERT Keyword Extractor* app is an easy-to-use interface built in Streamlit for the amazing [KeyBERT](https://github.com/MaartenGr/KeyBERT) library from Maarten Grootendorst!
        -   It uses a minimal keyword extraction technique that leverages multiple NLP embeddings and relies on [Transformers] (https://huggingface.co/transformers/) 🤗 to create keywords/keyphrases that are most similar to a document.
                """
            )

            st.markdown("")

        st.markdown("")
        st.markdown("## **📌 Paste document **")
        with st.form(key="my_form"):
            ce, c1, ce, c2, c3 = st.columns([0.07, 1, 0.07, 5, 0.07])
            with c1:
                self.model_options()

                self.keywords_extraction_options()

            with c2:
                self.input_document()

                self.check_data_button()

            if self.use_MMR:
                self.mmr = True
            else:
                self.mmr = False

            if self.StopWordsCheckbox:
                self.StopWords = "english"
            else:
                self.StopWords = None

            if not self.submit_button:
                st.stop()

            if self.min_Ngrams > self.max_Ngrams:
                st.warning("min_Ngrams can't be greater than max_Ngrams")
                st.stop()

            keywords = self.kw_model.extract_keywords(
                self.doc,
                keyphrase_ngram_range=(self.min_Ngrams, self.max_Ngrams),
                use_mmr=self.mmr,
                stop_words=self.StopWords,
                top_n=self.top_N,
                diversity=self.Diversity,
            )

            self.download_results(keywords)

            self.display_results(keywords)

    def model_options(self):
        ModelType = st.radio(
            "Choose your model",
            ["DistilBERT (Default)", "Flair"],
            help="At present, you can choose between 2 models (Flair or DistilBERT) to embed your text. More to come!",
        )

        if ModelType == "Default (DistilBERT)":

            @st.cache(allow_output_mutation=True)
            def load_model():
                return KeyBERT(model="roberta")

            self.kw_model = load_model()

        else:

            @st.cache(allow_output_mutation=True)
            def load_model():
                return KeyBERT("distilbert-base-nli-mean-tokens")

            self.kw_model = load_model()

    def keywords_extraction_options(self):
        self.top_N = st.slider(
            "# of results",
            min_value=1,
            max_value=30,
            value=10,
            help="You can choose the number of keywords/keyphrases to display. Between 1 and 30, default number is 10.",
        )

        self.min_Ngrams = st.number_input(
            "Minimum Ngram",
            min_value=1,
            max_value=4,
            help="""The minimum value for the ngram range.

    *Keyphrase_ngram_range* sets the length of the resulting keywords/keyphrases.

    To extract keyphrases, simply set *keyphrase_ngram_range* to (1, 2) or higher depending on the number of words you would like in the resulting keyphrases.""",
        )

        self.max_Ngrams = st.number_input(
            "Maximum Ngram",
            value=2,
            min_value=1,
            max_value=4,
            help="""The maximum value for the keyphrase_ngram_range.

    *Keyphrase_ngram_range* sets the length of the resulting keywords/keyphrases.

    To extract keyphrases, simply set *keyphrase_ngram_range* to (1, 2) or higher depending on the number of words you would like in the resulting keyphrases.""",
        )

        self.StopWordsCheckbox = st.checkbox(
            "Remove stop words",
            help="Tick this box to remove stop words from the document (currently English only)",
        )

        self.use_MMR = st.checkbox(
            "Use MMR",
            value=True,
            help="You can use Maximal Margin Relevance (MMR) to diversify the results. It creates keywords/keyphrases based on cosine similarity. Try high/low 'Diversity' settings below for interesting variations.",
        )

        self.Diversity = st.slider(
            "Keyword diversity (MMR only)",
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            help="""The higher the setting, the more diverse the keywords.

    Note that the *Keyword diversity* slider only works if the *MMR* checkbox is ticked.

    """,
        )

    def input_document(self):
        self.doc = st.text_area(
            "Paste your text below (max 500 words)",
            height=510,
        )

        MAX_WORDS = 500
        import re

        res = len(re.findall(r"\w+", self.doc))
        if res > MAX_WORDS:
            st.warning(
                "⚠️ Your text contains "
                + str(res)
                + " words."
                + " Only the first 500 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
            )

            self.doc = self.doc[:MAX_WORDS]

        self.submit_button = st.form_submit_button(label="✨ Get me the data!")

    def check_data_button(self):
        if self.use_MMR:
            self.mmr = True
        else:
            self.mmr = False

        if self.StopWordsCheckbox:
            self.StopWords = "english"
        else:
            self.StopWords = None

    def download_results(self, keywords):
        st.markdown("## **🎈 Check & download results **")

        st.header("")

        cs, c1, c2, c3, cLast = st.columns([2, 1.5, 1.5, 1.5, 2])

        with c1:
            CSVButton2 = download_button(keywords, "Data.csv", "📥 Download (.csv)")
        with c2:
            CSVButton2 = download_button(keywords, "Data.txt", "📥 Download (.txt)")
        with c3:
            CSVButton2 = download_button(keywords, "Data.json", "📥 Download (.json)")

        st.header("")

    def display_results(self, keywords):
        df = (
            DataFrame(keywords, columns=["Keyword/Keyphrase", "Relevancy"])
            .sort_values(by="Relevancy", ascending=False)
            .reset_index(drop=True)
        )

        df.index += 1

        # Create a word cloud for the top 10 most relevant keywords
        top_keywords = df.head(10)["Keyword/Keyphrase"].tolist()
        wordcloud_text = " ".join(top_keywords)

        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
            wordcloud_text
        )

        # Display the word cloud
        st.markdown("## **🌟 Word Cloud of Top 10 Relevant Keywords**")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # Add styling
        cmGreen = sns.light_palette("green", as_cmap=True)
        cmRed = sns.light_palette("red", as_cmap=True)
        df = df.style.background_gradient(
            cmap=cmGreen,
            subset=[
                "Relevancy",
            ],
        )

        c1, c2, c3 = st.columns([1, 3, 1])

        format_dictionary = {
            "Relevancy": "{:.1%}",
        }

        df = df.format(format_dictionary)

        with c2:
            st.table(df)


if __name__ == "__main__":
    bert_extractor = BERTKeywordExtractor()
    bert_extractor.run()
