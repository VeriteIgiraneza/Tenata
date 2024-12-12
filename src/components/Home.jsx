const Home = ({ products }) => {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-center mb-6">Added Products</h2>
      {products.map((product, index) => (
        <div key={index} className="bg-white p-4 rounded-lg shadow">
          <div className="flex flex-col md:flex-row justify-between gap-4">
            <div className="flex-1">
              <p><strong>Product Name:</strong> {product.productName}</p>
              <p><strong>Quantity in Store:</strong> {product.quantity}</p>
              <p><strong>Quantity Left:</strong> {product.quantityLeft}</p>
              <p><strong>Quantity Sold:</strong> {product.quantity - product.quantityLeft}</p>
            </div>
            <div className="text-right">
              <p><strong>Purchase Cost:</strong> ${product.costPrice.toFixed(2)}</p>
              <p><strong>Cost per Unit:</strong> ${(product.costPrice / product.quantity).toFixed(2)}</p>
              <p><strong>Selling Price:</strong> ${product.sellPrice.toFixed(2)}</p>
              <p><strong>Total Amount:</strong> ${(product.sellPrice * (product.quantity - product.quantityLeft)).toFixed(2)}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Home;