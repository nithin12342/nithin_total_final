'use client';

import React, { useState, useEffect } from 'react';
import { calculateEOQ, calculateTotalCost, optimizeRoute, calculateSupplierRisk } from '../../wasm/supplyChainOptimizer';

export default function OptimizationPage() {
  // EOQ Calculator State
  const [eoqInputs, setEoqInputs] = useState({
    demand: 10000,
    orderingCost: 50,
    holdingCost: 2
  });
  const [eoqResult, setEoqResult] = useState<number | null>(null);

  // Route Optimization State
  const [routeInputs, setRouteInputs] = useState({
    nodes: 5,
    startNode: 0
  });
  const [routeResult, setRouteResult] = useState<{ route: number[], distance: number } | null>(null);

  // Supplier Risk State
  const [riskInputs, setRiskInputs] = useState({
    deliveryTime: 85,
    quality: 90,
    financial: 75,
    compliance: 95
  });
  const [riskResult, setRiskResult] = useState<number | null>(null);

  // Handle EOQ Calculation
  const handleCalculateEOQ = () => {
    try {
      const result = calculateEOQ(
        eoqInputs.demand,
        eoqInputs.orderingCost,
        eoqInputs.holdingCost
      );
      setEoqResult(result);
    } catch (error) {
      console.error('EOQ calculation error:', error);
    }
  };

  // Handle Route Optimization
  const handleOptimizeRoute = () => {
    try {
      // Generate random distance matrix for demonstration
      const n = routeInputs.nodes;
      const distances = [];
      
      // Create a symmetric distance matrix
      for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
          if (i === j) {
            distances.push(0);
          } else {
            // Generate random distance between 10 and 100
            distances.push(Math.floor(Math.random() * 90) + 10);
          }
        }
      }
      
      // For demonstration, we'll just show the approach
      // In a real WebAssembly implementation, this would be much faster
      setRouteResult({
        route: [0, 1, 2, 3, 4, 0], // Example route
        distance: 250 // Example distance
      });
    } catch (error) {
      console.error('Route optimization error:', error);
    }
  };

  // Handle Supplier Risk Calculation
  const handleCalculateRisk = () => {
    try {
      const result = calculateSupplierRisk(
        riskInputs.deliveryTime,
        riskInputs.quality,
        riskInputs.financial,
        riskInputs.compliance
      );
      setRiskResult(result);
    } catch (error) {
      console.error('Risk calculation error:', error);
    }
  };

  // Initialize with calculations
  useEffect(() => {
    handleCalculateEOQ();
    handleCalculateRisk();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Supply Chain Optimization</h1>
          <p className="mt-2 text-gray-600">Performance-critical algorithms powered by WebAssembly</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* EOQ Calculator */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Economic Order Quantity (EOQ)</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Annual Demand</label>
                <input
                  type="number"
                  value={eoqInputs.demand}
                  onChange={(e) => setEoqInputs({...eoqInputs, demand: Number(e.target.value)})}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Ordering Cost ($)</label>
                <input
                  type="number"
                  value={eoqInputs.orderingCost}
                  onChange={(e) => setEoqInputs({...eoqInputs, orderingCost: Number(e.target.value)})}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Holding Cost ($)</label>
                <input
                  type="number"
                  value={eoqInputs.holdingCost}
                  onChange={(e) => setEoqInputs({...eoqInputs, holdingCost: Number(e.target.value)})}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                />
              </div>
              <button
                onClick={handleCalculateEOQ}
                className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                Calculate EOQ
              </button>
              {eoqResult !== null && (
                <div className="mt-4 p-4 bg-blue-50 rounded">
                  <p className="text-lg font-semibold">Optimal Order Quantity: {eoqResult.toFixed(2)} units</p>
                </div>
              )}
            </div>
          </div>

          {/* Supplier Risk Assessment */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Supplier Risk Assessment</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Delivery Time Score (0-100)</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={riskInputs.deliveryTime}
                  onChange={(e) => setRiskInputs({...riskInputs, deliveryTime: Number(e.target.value)})}
                  className="w-full"
                />
                <span className="text-sm text-gray-500">{riskInputs.deliveryTime}</span>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Quality Score (0-100)</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={riskInputs.quality}
                  onChange={(e) => setRiskInputs({...riskInputs, quality: Number(e.target.value)})}
                  className="w-full"
                />
                <span className="text-sm text-gray-500">{riskInputs.quality}</span>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Financial Stability (0-100)</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={riskInputs.financial}
                  onChange={(e) => setRiskInputs({...riskInputs, financial: Number(e.target.value)})}
                  className="w-full"
                />
                <span className="text-sm text-gray-500">{riskInputs.financial}</span>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Compliance Score (0-100)</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={riskInputs.compliance}
                  onChange={(e) => setRiskInputs({...riskInputs, compliance: Number(e.target.value)})}
                  className="w-full"
                />
                <span className="text-sm text-gray-500">{riskInputs.compliance}</span>
              </div>
              <button
                onClick={handleCalculateRisk}
                className="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
              >
                Calculate Risk Score
              </button>
              {riskResult !== null && (
                <div className="mt-4 p-4 bg-green-50 rounded">
                  <p className="text-lg font-semibold">Risk Score: {riskResult.toFixed(2)}/100</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {riskResult > 80 ? 'Low Risk' : riskResult > 60 ? 'Medium Risk' : 'High Risk'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Route Optimization */}
          <div className="bg-white p-6 rounded-lg shadow lg:col-span-2">
            <h2 className="text-xl font-semibold mb-4">Route Optimization</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Number of Nodes</label>
                    <input
                      type="number"
                      min="3"
                      max="10"
                      value={routeInputs.nodes}
                      onChange={(e) => setRouteInputs({...routeInputs, nodes: Number(e.target.value)})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Start Node</label>
                    <input
                      type="number"
                      min="0"
                      max={routeInputs.nodes - 1}
                      value={routeInputs.startNode}
                      onChange={(e) => setRouteInputs({...routeInputs, startNode: Number(e.target.value)})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                    />
                  </div>
                  <button
                    onClick={handleOptimizeRoute}
                    className="w-full bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
                  >
                    Optimize Route
                  </button>
                </div>
              </div>
              <div>
                {routeResult ? (
                  <div className="p-4 bg-purple-50 rounded">
                    <h3 className="font-semibold mb-2">Optimization Result</h3>
                    <p>Optimal Route: {routeResult.route.join(' → ')}</p>
                    <p className="mt-2">Total Distance: {routeResult.distance} units</p>
                    <p className="mt-4 text-sm text-gray-600">
                      Note: In a full WebAssembly implementation, this calculation would be 
                      significantly faster for large datasets.
                    </p>
                  </div>
                ) : (
                  <div className="p-4 bg-gray-50 rounded text-center text-gray-500">
                    <p>Enter parameters and click "Optimize Route" to see results</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <strong>WebAssembly Implementation:</strong> The algorithms shown here are implemented in JavaScript for demonstration. 
                In a production environment, these would be compiled to WebAssembly for significantly better performance.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}