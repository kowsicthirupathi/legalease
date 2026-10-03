import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# Find the LegalEase project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env from the LegalEase project folder
load_dotenv(PROJECT_ROOT / ".env")


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check C:\\Users\\ADMIN\\Desktop\\legalease\\.env"
    )


client = genai.Client(api_key=api_key)


def generate_legal_document(
    document_type,
    parties,
    terms,
    effective_date
):
    prompt = f"""
You are a legal document drafting assistant.

Generate a professional and clearly structured {document_type}.

Parties:
{parties}

Effective Date:
{effective_date}

Important Terms:
{terms}

Requirements:
- Create a professional legal document.
- Use clear headings and sections.
- Include the provided parties, date, and terms.
- Do not invent important facts that were not provided.
- Make the document editable and easy to understand.
- Add a short disclaimer that this document is for informational
  purposes and should be reviewed by a qualified legal professional.

Generate only the document content.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text