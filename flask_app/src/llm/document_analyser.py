import os
from langchain import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import AnalyzeDocumentChain
from PyPDF2 import PdfReader
from dotenv import dotenv_values

from flask_app.src.processor.create_video import generate_paths, get_txt_rank

PARENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
TEXT_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Texts')

env_vars = dotenv_values(os.path.join(PARENT_PATH, "src/.env"))
openai_rotational_keys = [env_vars.get("OPENAI_KEY_1"), env_vars.get("OPENAI_KEY_2")]


def get_key(key):
    return openai_rotational_keys[key]


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

    docs_path = generate_paths('%s' % TEXT_PATH)
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
    pdf = PdfReader(path)
    page_count = len(pdf.pages)
    print("Number of Pages: ", page_count)

    text_data = []
    text_string = ''
    page_counter = 0

    for i in range(page_count):
        text_string += pdf.pages[i].extract_text()
        page_counter += 1
        if page_counter == 5:
            text_data.append(text_string)
            text_string = ''
            page_counter = 0

    if not text_string == '':
        text_data.append(text_string)

    for j, txt in enumerate(text_data):
        text_path = TEXT_PATH + '/' + str(j) + '.txt'
        text_file = open(text_path, "w")
        text_file.write(txt)
        text_file.close()
