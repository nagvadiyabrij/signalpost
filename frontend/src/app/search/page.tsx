"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

interface CompanyData {
  organization_number: string;
  name: string;
  status: string;
  company_type: string;
  registration_date: string;
  business_address: string;
  postal_address: string;
  municipality: string;
  industry: string;
  industry_code: string;
}

interface Fact {
  field: string;
  value: string;
  source_url: string;
  source_name: string;
  retrieved_at: string;
  financial_year?: number;
  currency?: string;
  confidence: number;
}

interface Source {
  url: string;
  name: string;
  retrieved_at: string;
  http_status: number;
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const orgNumber = searchParams.get("org") || "";
  
  const [searchOrgNumber, setSearchOrgNumber] = useState(orgNumber);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [companyData, setCompanyData] = useState<CompanyData | null>(null);
  const [facts, setFacts] = useState<Fact[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [progress, setProgress] = useState<string[]>([]);

  useEffect(() => {
    if (orgNumber) {
      performSearch(orgNumber);
    }
  }, [orgNumber]);

  const performSearch = async (orgNum: string) => {
    setLoading(true);
    setError(null);
    setProgress(["Validating organization number...", "Searching public sources..."]);
    
    try {
      const response = await fetch("http://localhost:8000/api/company/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ organization_number: orgNum }),
      });

      setProgress(["Resolving company identity...", "Verifying sources...", "Extracting facts..."]);

      const data = await response.json();

      if (data.status === "error") {
        setError(data.message || "An error occurred");
        setProgress([]);
      } else if (data.status === "not_found") {
        setError("Company not found in registry");
        setProgress([]);
      } else {
        setCompanyData(data.company);
        setFacts(data.facts || []);
        setSources(data.sources || []);
        setWarnings(data.warnings || []);
        setProgress(["Company profile ready"]);
        
        // Redirect to company profile page
        setTimeout(() => {
          router.push(`/company/${orgNum}`);
        }, 1000);
      }
    } catch (err) {
      setError("Failed to connect to the server. Please ensure the backend is running.");
      setProgress([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchOrgNumber.trim()) {
      router.push(`/search?org=${searchOrgNumber.trim()}`);
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
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            Search Norwegian Companies
          </h1>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="flex gap-4">
              <input
                type="text"
                placeholder="Enter 9-digit organization number"
                value={searchOrgNumber}
                onChange={(e) => setSearchOrgNumber(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                maxLength={9}
              />
              <button
                onClick={handleSearch}
                disabled={loading}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50"
              >
                {loading ? "Searching..." : "Find Company"}
              </button>
            </div>
          </div>

          {loading && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Researching Company
              </h2>
              <div className="space-y-2">
                {progress.map((step, index) => (
                  <div key={index} className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-2">✓</span>
                    {step}
                  </div>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
              <h2 className="text-lg font-semibold text-red-900 mb-2">
                Error
              </h2>
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {warnings.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
              <h2 className="text-lg font-semibold text-yellow-900 mb-2">
                Warnings
              </h2>
              <ul className="list-disc list-inside text-yellow-700">
                {warnings.map((warning, index) => (
                  <li key={index}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
