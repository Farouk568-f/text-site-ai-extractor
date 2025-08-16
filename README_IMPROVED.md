import requests

# استخراج نص من رابط مع حد أدنى 1000
payload = {
    "url": "https://sdaia.gov.sa/ar/SDAIA/about/Pages/AboutAI.aspx",
    "min_length": 1000
}

response = requests.post("http://localhost:5001/extract-single/", json=payload)
result = response.json()

if result["status"] == "success":
    print(f"عدد الفقرات: {result['paragraphs_count']}")
    print(f"طول النص: {result['text_length']}")
    print(f"النص: {result['text'][:200]}...")