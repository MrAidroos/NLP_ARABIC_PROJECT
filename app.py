from flask import Flask, render_template, request
import os
from nltk.util import ngrams
from collections import Counter
import re  # Regular Expressions
from tashaphyne.stemming import ArabicLightStemmer
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.morphology.analyzer import Analyzer
from transformers import pipeline  # استخدام مكتبة Transformers للـ NER

app = Flask(__name__)

# Initialize ArabicLightStemmer for Arabic
arabic_stemmer = ArabicLightStemmer()

# Helper function to find and verify the morphology database path
def find_db_path():
    # تحديث المسار هنا
    default_path = os.path.expanduser("~/.camel_tools/data/morphology-db-msa-r13/camel_morphology.db")
    alternative_path = r"E:\My Projects\app\custom_camel_data\morphology-db-msa-r13\morphology.db"  # المسار الجديد

    if os.path.exists(default_path):
        app.logger.info(f"Morphology database found at {default_path}")
        return default_path
    elif os.path.exists(alternative_path):
        app.logger.info(f"Morphology database found at {alternative_path}")
        return alternative_path
    else:
        app.logger.error("Morphology database not found. Please install it using camel_data.")
        return None

# Initialize Morphological Analyzer for Lemmatization
try:
    db_path = find_db_path()
    if not db_path:
        raise FileNotFoundError("Morphology database not found. Please install it using camel_data.")
    morph_analyzer = Analyzer(db=db_path)
    app.logger.info("Morphological Analyzer initialized successfully.")
except Exception as e:
    app.logger.error(f"Error initializing Analyzer: {e}")
    morph_analyzer = None

# Initialize Camel Tools components
mle_disambiguator = MLEDisambiguator.pretrained()

# Initialize NER model from Hugging Face with a local path
ner_model_path = r"E:\My Projects\app\ner_arabert_data"
ner_pipeline = pipeline(
    "ner",
    model=ner_model_path,
    tokenizer=ner_model_path,
    aggregation_strategy="simple"
)

# Helper function for NER analysis with truncation
def split_text(text, tokenizer, max_length=128):
    tokens = tokenizer.tokenize(text)
    chunks = [' '.join(tokens[i:i + max_length]) for i in range(0, len(tokens), max_length)]
    app.logger.info(f"Text split into {len(chunks)} chunks.")
    return chunks

def analyze_entities(text):
    try:
        chunks = split_text(text, ner_pipeline.tokenizer, max_length=128)
        entities = []
        for chunk in chunks:
            app.logger.info(f"Processing chunk: {chunk}")
            chunk_entities = ner_pipeline(chunk)
            app.logger.info(f"Entities found in chunk: {chunk_entities}")
            entities.extend(chunk_entities)
        return entities
    except Exception as e:
        app.logger.error(f"Error in analyze_entities: {e}")
        return []

# Home page
@app.route('/')
def home():
    return render_template('index.html', title="Home", message="Welcome to the NLP Project!")

# Explanation page
@app.route('/explanation')
def explanation():
    return render_template('explanation.html', title="شرح التقنيات")

