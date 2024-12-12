import { useState } from 'react';

const AddProduct = ({ onAdd }) => {
  const [formData, setFormData] = useState({
    productName: '',
    costPrice: '',
    quantity: '',
    sellPrice: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('http://localhost:5000/api/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ action: 'add', ...formData })
    });
    if (response.ok) {
      setFormData({ productName: '', costPrice: '', quantity: '', sellPrice: '' });
      onAdd();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center mb-6">Add Product</h2>
      <input
        type="text"
        placeholder="Product Name"
        value={formData.productName}
        onChange={(e) => setFormData({ ...formData, productName: e.target.value })}
        className="w-full p-2 border rounded"
        required
      />
      <input
        type="number"
        placeholder="Cost Price"
        value={formData.costPrice}
        onChange={(e) => setFormData({ ...formData, costPrice: e.target.value })}
        className="w-full p-2 border rounded"
        step="0.01"
        required
      />
      <input
        type="number"
        placeholder="Quantity"
        value={formData.quantity}
        onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
        className="w-full p-2 border rounded"
        required
      />
      <input
        type="number"
        placeholder="Sell Price"
        value={formData.sellPrice}
        onChange={(e) => setFormData({ ...formData, sellPrice: e.target.value })}
        className="w-full p-2 border rounded"
        step="0.01"
        required
      />
      <button type="submit" className="w-full bg-blue-600 text-white p-3 rounded hover:bg-blue-700">
        Add Product
      </button>
    </form>
  );
};

export default AddProduct;