import React from 'react';
import './globals.css';

export const metadata = {
  title: 'Supply Chain Finance Platform',
  description: 'Enterprise-grade supply chain finance platform with advanced features',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}