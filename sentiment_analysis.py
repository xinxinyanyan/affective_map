import os
import glob
from transformers import pipeline
from tqdm import tqdm
import spacy
import argparse
import json


# Function to process the text
def process_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split the content by two or more newlines to handle multiple empty lines as separators
    all_sentences = {
        i: para.strip() for i, para in enumerate(content.split("\n\n")) if para.strip()
    }

    return all_sentences


# Function that extracts the locations and its place in the text
def extract_locations(all_sentences):
    # Load the pre-trained model
    nlp = spacy.load("en_core_web_sm")
    all_locations = {}

    for i, cur_sentence in tqdm(all_sentences.items(), desc="Extracting locations"):
        # Process the text with spacy to detect entities
        doc = nlp(cur_sentence)
        if doc.ents == ():
            continue
        else:
            # if there is location
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC"]:
                    # Associate sentiment with location entity}
                    all_locations[i] = ent.text

    return all_locations


def sentiment_analysis(all_sentences):
    # initialize output
    all_sentiments = {}

    # set up sentiment analysis pipeline
    emotion_pipeline = pipeline(
        "text-classification",
        model="bhadresh-savani/distilbert-base-uncased-emotion",
        truncation=True,
        top_k=1,
    )

    for i, cur_sentence in tqdm(all_sentences.items(), desc="Analyzing sentiment"):
        # Analyze the sentiment of the sentence
        emotion = emotion_pipeline(cur_sentence)
        all_sentiments[i] = emotion[0][0]["label"]

    return all_sentiments


def main():
    parser = argparse.ArgumentParser(description="A script to convert PDFs to texts.")
    parser.add_argument(
        "--input_dir",
        dest="input_dir",
        help="Input folder directory that contains all the texts.",
        default="./texts/clean/",
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        help="Output folder directory that will contain the processed sentiment/location results.",
        default="./results/",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="store_true",
        dest="verbosity",
        default=False,
        help="Verbosity. Default: False.",
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    verbosity = args.verbosity
    if verbosity:
        print(f"\nInput directory: {input_dir}")
        print(f"Output directory: {output_dir}")

    # get all the PDF file path from the folder
    all_text_paths = glob.glob(input_dir + "*_clean.txt")
    if verbosity:
        print(f"\nNumber of text files: {len(all_text_paths)}")

    # process each book
    all_results = {}
    for cur_path in tqdm(all_text_paths, desc="Processing texts"):
        cur_book_name = os.path.basename(cur_path)
        if verbosity:
            print(f"\nProcessing {cur_book_name}")

        # break the book into paragraphs
        cur_book_sentences = process_text(cur_path)

        # perform location extraction on the entire book
        cur_locations = extract_locations(cur_book_sentences)

        # perform sentiment analysis on the entire book
        cur_sentiments = sentiment_analysis(cur_book_sentences)

        all_results[cur_book_name] = {
            "locations": cur_locations,  # {paragraph_id: location}
            "sentiments": cur_sentiments,  # {paragraph_id: sentiment}
            "sentences": cur_book_sentences,  # {paragraph_id: sentence}
        }

    # save the results
    output_path = os.path.join(output_dir, "all_results.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f)

    if verbosity:
        print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
