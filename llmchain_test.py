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

# Generating summary with new chain using the old memory
summary_template = "{chat_history} Summarise our conversation in {words} words or less"
summary_prompt = PromptTemplate(
    input_variables=["chat_history", "words"],
    template=summary_template)
summary_chain = LLMChain(
    llm=llm,
    prompt=summary_prompt,
    memory=memory,
)
print("Here is a summary of our conversation:")
summary_result = summary_chain.predict(words="10")
print(summary_result)