import ollama

response = ollama.chat(model="llama3.2", messages=[
    {"role": "user", "content": "Selamat pagi, apa kabar?"}
])

print(response['message']['content'])
