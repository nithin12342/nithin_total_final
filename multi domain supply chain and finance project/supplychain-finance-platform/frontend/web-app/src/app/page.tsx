import React from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold mb-4">Supply Chain Finance Platform</h1>
      <p className="text-lg text-gray-700 mb-8">Server-Side Rendered Main Application</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
        <Link href="/analytics" className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-2">Analytics Dashboard</h2>
          <p className="text-gray-600">Comprehensive insights into supply chain finance operations.</p>
        </Link>
        <Link href="/users" className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-2">User Management</h2>
          <p className="text-gray-600">Manage users and their permissions across the platform.</p>
        </Link>
        <Link href="/optimization" className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-2">Optimization Tools</h2>
          <p className="text-gray-600">Performance-critical algorithms powered by WebAssembly.</p>
        </Link>
      </div>
    </div>
  );
}