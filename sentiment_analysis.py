from transformers import pipeline
from collections import defaultdict
from tqdm import tqdm
import spacy
import pandas as pd


def load_paragraphs_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split the content by two or more newlines to handle multiple empty lines as separators
    paragraphs = [para.strip() for para in content.split("\n\n") if para.strip()]

    return paragraphs


classifier = pipeline(
    "text-classification",
    model="bhadresh-savani/distilbert-base-uncased-emotion",
    top_k=1,
)
data_paths = ["/Users/xinyan/Desktop/DH/Affective_Map/example_cut.txt"]

# process each book
all_books_results = []
for cur_path in data_paths:
    cur_book = load_paragraphs_from_file(cur_path)
    # analyze each paragraph
    for i in tqdm(range(len(cur_book))):
        cur_parapraph = cur_book[i]
        print(cur_parapraph)
        # sentiment analysis
        cur_prediction = classifier(
            cur_parapraph,
        )
        # location extraction

        # Load the pre-trained model
        location_pipeline = spacy.load("en_core_web_sm")
        # Load the emotion classifier pipeline from transformers
        emotion_pipeline = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )

        # Process the text with spaCy to detect entities
        all_locations = location_pipeline(cur_parapraph)

        # Dictionary to hold locations and their sentiment
        location_emotions = {}

        # Iterate over the sentences
        for sentence in all_locations.sents:
            # Analyze the sentiment of the sentence
            emotion = emotion_pipeline(sentence.text)

            # Search for GPE (Geo-Political Entities) within the sentence
            for ent in sentence.ents:
                if ent.label_ in ["GPE", "LOC"]:
                    # Associate sentiment with location entity
                    location_emotions[ent.text] = (
                        # sentence.text,
                        emotion[0]["label"],
                        emotion[0]["score"],
                    )

    # Now we have a dictionary with locations and their associated sentence and sentiment
    for location, (label, score) in location_emotions.items():
        print(f"Location: {location}, Sentiment: {label}, Score: {score}")

    all_books_results.append(location_emotions)
    exit()


# Example list of sentiment strings
sentiment_outputs = [
    "Location: Beijing, Sentence: 'It is a beautiful city', Sentiment: Positive, Score: 0.9",
    "Location: Shanghai, Sentence: 'Not what I expected', Sentiment: Negative, Score: 0.8",
    # Add more sentiment output strings here...
]


# Function to parse the sentiment output
def parse_sentiment_output(output):
    parts = output.split(", ")
    location = parts[0].split(": ")[1]
    sentence = parts[1].split(": ")[1].strip("'")
    sentiment = parts[2].split(": ")[1]
    score = float(parts[3].split(": ")[1])
    return location, sentence, sentiment, score


# Parse the outputs and create a list of tuples
parsed_data = [parse_sentiment_output(output) for output in sentiment_outputs]

# Create a DataFrame from the parsed data
sentiment_data = pd.DataFrame(
    parsed_data, columns=["Location", "Sentence", "Sentiment", "Score"]
)

print(sentiment_data)
