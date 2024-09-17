from fuzzywuzzy import fuzz, process

# Fuzzy matching threshold
threshold = 80

def extract_name_from_label(shipping_label: str, employee_list: list[str], threshold=80):
    # Extract words and phrases likely to be names (heuristics: based on presence of upper-case letters)
    words = [word for word in shipping_label.split() if any(char.isupper() for char in word)]
    
    # Join consecutive potential name parts
    possible_name = ' '.join(words)

    # Perform fuzzy matching
    match = process.extractOne(possible_name, employee_list, scorer=fuzz.partial_ratio)
    
    # Check if the match is above the threshold
    if match[1] >= threshold:
        return match[0]

    
    matched_name = extract_name_from_label(shipping_label, truth_names, threshold)
    if matched_name is None:
        print("No OCR found")
        print("")
        return None
    print(f"OCR'D NAME: ---------> {matched_name}")
