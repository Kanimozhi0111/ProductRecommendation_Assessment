from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq

app = Flask(__name__)
CORS(app, origins=["*"])

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


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(PRODUCTS)


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        user_preference = data.get('preference', '').strip()

        if not user_preference:
            return jsonify({'error': 'Please enter your preference'}), 400

        # Simple fallback first (before using Groq)
        # This ensures the endpoint works even if Groq fails
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            # Fallback to simple keyword matching
            recommended = []
            keywords = user_preference.lower().split()
            for product in PRODUCTS:
                text = f"{product['name']} {product['category']} {product['description']} {product['price']}".lower()
                for keyword in keywords:
                    if keyword in text and product not in recommended:
                        recommended.append(product)
                        break
            return jsonify({'recommendations': recommended, 'fallback': True})

        # Use Groq API
        client = Groq(api_key=api_key)

        product_list = '\n'.join([
            f"{p['id']}. {p['name']} - ${p['price']} - {p['category']} - {p['description']}"
            for p in PRODUCTS
        ])

        prompt = f"""
        Products available:
        {product_list}

        User wants: "{user_preference}"

        Return ONLY the product IDs (comma-separated) that match this preference.
        Example: "1,3,5"
        If none match, return "none".
        """

        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a product recommendation assistant. Only return product IDs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )

        ai_response = response.choices[0].message.content.strip()

        recommended_products = []
        if ai_response.lower() != 'none':
            try:
                ids = [int(id.strip()) for id in ai_response.split(',')]
                recommended_products = [p for p in PRODUCTS if p['id'] in ids]
            except:
                pass

        return jsonify({'recommendations': recommended_products, 'fallback': False})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


# For Vercel - this is required
def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)
app = app