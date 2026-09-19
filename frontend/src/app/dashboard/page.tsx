"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface DashboardStats {
  companies_researched: number;
  facts_verified: number;
  sources_collected: number;
  status: string;
}

interface BudgetUsage {
  requests_used: number;
  requests_remaining: number;
  usage_percentage: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [budget, setBudget] = useState<BudgetUsage | null>(null);
  const [loading, setLoading] = useState(true);
  const [systemHealth, setSystemHealth] = useState({
    registry: "Checking...",
    search: "Not configured",
    ai: "Not configured"
  });

  useEffect(() => {
    fetchStats();
    fetchBudget();
    checkSystemHealth();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchBudget = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/budget`);
      const data = await response.json();
      setBudget(data.budget);
    } catch (error) {
      console.error("Failed to fetch budget:", error);
    }
  };

  const checkSystemHealth = async () => {
    // Check registry health
    try {
      const response = await fetch("https://data.brreg.no/enhetsregisteret/api/");
      setSystemHealth(prev => ({ ...prev, registry: "Connected" }));
    } catch {
      setSystemHealth(prev => ({ ...prev, registry: "Disconnected" }));
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
              <Link href="/dashboard" className="text-gray-700 hover:text-indigo-600 font-medium">
                Dashboard
              </Link>
              <Link href="/history" className="text-gray-700 hover:text-indigo-600">
                History
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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          System Dashboard
        </h1>

        {/* System Health */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">System Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
              <div>
                <span className="font-medium text-gray-900">Registry Source</span>
                <div className="text-sm text-gray-600">Brønnøysundregistrene</div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                systemHealth.registry === "Connected" 
                  ? "bg-green-100 text-green-800" 
                  : "bg-red-100 text-red-800"
              }`}>
                {systemHealth.registry}
              </span>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
              <div>
                <span className="font-medium text-gray-900">Search Provider</span>
                <div className="text-sm text-gray-600">External API</div>
              </div>
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                {systemHealth.search}
              </span>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
              <div>
                <span className="font-medium text-gray-900">AI Provider</span>
                <div className="text-sm text-gray-600">LLM API</div>
              </div>
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                {systemHealth.ai}
              </span>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-2">Companies Researched</div>
            <div className="text-3xl font-bold text-gray-900">
              {loading ? "..." : stats?.companies_researched || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-2">Facts Verified</div>
            <div className="text-3xl font-bold text-gray-900">
              {loading ? "..." : stats?.facts_verified || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-2">Sources Collected</div>
            <div className="text-3xl font-bold text-gray-900">
              {loading ? "..." : stats?.sources_collected || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-2">System Status</div>
            <div className="text-3xl font-bold text-green-600">
              {loading ? "..." : stats?.status || "Unknown"}
            </div>
          </div>
        </div>

        {/* Request Budget */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Request Budget</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Requests Used</span>
                <span className="font-medium text-gray-900">
                  {budget ? `${budget.requests_used} / 1,800` : "Loading..."}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-indigo-600 h-2 rounded-full transition-all" 
                  style={{ width: budget ? `${budget.usage_percentage}%` : "0%" }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Estimated API Cost</span>
                <span className="font-medium text-gray-900">$0.00 / $10.00</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: "0%" }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Performance Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded">
              <div className="text-sm text-gray-600">Cache Hit Rate</div>
              <div className="text-lg font-medium text-gray-900">--</div>
            </div>
            <div className="p-4 bg-gray-50 rounded">
              <div className="text-sm text-gray-600">Average Response Time</div>
              <div className="text-lg font-medium text-gray-900">--</div>
            </div>
            <div className="p-4 bg-gray-50 rounded">
              <div className="text-sm text-gray-600">Facts Accepted</div>
              <div className="text-lg font-medium text-gray-900">--</div>
            </div>
            <div className="p-4 bg-gray-50 rounded">
              <div className="text-sm text-gray-600">Facts Rejected</div>
              <div className="text-lg font-medium text-gray-900">--</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
