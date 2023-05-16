import openai

openai.api_key = "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"


def prompt_reply(input_prompt):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": input_prompt}
        ],
        temperature=0
    )
    output = completion.choices[0].message.content
    print(output)


message = input("Enter Prompt: ")
prompt_reply(message)
