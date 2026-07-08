from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
# Update this line - allow all origins for Vercel
CORS(app, origins=["*"])  # Allow all origins (works for any Vercel URL)

# Initialize Groq client (Change: Use Groq instead of OpenAI)
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Product database
PRODUCTS = [
    {"id": 1, "name": "iPhone 15", "category": "Phone", "price": 799, "description": "Latest Apple smartphone"},
    {"id": 2, "name": "Samsung Galaxy S24", "category": "Phone", "price": 699, "description": "Android flagship"},
    {"id": 3, "name": "Google Pixel 8", "category": "Phone", "price": 499, "description": "Pure Android experience"},
    {"id": 4, "name": "OnePlus 12", "category": "Phone", "price": 599, "description": "Fast charging performance"},
    {"id": 5, "name": "Xiaomi 14", "category": "Phone", "price": 399, "description": "Budget-friendly premium"},
    {"id": 6, "name": "MacBook Air", "category": "Laptop", "price": 999, "description": "Lightweight M2 chip"},
    {"id": 7, "name": "Dell XPS 13", "category": "Laptop", "price": 899, "description": "Premium Windows laptop"},
    {"id": 8, "name": "Sony WH-1000XM5", "category": "Headphones", "price": 299, "description": "Noise-cancelling"},
    {"id": 9, "name": "AirPods Pro 2", "category": "Headphones", "price": 249, "description": "Premium earbuds"}
]


@app.route('/api/products', methods=['GET'])
def get_products():
    """Return all products"""
    return jsonify(PRODUCTS)


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get AI-powered product recommendations using Groq"""
    try:
        data = request.get_json()
        user_preference = data.get('preference', '').strip()

        if not user_preference:
            return jsonify({'error': 'Please enter your preference'}), 400

        # Create product list for AI prompt
        product_list = '\n'.join([
            f"{p['id']}. {p['name']} - ${p['price']} - {p['category']} - {p['description']}"
            for p in PRODUCTS
        ])

        # Prompt for Groq
        prompt = f"""
        Products available:
        {product_list}

        User wants: "{user_preference}"

        Return ONLY the product IDs (comma-separated) that match this preference.
        Example: "1,3,5"
        Be strict and only recommend products that clearly match.
        If none match, return "none".
        """

        # Call Groq API (Change: Different API call)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Groq's model
            messages=[
                {"role": "system", "content": "You are a product recommendation assistant. Only return product IDs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )

        ai_response = response.choices[0].message.content.strip()

        # Parse AI response
        recommended_products = []
        if ai_response.lower() != 'none':
            try:
                ids = [int(id.strip()) for id in ai_response.split(',')]
                recommended_products = [p for p in PRODUCTS if p['id'] in ids]
            except ValueError:
                recommended_products = []

        return jsonify({
            'recommendations': recommended_products,
            'preference': user_preference
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to get recommendations'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, port=port)