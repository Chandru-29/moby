from google import genai

client = genai.Client()

def structure_document(raw_text: str):

    prompt = f"""
Convert the following OCR document into structured JSON.

Extract:

- document_number
- document_date
- customer
- destination
- quality
- description
- chemical_composition
- heat_numbers
- mechanical_tests
- dimensions

Return STRICT JSON only.

OCR TEXT:
{raw_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt
    )

    return response.text