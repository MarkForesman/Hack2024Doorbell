from fuzzywuzzy import fuzz, process
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from main import di_ocr
import os
from dotenv import load_dotenv

load_dotenv(override=True)

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Sample string (shipping label)
shipping_label = "13.2 Lbs 12/19 DHO3 SMIL& 19426 OIL CENTER BLVD 77073-3300 Courtney Crum HOUSTON , TX United StatesTBA310617993084CYCLE 1"

# List of "source of truth names"
truth_names = ["Morgan Winter", "Courtney Crum", "Jose Rodriguez", "Mark Foresman", "Courtney Kouba"]

# Fuzzy matching threshold
threshold = 80

def extract_name_from_label(label, names, threshold=80):
    # Extract words and phrases likely to be names (heuristics: based on presence of upper-case letters)
    words = [word for word in label.split() if any(char.isupper() for char in word)]
    
    # Join consecutive potential name parts
    possible_name = ' '.join(words)

    # Perform fuzzy matching
    match = process.extractOne(possible_name, names, scorer=fuzz.partial_ratio)
    
    # Check if the match is above the threshold
    if match[1] >= threshold:
        return match[0]
    return None

from pathlib import Path

# Path to the folder
folder_path = Path('./images')

# Loop through files in the folder
for file in folder_path.iterdir():
    if file.is_file():
        print(f"Processing file: {file.name}")
        shipping_label = di_ocr(document_intelligence_client, f"./images/{file.name}")
        matched_name = extract_name_from_label(shipping_label, truth_names, threshold)
        print(f"OCR'D NAME: ---------> {matched_name}")
        
# Extract name from shipping label
# for item in blank:

