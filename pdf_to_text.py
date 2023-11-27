import argparse
import glob
import os
from tqdm import tqdm
from pdfminer.high_level import extract_text
from openai import OpenAI
import json

client = OpenAI(api_key="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")


# helper function that formats the request to openai
def get_completion(prompt, model="gpt-3.5-turbo", temperature=0):
    # def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=temperature
    )
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="A script to convert PDFs to texts.")
    parser.add_argument(
        "--input_dir",
        dest="input_dir",
        help="Input folder directory that contains all the PDFs.",
        default="./books/",
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        help="Output folder directory that will contain all the converted texts.",
        default="./texts/",
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
    all_pdf_paths = glob.glob(input_dir + "*.pdf")
    if verbosity:
        print(f"\nNumber of PDF files: {len(all_pdf_paths)}")

    # convert all the PDFs to texts
    for pdf_path in all_pdf_paths:
        if verbosity:
            print(f"\nProcessing {pdf_path}")

        # check if the associated text file already exists
        file_name = os.path.basename(pdf_path).split(".pdf")[0]
        txt_path = os.path.join(output_dir, file_name + ".txt")
        if os.path.exists(txt_path):
            if verbosity:
                print(f"Text file {txt_path} already exists")
            continue

        # get the text
        text = extract_text(pdf_path)

        # write the text to a file
        output_file = open(txt_path, "w")
        output_file.write(text)
        output_file.close()

    # get all the PDF file path from the folder
    all_txt_paths = glob.glob(output_dir + "*.txt")

    for txt_path in all_txt_paths:
        if verbosity:
            print(f"\nCleaning {txt_path}")
        # load the text
        with open(txt_path, "r") as f:
            text_list = f.readlines()
        # combine into strings
        text = "".join(text_list)

        # split the text with ".\n"
        text = text.split(".\n\n")
        text = [t + "." for t in text]
        cleaned_text = ""
        for cur_text in tqdm(text, desc="Cleaning text"):
            prompt = f"""
                Break the paragraphs delimited by triple backticks into sentences. Separate each sentence with an empty line. '''{cur_text}'''
            """
            cur_response = get_completion(prompt)
            cleaned_text += cur_response + "\n"

        # save the cleaned text
        clean_txt_path = txt_path.replace(".txt", "_clean.txt")
        with open(clean_txt_path, "w") as f:
            f.writelines(cleaned_text)


if __name__ == "__main__":
    main()
