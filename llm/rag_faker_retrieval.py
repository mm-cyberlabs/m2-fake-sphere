import os
import logging  # For logging messages
import time  # For measuring execution time
from tqdm import tqdm  # For showing a progress bar

import faiss
from attr.validators import max_len
from jedi.settings import cache_directory
from sentence_transformers import SentenceTransformer

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

CACHE = './cache'
# Set a cache folder to avoid repeated network downloads
os.environ['TRANSFORMERS_CACHE'] = CACHE
os.environ['HF_HUB_TIMEOUT'] = "60"

# Configure logging to display INFO level messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load all Markdown files
docs_dir = 'faker_20250331_225454'
docs = []
doc_paths = [os.path.join(docs_dir, f) for f in os.listdir(docs_dir) if f.endswith('.md')]
logging.info("Loading markdown files from directory: {}".format(docs_dir))
for path in tqdm(doc_paths, desc="Loading docs"):
    with open(path, 'r', encoding='utf-8') as file:
        docs.append(file.read())
logging.info("Loaded {} markdown files.".format(len(docs)))

# Load a pre-trained SentenceTransformer model (cached locally)
logging.info("Loading SentenceTransformer model...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=CACHE)
doc_embedding = embed_model.encode(docs)

# Build a FAISS index for performance retrieval
index = faiss.IndexFlatL2(doc_embedding.shape[1])
index.add(doc_embedding)
logging.info("FAISS index built.")


# Helper to retrieve the most relevant documentation snippet for a given query.
def retrieve_context(query, k=1):
    query_embedding = embed_model.encode([query])
    distances, indices = index.search(query_embedding, k)
    return [docs[i] for i in indices[0]]


# Set up a text generation pipeline (using T5 as an example)
PRETRAINED_MODEL = 't5-base'
tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL, cache_dir=CACHE)
model = AutoModelForSeq2SeqLM.from_pretrained(PRETRAINED_MODEL, cache_dir=CACHE)
generator = pipeline('text2text-generation', model=model, tokenizer=tokenizer)


# Combine retrieval and generation to implement the RAG
def generate_faker_function(field_name):
    logging.info("Generating Faker function for field: '{}'".format(field_name))
    # retrieve the relevant documentation snippet for the given field name
    context_list = retrieve_context(field_name, k=1)
    context = context_list[0] if context_list else ''
    # build a prompt including the retrieved context and the query
    prompt = (f"Using the following documentation: {context} "
              f"Which Faker function should be used for the following '{field_name}'?")
    print(f"Prompt -> {prompt}")

    output = generator(prompt, max_length=100)
    return output[0]['generated_text']


if __name__ == "__main__":
    start_time = time.time()  # Start timer
    result = generate_faker_function('first_name')
    result1 = generate_faker_function('address_line1')
    result2 = generate_faker_function('credit_card_number')
    result3 = generate_faker_function('ssn')
    print(f"\t* first_name -> {result}")
    print(f"\t* address_line1 -> {result1}")
    print(f"\t* credit_card_number -> {result2}")
    print(f"\t* ssn -> {result3}")
    elapsed_time = time.time() - start_time  # Compute elapsed time
    logging.info("Execution time: {:.2f} seconds".format(elapsed_time))
