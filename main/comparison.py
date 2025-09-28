from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModel
import torch #pip install torch
import os
import logging
import transformers
import datasets #pip install datasets
import sentence_transformers
import contextlib
import sys
import os



@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, 'w') as fnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = fnull
        sys.stderr = fnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

# Silence Hugging Face and tokenizers
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "true"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Disable all logging
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("filelock").setLevel(logging.ERROR)
logging.getLogger("datasets").setLevel(logging.ERROR)
logging.getLogger("torch").setLevel(logging.ERROR)

# Force transformers to shut up entirely (legacy)
transformers.logging.set_verbosity_error()

# Define semantic models to use (model name: loading function)
semantic_models = {
    # Sentence-Transformers (optimized for semantic similarity)
    "all-MiniLM-L6-v2": lambda: SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"),
    "paraphrase-MiniLM-L3-v2": lambda: SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L3-v2"),
    "multi-qa-MiniLM-L6-cos-v1": lambda: SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-cos-v1"),
    "sentence-t5-base": lambda: SentenceTransformer("sentence-transformers/sentence-t5-base"),
    
    # Hugging Face models adapted for sentence embeddings (STS-evaluated)
    "intfloat/e5-base": lambda: SentenceTransformer("intfloat/e5-base"),
    "BAAI/bge-small-en-v1.5": lambda: SentenceTransformer("BAAI/bge-small-en-v1.5"),
}

def compare_with_models(explanation_file, nlp_file):
    """Compare explanation and summary using multiple semantic models."""
    with open(explanation_file, 'r') as f:
        explanation_text = f.read().strip()

    with open(nlp_file, 'r') as f:
        nlp_summary = f.read().strip()

    # Normalize case
    explanation_text = explanation_text.lower()
    nlp_summary = nlp_summary.lower()

    print("🔍 Comparing Full Explanation with NLP Summary:\n")

    for model_name, load_model in semantic_models.items():
        try:
            with suppress_output():
                model = load_model()
            # Encode
            expl_embed = model.encode(explanation_text, convert_to_tensor=True)
            nlp_embed = model.encode(nlp_summary, convert_to_tensor=True)
            # Cosine similarity
            score = util.pytorch_cos_sim(expl_embed, nlp_embed).item()
            print(f"→ [{model_name}]: Semantic Match Score: {score:.2f} | {'Trustworthy' if score >= 0.6 else 'Untrustworthy'}")
        except Exception as e:
            print(f"⚠️ Error using model '{model_name}': {e}")

if __name__ == "__main__":
    compare_with_models("explanation.txt", "nlp_output.txt")
