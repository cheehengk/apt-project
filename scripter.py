from PyPDF2 import PdfReader

pdfReader = PdfReader('Chapter1Solutions.pdf')

num_pages = len(pdfReader.pages)
print("Number of Pages: ", num_pages)

for i in range(num_pages):
    text = pdfReader.pages[i].extract_text()
    print(text)
