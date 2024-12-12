import { useState, useEffect } from 'react';

const Statistics = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    const response = await fetch('http://localhost:5000/api/statistics', {
      credentials: 'include'
    });
    const data = await response.json();
    setStats(data);
  };

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-center mb-6">Statistics</h2>
      <div className="bg-white p-4 rounded-lg shadow">
        <p><strong>Total Products:</strong> {stats.totalProducts}</p>
        <p><strong>Total Quantity Sold:</strong> {stats.totalQuantitySold}</p>
        <p><strong>Total Amount:</strong> ${stats.totalAmount.toFixed(2)}</p>
        <p><strong>Total Profit:</strong> ${stats.totalProfit.toFixed(2)}</p>
      </div>
    </div>
  );
};

export default Statistics;