# Import the necessary classes from the transformers library.
# The AutoModelForCausalLM class is used to load a language model,

# and AutoTokenizer is used to load the corresponding tokenizer.

from transformers import AutoModelForCausalLM, AutoTokenizer

import torch


# The name of the model on Hugging Face. This identifies the specific

# model and version to be loaded.

model_name = "Qwen/Qwen2.5-32B-Instruct"


# Load the model from the specified name.

# `torch_dtype="auto"` automatically selects the most efficient

# data type (e.g., float16) to save memory.

# `device_map="auto"` automatically distributes the model across

# available devices (like GPUs) to fit it into memory.

print("Loading model...")

model = AutoModelForCausalLM.from_pretrained(

    model_name,

    torch_dtype="auto",

    device_map="auto",

    trust_remote_code=True # This is often needed for custom model architectures

)

print("Model loaded.")


# Load the tokenizer. This is a critical step that converts text

# into tokens (numerical representations) that the model understands.

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

print("Tokenizer loaded.")


# Define the conversation with a system prompt and a user prompt.

# The system prompt sets the persona and role of the assistant.

# The user prompt is the actual question or request.

prompt_text = "Give me a short introduction to large language model."

messages = [

    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},

    {"role": "user", "content": prompt_text}

]


# Apply the chat template to the messages. This formats the conversation

# into a single string that the model expects as input.

# `tokenize=False` ensures the output is a string, not token IDs.

# `add_generation_prompt=True` adds a special token to signal the start

# of the model's response.

text = tokenizer.apply_chat_template(

    messages,

    tokenize=False,

    add_generation_prompt=True

)


# Print the formatted text to see what the model is actually receiving.

# This is a useful debugging step.

print("\n--- Formatted Input Text ---\n")

print(text)

print("\n" + "-"*30 + "\n")


# Tokenize the formatted text and move it to the same device as the model.

# The `return_tensors="pt"` argument returns PyTorch tensors.

model_inputs = tokenizer([text], return_tensors="pt").to(model.device)


# Generate the response from the model.

# `**model_inputs` unpacks the dictionary of inputs.

# `max_new_tokens` sets the maximum length of the generated response.

# The result is a tensor of token IDs.

print("Generating response...")

generated_ids = model.generate(

    **model_inputs,

    max_new_tokens=512,

    do_sample=True, # Add a sampling strategy for more creative output

    temperature=0.7, # Controls the randomness of the output

    top_p=0.95 # Controls the diversity of the output

)

# Extract only the newly generated tokens from the output.

# This prevents re-decoding the input prompt.

input_ids_len = model_inputs.input_ids.shape[1]

generated_ids = generated_ids[0][input_ids_len:]


# Decode the generated token IDs back into a human-readable string.

# `skip_special_tokens=True` removes any special tokens (like `<s>` or `<eos>`).

response = tokenizer.decode(generated_ids, skip_special_tokens=True)


# Print the final response.

print("--- Generated Response ---\n")

print(response)