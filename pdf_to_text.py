from pdfminer.high_level import extract_text

text = extract_text("/Users/xinyan/Desktop/DH/Affective_Map/example_cut.pdf")
output_file = open("//Users/xinyan/Desktop/DH/Affective_Map/example_cut.txt", "w")
output_file.write(text)
output_file.close()
