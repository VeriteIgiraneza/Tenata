const AddQuantity = ({ products, onUpdate }) => {
  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const updates = [];

    for (const [key, value] of formData.entries()) {
      if (value > 0) {
        const index = key.split('-')[1];
        const currentProduct = products[index];
        const newQuantity = currentProduct.quantityLeft + parseInt(value);

        if (newQuantity <= currentProduct.quantity) {
          updates.push({
            index: parseInt(index),
            quantityLeft: newQuantity
          });
        }
      }
    }

    if (updates.length > 0) {
      const response = await fetch('http://localhost:5000/api/update-quantity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ updates })
      });

      if (response.ok) {
        onUpdate();
        e.target.reset();
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center mb-6">Add Quantity</h2>
      {products.map((product, index) => (
        <div key={index} className="bg-white p-4 rounded-lg shadow">
          <div className="flex flex-col md:flex-row justify-between gap-4">
            <div className="flex-1">
              <p><strong>Product Name:</strong> {product.productName}</p>
              <p><strong>Current Quantity:</strong> {product.quantityLeft}</p>
              <p><strong>Maximum Quantity:</strong> {product.quantity}</p>
            </div>
            <div className="flex items-center space-x-2">
              <label className="whitespace-nowrap">Add Quantity:</label>
              <input
                type="number"
                name={`quantity-${index}`}
                className="w-24 p-2 border rounded"
                min="0"
                max={product.quantity - product.quantityLeft}
                defaultValue="0"
              />
            </div>
          </div>
        </div>
      ))}
      <button type="submit" className="w-full bg-blue-600 text-white p-3 rounded hover:bg-blue-700">
        Update Quantities
      </button>
    </form>
  );
};

export default AddQuantity;