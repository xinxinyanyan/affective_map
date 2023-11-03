import argparse
import glob
import os
from tqdm import tqdm
from pdfminer.high_level import extract_text


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
    verbosity = args.verbosity
    if verbosity:
        print(f"\nInput directory: {input_dir}")
        print(f"Output directory: {output_dir}")

    # get all the PDF file path from the folder
    all_pdf_paths = glob.glob(input_dir + "*.pdf")
    if verbosity:
        print(f"\nNumber of PDF files: {len(all_pdf_paths)}")

    # convert all the PDFs to texts
    for pdf_path in tqdm(all_pdf_paths, desc="Converting PDFs to texts"):
        # get the text
        text = extract_text(pdf_path)
        # write the text to a file
        # get the file name
        file_name = os.path.basename(pdf_path).split(".pdf")[0]
        output_file = open(output_dir + file_name + ".txt", "w")
        output_file.write(text)
        output_file.close()


if __name__ == "__main__":
    main()
