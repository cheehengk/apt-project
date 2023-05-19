import os
from langchain import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import AnalyzeDocumentChain
from create_video import get_txt_rank, generate_paths
from scripter import get_key
from PyPDF2 import PdfReader
import requests


def slice_script(script):
    words = script.split()
    slices = []
    chunk_size = 10

    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        slices.append(chunk)

    return slices


def analyse_doc(key):
    os.environ['OPENAI_API_KEY'] = get_key(key)

    docs_path = generate_paths('../Texts')
    docs_path.sort(key=get_txt_rank)

    script = ''

    for filepath in docs_path:
        with open(filepath) as d:
            doc = d.read()

        llm = OpenAI(temperature=0)
        summary_chain = load_summarize_chain(llm, chain_type="map_reduce")
        summarize_document_chain = AnalyzeDocumentChain(combine_docs_chain=summary_chain)
        summary = summarize_document_chain.run(doc)
        script += summary

    return slice_script(script)


def extract_pdf(path):
    pdfReader = PdfReader(path)
    pages = len(pdfReader.pages)
    print("Number of Pages: ", pages)

    text_data = []
    text_string = ''
    page_counter = 0

    for i in range(pages):
        text_string += pdfReader.pages[i].extract_text()
        page_counter += 1
        if page_counter == 5:
            text_data.append(text_string)
            text_string = ''
            page_counter = 0

    if not text_string == '':
        text_data.append(text_string)

    for j, txt in enumerate(text_data):
        text_path = 'Texts/' + str(j) + '.txt'
        text_file = open(text_path, "w")
        text_file.write(txt)
        text_file.close()
