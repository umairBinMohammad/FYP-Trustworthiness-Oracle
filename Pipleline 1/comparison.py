from sentence_transformers import SentenceTransformer, util

# Load the pre-trained sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def is_semantic_match(nlp_line, explanation, threshold=0.6):
    """Compare a line of NLP output with the explanation using cosine similarity."""
    nlp_embed = model.encode(nlp_line, convert_to_tensor=True)
    expl_embed = model.encode(explanation, convert_to_tensor=True)
    score = util.pytorch_cos_sim(nlp_embed, expl_embed).item()
    return score >= threshold, score

def compare_explanation_with_nlp(explanation_file, nlp_file):
    """Compare the explanation with NLP output from the text files."""
    # Load the explanation text from the file
    with open(explanation_file, 'r') as expl_file:
        explanation_text = expl_file.read().strip()

    # Load the NLP output from the file (assuming each line is a change description)
    with open(nlp_file, 'r') as nlp_file:
        nlp_lines = nlp_file.readlines()

    print("Comparing Explanation with NLP Summary:\n")
    
    # Iterate through each NLP line and compare with the explanation
    for nlp_line in nlp_lines:
        nlp_line = nlp_line.strip()  # Clean up any leading/trailing whitespace
        match, score = is_semantic_match(nlp_line, explanation_text)
        print(f"• {nlp_line}\n  → Match: {'✅' if match else '❌'} (Score: {score:.2f})\n")

if __name__ == "__main__":
    # Adjust paths to point to your actual files
    explanation_file = 'explanation.txt'  # File with the explanation text
    nlp_file = 'nlp_output.txt'          # File with the NLP output

    compare_explanation_with_nlp(explanation_file, nlp_file)




