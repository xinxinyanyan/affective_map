from transformers import pipeline
from collections import defaultdict


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
data_paths = ["/Users/xinyan/Desktop/DH/Affective_Map/example.txt"]

# process each book
all_sentiments = []
for cur_path in data_paths:
    cur_book = load_paragraphs_from_file(cur_path)
    # analyze each paragraph
    for i in range(len(cur_book)):
        cur_parapraph = cur_book[i]
        # sentiment analysis
        cur_prediction = classifier(
            cur_parapraph,
        )
        # location extraction
        import spacy

        # Load the pre-trained model
        nlp = spacy.load("en_core_web_sm")
        # Load the emotion classifier pipeline from transformers
        emotion_pipeline = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )

        # Sample text
        text = cur_parapraph

        # Process the text with spaCy to detect entities
        doc = nlp(text)

        # Dictionary to hold locations and their sentiment
        location_emotions = {}

        # Iterate over the sentences
        for sentence in doc.sents:
            # Analyze the sentiment of the sentence
            emotion = emotion_pipeline(sentence.text)

            # Search for GPE (Geo-Political Entities) within the sentence
            for ent in sentence.ents:
                if ent.label_ in ["GPE", "LOC"]:
                    # Associate sentiment with location entity
                    location_emotions[ent.text] = (
                        sentence.text,
                        emotion[0]["label"],
                        emotion[0]["score"],
                    )

        # Now we have a dictionary with locations and their associated sentence and sentiment
        for location, (sentence, label, score) in location_emotions.items():
            print(
                f"Location: {location}, Sentence: '{sentence}', Sentiment: {label}, Score: {score}"
            )
