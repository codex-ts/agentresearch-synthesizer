import json
import re


def extract_json(text: str) -> str:
    import re

    # Remove markdown code blocks
    text = re.sub(r"```(?:json)?\s*|```", "", text)

    # Find ALL JSON objects
    matches = re.findall(r"\{.*?\}", text, re.DOTALL)

    if not matches:
        raise ValueError("No JSON found in output")

    # Take the LARGEST one (most likely full report)
    json_str = max(matches, key=len)

    return json_str


def parse_report(output: str) -> dict:
    # Remove markdown
    text = re.sub(r"```(?:json)?", "", output)
    text = text.replace("```", "").strip()

    # Extract ALL JSON blocks
    matches = re.findall(r"\{.*\}", text, re.DOTALL)

    if not matches:
        raise ValueError("No JSON found")

    # Pick the largest JSON (most likely the full report)
    json_str = max(matches, key=len)

    # Clean common issues
    json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print("\n--- RAW OUTPUT ---\n", output)
        print("\n--- EXTRACTED JSON ---\n", json_str)
        raise ValueError(f"Invalid JSON format: {e}")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print("\n--- RAW OUTPUT ---\n")
        print(output)
        print("\n--- CLEANED JSON ---\n")
        print(json_str)
        raise ValueError(f"Invalid JSON format: {e}")

def validate_report(report: dict) -> dict:
    required_fields = ["title", "summary", "key_findings", "why_it_matters", "sources"]
    for field in required_fields:
        if field not in report:
            raise ValueError(f"Missing field: {field}")
    if not isinstance(report["key_findings"], list):
        raise ValueError("key_findings must be a list")
    if not isinstance(report["sources"], list):
        raise ValueError("sources must be a list")
    return report

def parse_and_validate_report(output: str) -> dict:
    parsed = parse_report(output)
    validated = validate_report(parsed)
    return validated