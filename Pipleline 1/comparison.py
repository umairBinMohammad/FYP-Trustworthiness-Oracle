from sentence_transformers import SentenceTransformer, util

# Load the pre-trained sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def compare_full_paragraphs(explanation_file, nlp_file):
    """Compare the entire explanation with the full NLP summary."""
    with open(explanation_file, 'r') as f:
        explanation_text = f.read().strip()

    with open(nlp_file, 'r') as f:
        nlp_summary = f.read().strip()

    # Normalize case
    explanation_text = explanation_text.lower()
    nlp_summary = nlp_summary.lower()

    # Encode both texts
    expl_embed = model.encode(explanation_text, convert_to_tensor=True)
    nlp_embed = model.encode(nlp_summary, convert_to_tensor=True)

    # Compute similarity
    score = util.pytorch_cos_sim(expl_embed, nlp_embed).item()

    # Report
    print("🔍 Comparing Full Explanation with NLP Summary:\n")
    print(f"→ Semantic Match Score: {score:.2f}")
    print(f"→ Result: {'✅ Match' if score >= 0.6 else '❌ No Match'}")

if __name__ == "__main__":
    compare_full_paragraphs("explanation.txt", "nlp_output.txt")

