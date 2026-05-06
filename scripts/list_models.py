import google.generativeai as genai
API_KEY = "AIzaSyBQ3zSI0u876OsBtCkoEk3Tgy5Q8pLV8Bc"
genai.configure(api_key=API_KEY)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
