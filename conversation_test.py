from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory


conversation = ConversationChain(
    llm=OpenAI(temperature=0), # deterministic temperature
    verbose=False,
    memory=ConversationBufferMemory()
)

prompt = input("Enter starting prompt: ")

while prompt != "":  # enter blank line to exit
    result = conversation.predict(input=prompt)
    print(result, "\n")
    prompt = input("Enter next prompt: ")

summary_prompt = "Summarise our conversation in 20 or less words"

print("Here is a summary of our conversation:")
result = conversation.predict(input=summary_prompt)
print(result, "\n")
