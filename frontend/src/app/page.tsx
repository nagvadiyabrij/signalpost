"use client";

import { useState } from "react";
import Link from "next/link";

export default function Home() {
  const [orgNumber, setOrgNumber] = useState("");

  const handleSearch = () => {
    if (orgNumber.trim()) {
      window.location.href = `/search?org=${orgNumber.trim()}`;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="text-2xl font-bold text-indigo-600">
                Signalpost
              </Link>
            </div>
            <div className="flex items-center space-x-8">
              <Link href="/" className="text-gray-700 hover:text-indigo-600">
                Home
              </Link>
              <Link href="/search" className="text-gray-700 hover:text-indigo-600">
                Search
              </Link>
              <Link href="/dashboard" className="text-gray-700 hover:text-indigo-600">
                Dashboard
              </Link>
              <Link href="/sources" className="text-gray-700 hover:text-indigo-600">
                Sources
              </Link>
              <Link href="/how-it-works" className="text-gray-700 hover:text-indigo-600">
                How It Works
              </Link>
              <Link href="/about" className="text-gray-700 hover:text-indigo-600">
                About
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Find verified information about Norwegian companies
          </h1>
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Enter a Norwegian organization number and discover public company information 
            with source-backed evidence. Every fact is linked to its source.
          </p>

          <div className="max-w-md mx-auto">
            <div className="flex gap-4">
              <input
                type="text"
                placeholder="Enter 9-digit organization number"
                value={orgNumber}
                onChange={(e) => setOrgNumber(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                maxLength={9}
              />
              <button
                onClick={handleSearch}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                Find Company
              </button>
            </div>
          </div>

          <div className="mt-12 bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Trust & Transparency
            </h3>
            <ul className="text-left text-gray-600 space-y-2">
              <li>✓ Every published fact is linked to its source</li>
              <li>✓ Company identity verification prevents wrong-company matches</li>
              <li>✓ Financial data includes currency, year, and source</li>
              <li>✓ Fresh information with retrieval timestamps</li>
              <li>✓ No fabricated data - unknown facts shown as unavailable</li>
            </ul>
          </div>
        </div>
      </main>

      <footer className="bg-white border-t mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-500">
            © 2026 Signalpost. Norwegian Company Information Research Tool.
          </p>
        </div>
      </footer>
    </div>
  );
}