# Text Analysis page
@app.route('/text_analysis', methods=['GET', 'POST'])
def text_analysis():
    result = {}
    if request.method == 'POST':
        if 'text' not in request.form or not request.form['text']:
            result["Error"] = "No text provided for analysis."
            app.logger.error("No text provided for analysis.")
            return render_template('text_analysis.html', title="Text Analysis", result=result)

        text = request.form['text']
        analysis_type = request.form.get('analysis_type', 'all')
        n_value = int(request.form.get('n_value', 1))  # Default n value is 1

        try:
            # n-grams
            if analysis_type == "ngrams":
                result[f"{n_value}-grams"] = analyze_ngrams(text, n_value)

            # POS Tags
            if analysis_type == "all" or analysis_type == "pos":
                tokens = simple_word_tokenize(text)
                disambig = mle_disambiguator.disambiguate(tokens)
                result["POS Tags"] = []
                for d in disambig:
                    if d.analyses:
                        analysis = d.analyses[0].analysis
                        word = analysis.get("diac", "")
                        pos = analysis.get("pos", "N/A")
                        result["POS Tags"].append((word, pos))

            # Named Entities
            if analysis_type == "all" or analysis_type == "entities":
                entities = analyze_entities(text)
                app.logger.info(f"Raw entities result: {entities}")
                if not entities:
                    result["Error"] = "No named entities found or error during analysis."
                    app.logger.error("No named entities found or error during analysis.")
                else:
                    valid_entities = [e for e in entities if isinstance(e, dict)]
                    if not valid_entities:
                        result["Error"] = "Entities found but no valid entities to display."
                        app.logger.error("Entities found but no valid entities to display.")
                    else:
                        result["Named Entities"] = [
                            {
                                "Entity": e.get("word", "N/A"),
                                "Type": e.get("entity_group", "N/A"),
                                "Score": round(e.get("score", 0.0), 2)
                            }
                            for e in valid_entities
                        ]

            # Lemmatization
            if analysis_type == "all" or analysis_type == "lemmatization":
                if not morph_analyzer:
                    result["Error"] = "Morphological Analyzer not initialized. Unable to perform Lemmatization."
                    app.logger.error("Morphological Analyzer not initialized.")
                else:
                    tokens = text.split()
                    lemmatization_results = []
                    for word in tokens:
                        try:
                            analyses = morph_analyzer.analyze(word)
                            lemma = analyses[0]['lemma'] if analyses else "N/A"
                            lemmatization_results.append((word, lemma))
                        except Exception as e:
                            app.logger.error(f"Error lemmatizing word '{word}': {e}")
                            lemmatization_results.append((word, "Error"))
                    result["Lemmatization"] = lemmatization_results

            # Unigrams, Bigrams, Trigrams
            tokens = text.split()
            if analysis_type in ["all", "unigrams"]:
                result["Unigrams"] = Counter(list(ngrams(tokens, 1)))
            if analysis_type in ["all", "bigrams"]:
                result["Bigrams"] = Counter(list(ngrams(tokens, 2)))
            if analysis_type in ["all", "trigrams"]:
                result["Trigrams"] = Counter(list(ngrams(tokens, 3)))

            # Arabic Stemming
            if analysis_type == "all" or analysis_type == "stemming":
                tokens = text.split()
                stemmed_results = []
                for word in tokens:
                    try:
                        stem = arabic_stemmer.light_stem(word)
                        stemmed_results.append((word, stem))
                    except Exception as e:
                        app.logger.error(f"Error stemming word '{word}': {e}")
                        stemmed_results.append((word, "Error"))
                result["Stemming"] = stemmed_results

            # Regular Expressions
            if analysis_type == "all" or analysis_type == "regex":
                numbers = re.findall(r'\b\d+\b', text)
                emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA0-9-.]+', text)
                words_starting_with_t = re.findall(r'\bT\w*', text, re.IGNORECASE)

                app.logger.info(f"Regex Analysis: Numbers={numbers}, Emails={emails}, Words Starting with T={words_starting_with_t}")

                result["Regex"] = {
                    "Numbers": numbers,
                    "Emails": emails,
                    "Words Starting with T": words_starting_with_t
                }
        except Exception as e:
            app.logger.error(f"Error during analysis: {e}")
            result["Error"] = f"An error occurred during analysis: {str(e)}"

    app.logger.info(f"Final result: {result}")
    return render_template('text_analysis.html', title="Text Analysis", result=result)

# Search page
@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    keyword = None
    total_count = 0
    if request.method == 'POST':
        keyword = request.form['keyword']
        documents_dir = "documents"  # Directory containing text documents
        for filename in os.listdir(documents_dir):
            filepath = os.path.join(documents_dir, filename)
            if os.path.isfile(filepath) and filename.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    count = content.lower().count(keyword.lower())
                    if count > 0:
                        total_count += count
                        results.append({
                            "file": filename,
                            "count": count,
                            "lines": [line for line in content.splitlines() if keyword.lower() in line.lower()]
                        })
    return render_template('search.html', title="Text Search", results=results, keyword=keyword, total_count=total_count)

# Challenges page
@app.route('/challenges')
def challenges():
    return render_template('challenges.html', title="Challenges", message="Difficulties in natural language processing.")

def analyze_ngrams(text, n):
    tokens = text.split()
    n_grams = list(ngrams(tokens, n))
    return Counter(n_grams)

if __name__ == '__main__':
    app.run(debug=True)
