from langchain import PromptTemplate, OpenAI, LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory

template = "{chat_history}. You are a chatbot having a conversation with a human, as Jarvis in Marvels Iron Man. " \
           "Answer his {question}"

llm = OpenAI(temperature=0)

prompt = PromptTemplate(
    input_variables=["chat_history", "question"],
    template=template)

memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
)

question = input("Enter first question: ")

while question != "":  # enter blank line to exit
    result = llm_chain.predict(question=question)
    print(result, "\n")
    question = input("Enter next question: ")