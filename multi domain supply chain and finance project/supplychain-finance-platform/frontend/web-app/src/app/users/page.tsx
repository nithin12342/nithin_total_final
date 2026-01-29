import React from 'react';
import { User } from '../../types/users';

// This function runs on the server side to fetch data
async function getUsersData(): Promise<User[]> {
  // In a real application, this would fetch from your backend API
  // For demonstration, we're returning mock data
  return [
    { id: 1, name: 'John Smith', email: 'john.smith@company.com', role: 'Admin', status: 'Active', lastLogin: '2023-06-15T10:30:00Z' },
    { id: 2, name: 'Sarah Johnson', email: 'sarah.j@supplier.com', role: 'Supplier', status: 'Active', lastLogin: '2023-06-14T14:22:00Z' },
    { id: 3, name: 'Michael Chen', email: 'm.chen@finance.com', role: 'Financier', status: 'Active', lastLogin: '2023-06-13T09:15:00Z' },
    { id: 4, name: 'Emma Wilson', email: 'e.wilson@company.com', role: 'Admin', status: 'Inactive', lastLogin: '2023-05-22T16:45:00Z' },
    { id: 5, name: 'David Brown', email: 'd.brown@logistics.com', role: 'Supplier', status: 'Active', lastLogin: '2023-06-15T08:10:00Z' },
    { id: 6, name: 'Lisa Garcia', email: 'l.garcia@bank.com', role: 'Financier', status: 'Active', lastLogin: '2023-06-14T11:30:00Z' },
    { id: 7, name: 'Robert Taylor', email: 'r.taylor@manufacturer.com', role: 'Supplier', status: 'Pending', lastLogin: null },
    { id: 8, name: 'Jennifer Lee', email: 'j.lee@invest.com', role: 'Financier', status: 'Active', lastLogin: '2023-06-12T13:20:00Z' },
  ];
}

export default async function UsersPage() {
  const users = await getUsersData();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          <p className="mt-2 text-gray-600">Manage users and their permissions across the platform</p>
        </div>

        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-lg leading-6 font-medium text-gray-900">Users</h2>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                Add User
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th scope="col" className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-800 font-medium">{user.name.charAt(0)}</span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{user.name}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{user.role}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${user.status === 'Active' ? 'bg-green-100 text-green-800' : 
                          user.status === 'Inactive' ? 'bg-red-100 text-red-800' : 
                          'bg-yellow-100 text-yellow-800'}`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <a href="#" className="text-blue-600 hover:text-blue-900">Edit</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}