import { useState, useEffect } from 'react';
import { Home as HomeIcon, Package, BarChart2, ShoppingCart, PlusCircle } from 'lucide-react';
import NavButton from './components/NavButton';
import Home from './components/Home';
import Products from './components/Products';
import Statistics from './components/Statistics';
import AddProduct from './components/AddProduct';
import AddQuantity from './components/AddQuantity';

const App = () => {
  const [view, setView] = useState('home');
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    const response = await fetch('http://localhost:5000/api/products', {
      credentials: 'include'
    });
    const data = await response.json();
    setProducts(data);
  };

  const renderView = () => {
    switch(view) {
      case 'home':
        return <Home products={products} />;
      case 'products':
        return <Products products={products} onUpdate={fetchProducts} />;
      case 'statistics':
        return <Statistics products={products} />;
      case 'add':
        return <AddProduct onAdd={fetchProducts} />;
      case 'quantity':
        return <AddQuantity products={products} onUpdate={fetchProducts} />;
      default:
        return <Home products={products} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <header className="fixed top-0 w-full bg-gray-800 text-white p-4 text-center z-50">
        <h1 className="text-xl font-bold">HARAKA</h1>
      </header>

      <main className="flex-grow mt-16 mb-20 p-4">
        {renderView()}
      </main>

      <nav className="fixed bottom-0 w-full bg-purple-100 bg-opacity-50 p-4 flex justify-center space-x-8">
        <NavButton icon={<HomeIcon size={24} />} label="Home" onClick={() => setView('home')} active={view === 'home'} />
        <NavButton icon={<Package size={24} />} label="Product" onClick={() => setView('products')} active={view === 'products'} />
        <NavButton icon={<BarChart2 size={24} />} label="Statistics" onClick={() => setView('statistics')} active={view === 'statistics'} />
        <NavButton icon={<ShoppingCart size={24} />} label="Add" onClick={() => setView('add')} active={view === 'add'} />
        <NavButton icon={<PlusCircle size={24} />} label="Quantity" onClick={() => setView('quantity')} active={view === 'quantity'} />
      </nav>
    </div>
  );
};

export default App;