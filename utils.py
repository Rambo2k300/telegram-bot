COUNTRY_CODES = {
    "880": "Bangladesh",
    "91": "India",
    "1": "USA",
    "44": "UK",
    "971": "UAE"
}

def normalize_number(num):
    return num.replace("+", "").strip()

def detect_country(num):
    for code, country in COUNTRY_CODES.items():
        if num.startswith(code):
            return country
    return "Unknown"
