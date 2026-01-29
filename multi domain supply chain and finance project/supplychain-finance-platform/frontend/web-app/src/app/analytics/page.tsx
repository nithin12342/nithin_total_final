import React from 'react';
import { AnalyticsData, Transaction } from '../../types/analytics';

// This function runs on the server side to fetch data
async function getAnalyticsData(): Promise<AnalyticsData> {
  // In a real application, this would fetch from your backend API
  // For demonstration, we're returning mock data
  return {
    totalTransactions: 12450,
    totalValue: 28750000,
    activeSuppliers: 342,
    activeFinanciers: 87,
    pendingApprovals: 23,
    monthlyGrowth: 12.5,
    riskScore: 78,
    topProducts: [
      { name: 'Electronics', value: 5400000 },
      { name: 'Textiles', value: 3200000 },
      { name: 'Machinery', value: 2800000 },
      { name: 'Chemicals', value: 2100000 },
      { name: 'Food Products', value: 1800000 },
    ],
    recentTransactions: [
      { id: 1, supplier: 'TechCorp Ltd', financier: 'Global Finance', amount: 150000, status: 'Completed' },
      { id: 2, supplier: 'TextileHub Inc', financier: 'Capital Partners', amount: 85000, status: 'Processing' },
      { id: 3, supplier: 'Machinex GmbH', financier: 'Industrial Bank', amount: 320000, status: 'Approved' },
      { id: 4, supplier: 'ChemWorld Co', financier: 'InvestCorp', amount: 195000, status: 'Pending' },
      { id: 5, supplier: 'FoodProducers Ltd', financier: 'AgriFinance', amount: 75000, status: 'Completed' },
    ]
  };
}

export default async function AnalyticsPage() {
  const data = await getAnalyticsData();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="mt-2 text-gray-600">Comprehensive insights into your supply chain finance operations</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Total Transactions</h3>
            <p className="mt-2 text-3xl font-bold text-blue-600">{data.totalTransactions.toLocaleString()}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Transaction Value</h3>
            <p className="mt-2 text-3xl font-bold text-green-600">${(data.totalValue / 1000000).toFixed(2)}M</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Active Suppliers</h3>
            <p className="mt-2 text-3xl font-bold text-purple-600">{data.activeSuppliers}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Active Financiers</h3>
            <p className="mt-2 text-3xl font-bold text-yellow-600">{data.activeFinanciers}</p>
          </div>
        </div>

        {/* Charts and Visualizations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Top Products by Value</h3>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
              <p className="text-gray-500">Chart visualization would appear here</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Transactions</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Supplier</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Financier</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.recentTransactions.map((transaction: Transaction) => (
                    <tr key={transaction.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{transaction.supplier}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{transaction.financier}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${transaction.amount.toLocaleString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${transaction.status === 'Completed' ? 'bg-green-100 text-green-800' : 
                            transaction.status === 'Processing' ? 'bg-blue-100 text-blue-800' : 
                            transaction.status === 'Approved' ? 'bg-purple-100 text-purple-800' : 
                            'bg-yellow-100 text-yellow-800'}`}>
                          {transaction.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Pending Approvals</h3>
            <p className="mt-2 text-3xl font-bold text-red-600">{data.pendingApprovals}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Monthly Growth</h3>
            <p className="mt-2 text-3xl font-bold text-indigo-600">{data.monthlyGrowth}%</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Risk Score</h3>
            <p className="mt-2 text-3xl font-bold text-orange-600">{data.riskScore}/100</p>
          </div>
        </div>
      </div>
    </div>
  );
}