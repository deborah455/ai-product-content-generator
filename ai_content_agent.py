import csv
import os
from openai import OpenAI, OpenAIError

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Input and output files
input_file = "products.csv"
output_file = "generated_content.txt"

def generate_mock_description(product_name, features):
    """Generate a mock AI-style product description (fallback mode)."""
    return (
        f"✨ {product_name} ✨\n"
        f"Experience innovation like never before! "
        f"This product features {features.lower()} to bring you comfort, "
        f"efficiency, and a touch of futuristic design. "
        f"Perfect for everyday use and built for dreamers like you.\n"
    )

def generate_ai_description(product_name, features):
    """Try generating real AI description using OpenAI."""
    try:
        prompt = (
            f"Write a short, captivating product description for '{product_name}' "
            f"highlighting these features: {features}. Keep it under 80 words, "
            f"make it sound professional and appealing."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative marketing copywriter."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()

    except OpenAIError as e:
        print(f"[Warning] OpenAI API unavailable or quota exceeded. Using mock text for {product_name}.")
        return generate_mock_description(product_name, features)

# --- Main Logic ---
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    with open(output_file, "w", encoding='utf-8') as outfile:
        outfile.write("Generated Product Descriptions\n\n")
        for row in reader:
            product_name = row["Product Name"]
            features = row["Features"]
            description = generate_ai_description(product_name, features)
            outfile.write(f"{product_name}\n{description}\n\n")

print("✅ Content generation complete! Check 'generated_content.txt'.")
