import pickle
import spacy
from spacy.training.example import Example
from pathlib import Path
import random
from tqdm import tqdm

# Read the links from the file
links_file = "valid_links.txt"
with open(links_file, "r") as file:
    links = [line.strip() for line in file.readlines()]


# Format the links with "PRODUCT" entity label
formatted_links = []
for link in links:
    entity_label = (0, len(link), "PRODUCT")
    for word in link.split():
        start_idx = link.index(word)
        end_idx = start_idx + len(word)
        entity_label = (start_idx, end_idx, "PRODUCT")
        formatted_link = (link, {"entities": [entity_label]})
        formatted_links.append(formatted_link)

# Read the product names from the file
product_names_file = "product_names.txt"
with open(product_names_file, "r") as file:
    product_names = [line.strip() for line in file.readlines()]

# Format the product names with "PRODUCT" entity label
for product_name in product_names:
    entity_label = (0, len(product_name), "PRODUCT")
    formatted_product_name = (product_name, {"entities": [entity_label]})
    formatted_links.append(formatted_product_name)


# Train the NER model
model = None
output_dir = Path("ner/")
n_iter = 25

# Load the model if it exists
if model is not None:
    nlp = spacy.load(model)
    print("Loaded model '%s'" % model)
else:
    # if not, crete a new empty model
    nlp = spacy.blank('en')
    print("Created blank 'en' model")

if 'ner' not in nlp.pipe_names:
    ner = nlp.create_pipe('ner')
    nlp.add_pipe('ner', last=True)
else:
    ner = nlp.get_pipe('ner')

# Adding labels to ner
for _, annotations in formatted_links:
    for ent in annotations.get('entities'):
        ner.add_label(ent[2])


example = []
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
with nlp.disable_pipes(*other_pipes):  # only train NER
    optimizer = nlp.begin_training()
    for itn in range(n_iter):
        print(f'Iteration: {itn + 1}')
        random.shuffle(formatted_links) 
        losses = {}
        for text, annotations in tqdm(formatted_links): 
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update(
                [example],
                drop=0.5,
                sgd=optimizer,
                losses=losses
            )
        print(losses)

if output_dir is not None:
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir()
    nlp.to_disk(output_dir)
    print("Saved model to", output_dir)
pickle.dump(nlp, open("links.pkl", "wb" ))


doc = nlp("https://www.skandium.com/products/ch24-soft")

for ent in doc.ents:
    print(ent.label_ + '  ------>   ' + ent.text)