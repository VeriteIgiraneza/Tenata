const Products = ({ products, onUpdate }) => {
  const handleQuantityUpdate = async (index, newQuantity) => {
    if (newQuantity > products[index].quantity) {
      alert('Quantity left cannot be greater than initial quantity');
      return;
    }

    const response = await fetch('http://localhost:5000/api/update-quantity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        updates: [{ index, quantityLeft: newQuantity }]
      })
    });

    if (response.ok) {
      onUpdate();
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-center mb-6">Order Products</h2>
      {products.map((product, index) => (
        <div key={index} className="bg-white p-4 rounded-lg shadow">
          <div className="flex flex-col md:flex-row justify-between gap-4">
            <div className="flex-1">
              <p><strong>Product Name:</strong> {product.productName}</p>
              <p><strong>Cost Price:</strong> ${product.costPrice.toFixed(2)}</p>
              <p><strong>Sell Price:</strong> ${product.sellPrice.toFixed(2)}</p>
              <p><strong>Quantity in Store:</strong> {product.quantity}</p>
            </div>
            <div className="flex items-center space-x-2">
              <label className="whitespace-nowrap">Quantity Left:</label>
              <input
                type="number"
                value={product.quantityLeft}
                onChange={(e) => handleQuantityUpdate(index, parseInt(e.target.value))}
                className="w-24 p-2 border rounded"
                min="0"
                max={product.quantity}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Products;