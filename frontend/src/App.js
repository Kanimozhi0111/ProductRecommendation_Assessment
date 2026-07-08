import React, { useState, useEffect } from 'react';
import './App.css';
import { products } from './products';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [preference, setPreference] = useState('');
  const [displayProducts, setDisplayProducts] = useState(products);
  const [allProducts, setAllProducts] = useState(products);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isRecommended, setIsRecommended] = useState(false);

  // Fetch products from backend on load
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/products`);
      setAllProducts(response.data);
      setDisplayProducts(response.data);
    } catch (err) {
      console.error('Failed to fetch products:', err);
      // Fallback to local products
      setAllProducts(products);
      setDisplayProducts(products);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!preference.trim()) {
      setError('Please enter your preference');
      return;
    }

    setLoading(true);
    setError('');
    setIsRecommended(false);

    try {
      const response = await axios.post(`${API_URL}/api/recommendations`, {
        preference: preference.trim()
      });

      const recommendations = response.data.recommendations;

      if (recommendations.length === 0) {
        setError('No products match your preference. Try different keywords.');
        setDisplayProducts([]);
      } else {
        setDisplayProducts(recommendations);
        setIsRecommended(true);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get recommendations. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const resetProducts = () => {
    setDisplayProducts(allProducts);
    setIsRecommended(false);
    setPreference('');
    setError('');
  };

  return (
    <div className="app">
      <header>
        <h1>🛍️ AI Product Recommender</h1>
        <p>Tell me what you want, and I'll find the perfect products</p>
      </header>

      <form onSubmit={handleSubmit} className="search-form">
        <input
          type="text"
          placeholder="e.g., I want a phone under $500"
          value={preference}
          onChange={(e) => setPreference(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? '🤔 Thinking...' : '🔍 Get Recommendations'}
        </button>
        {isRecommended && (
          <button type="button" onClick={resetProducts} className="reset-btn">
            📋 Show All
          </button>
        )}
      </form>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing your preferences with AI...</p>
        </div>
      )}

      <div className="product-section">
        <h2>
          {isRecommended ? '✨ Recommended Products' : '📦 All Products'}
          {isRecommended && (
            <span className="badge">🤖 AI Powered</span>
          )}
          <span className="count">{displayProducts.length} products</span>
        </h2>

        <div className="product-grid">
          {displayProducts.length === 0 && !loading ? (
            <p className="no-products">No products to display</p>
          ) : (
            displayProducts.map(product => (
              <div key={product.id} className="product-card">
                <span className="product-category">{product.category}</span>
                <h3>{product.name}</h3>
                <p className="description">{product.description}</p>
                <div className="price">${product.price}</div>
                <div className="product-id">ID: {product.id}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default App;