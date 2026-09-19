"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
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
  website: string;
  phone: string;
  email: string;
  description: string;
  parent_company: string;
  last_verified_at: string;
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

export default function CompanyProfilePage() {
  const params = useParams();
  const router = useRouter();
  const organizationNumber = params.organizationNumber as string;
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [companyData, setCompanyData] = useState<CompanyData | null>(null);
  const [facts, setFacts] = useState<Fact[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [selectedSource, setSelectedSource] = useState<Source | null>(null);

  useEffect(() => {
    fetchCompanyData();
  }, [organizationNumber]);

  const fetchCompanyData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/company/${organizationNumber}`);
      
      if (response.status === 404) {
        setError("Company not found. Please search for the company first.");
        setLoading(false);
        return;
      }

      const data = await response.json();
      
      if (data.status === "success") {
        setCompanyData(data.company);
        setFacts(data.facts || []);
        setSources(data.sources || []);
      } else {
        setError("Failed to load company data");
      }
    } catch (err) {
      setError("Failed to connect to the server. Please ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchCompanyData();
  };

  const getFactValue = (fieldName: string) => {
    const fact = facts.find(f => f.field === fieldName);
    return fact ? fact.value : null;
  };

  const getFactWithSource = (fieldName: string) => {
    return facts.find(f => f.field === fieldName);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
  };

  const formatCurrency = (value: string, currency?: string) => {
    if (!value) return "N/A";
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return value;
    return new Intl.NumberFormat("no-NO", {
      style: "currency",
      currency: currency || "NOK"
    }).format(numValue);
  };

  if (loading) {
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
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            <p className="mt-4 text-gray-600">Loading company profile...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error || !companyData) {
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
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="max-w-2xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-red-900 mb-2">
                Error
              </h2>
              <p className="text-red-700 mb-4">{error || "Company not found"}</p>
              <Link
                href="/search"
                className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Search for Company
              </Link>
            </div>
          </div>
        </main>
      </div>
    );
  }

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
        <div className="mb-6">
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Refresh Research
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {companyData.name}
              </h1>
              <p className="text-gray-600">
                Organization number: {companyData.organization_number}
              </p>
            </div>
            <div className="flex items-center">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                companyData.status === "Active" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
              }`}>
                <span className="w-2 h-2 mr-2 rounded-full bg-current"></span>
                {companyData.status}
              </span>
            </div>
          </div>

          <p className="text-sm text-gray-500">
            Last verified: {formatDate(companyData.last_verified_at)}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Overview</h2>
            <div className="space-y-3">
              <InfoRow
                label="Company Type"
                value={companyData.company_type}
                fact={getFactWithSource("company_type")}
                onViewSource={setSelectedSource}
              />
              <InfoRow
                label="Registration Date"
                value={formatDate(companyData.registration_date)}
                fact={getFactWithSource("registration_date")}
                onViewSource={setSelectedSource}
              />
              <InfoRow
                label="Industry"
                value={companyData.industry}
                fact={getFactWithSource("industry")}
                onViewSource={setSelectedSource}
              />
              <InfoRow
                label="Industry Code"
                value={companyData.industry_code}
                fact={getFactWithSource("industry_code")}
                onViewSource={setSelectedSource}
              />
              <InfoRow
                label="Municipality"
                value={companyData.municipality}
                fact={getFactWithSource("municipality")}
                onViewSource={setSelectedSource}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Address</h2>
            <div className="space-y-3">
              <InfoRow
                label="Business Address"
                value={companyData.business_address}
                fact={getFactWithSource("business_address")}
                onViewSource={setSelectedSource}
              />
              <InfoRow
                label="Postal Address"
                value={companyData.postal_address}
                fact={getFactWithSource("postal_address")}
                onViewSource={setSelectedSource}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
          <div className="space-y-3">
            <InfoRow
              label="Website"
              value={companyData.website}
              fact={getFactWithSource("website")}
              onViewSource={setSelectedSource}
              isLink
            />
            <InfoRow
              label="Phone"
              value={companyData.phone}
              fact={getFactWithSource("phone")}
              onViewSource={setSelectedSource}
            />
            <InfoRow
              label="Email"
              value={companyData.email}
              fact={getFactWithSource("email")}
              onViewSource={setSelectedSource}
              isLink
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Financial Information</h2>
          <div className="space-y-3">
            <FinancialInfoRow
              label="Revenue"
              value={getFactValue("revenue")}
              fact={getFactWithSource("revenue")}
              onViewSource={setSelectedSource}
            />
            <FinancialInfoRow
              label="Operating Profit"
              value={getFactValue("operating_profit")}
              fact={getFactWithSource("operating_profit")}
              onViewSource={setSelectedSource}
            />
            <FinancialInfoRow
              label="Profit Before Tax"
              value={getFactValue("profit_before_tax")}
              fact={getFactWithSource("profit_before_tax")}
              onViewSource={setSelectedSource}
            />
            <FinancialInfoRow
              label="Net Income"
              value={getFactValue("net_income")}
              fact={getFactWithSource("net_income")}
              onViewSource={setSelectedSource}
            />
            <FinancialInfoRow
              label="Total Assets"
              value={getFactValue("total_assets")}
              fact={getFactWithSource("total_assets")}
              onViewSource={setSelectedSource}
            />
            <FinancialInfoRow
              label="Equity"
              value={getFactValue("equity")}
              fact={getFactWithSource("equity")}
              onViewSource={setSelectedSource}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Sources</h2>
          <div className="space-y-2">
            {sources.map((source, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <span className="font-medium text-gray-900">{source.name}</span>
                  <span className="text-sm text-gray-500 ml-2">
                    Retrieved: {formatDate(source.retrieved_at)}
                  </span>
                </div>
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                >
                  View Source
                </a>
              </div>
            ))}
          </div>
        </div>
      </main>

      {selectedSource && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Source Details</h3>
              <button
                onClick={() => setSelectedSource(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <span className="font-medium text-gray-700">Source:</span>
                <span className="ml-2 text-gray-900">{selectedSource.name}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">URL:</span>
                <a
                  href={selectedSource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-2 text-indigo-600 hover:text-indigo-800 break-all"
                >
                  {selectedSource.url}
                </a>
              </div>
              <div>
                <span className="font-medium text-gray-700">Retrieved:</span>
                <span className="ml-2 text-gray-900">{formatDate(selectedSource.retrieved_at)}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">HTTP Status:</span>
                <span className="ml-2 text-gray-900">{selectedSource.http_status}</span>
              </div>
            </div>
            <div className="mt-6">
              <a
                href={selectedSource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Open Source
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function InfoRow({ label, value, fact, onViewSource, isLink = false }: {
  label: string;
  value: string | null;
  fact: Fact | undefined;
  onViewSource: (source: Source) => void;
  isLink?: boolean;
}) {
  if (!value) return null;

  const displayValue = isLink ? (
    <a href={value} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800">
      {value}
    </a>
  ) : (
    value
  );

  return (
    <div className="flex justify-between items-start">
      <span className="text-gray-600 font-medium">{label}:</span>
      <div className="text-right flex-1 ml-4">
        <div className="text-gray-900">{displayValue}</div>
        {fact && (
          <button
            onClick={() => onViewSource({
              url: fact.source_url,
              name: fact.source_name,
              retrieved_at: fact.retrieved_at,
              http_status: 200
            })}
            className="text-xs text-indigo-600 hover:text-indigo-800 mt-1"
          >
            Source: {fact.source_name} ({formatDate(fact.retrieved_at)})
          </button>
        )}
      </div>
    </div>
  );
}

function FinancialInfoRow({ label, value, fact, onViewSource }: {
  label: string;
  value: string | null;
  fact: Fact | undefined;
  onViewSource: (source: Source) => void;
}) {
  if (!value) return null;

  const financialYear = fact?.financial_year;
  const currency = fact?.currency;

  return (
    <div className="flex justify-between items-start">
      <span className="text-gray-600 font-medium">{label}:</span>
      <div className="text-right flex-1 ml-4">
        <div className="text-gray-900">{value}</div>
        {financialYear && (
          <div className="text-sm text-gray-500">Financial year: {financialYear}</div>
        )}
        {currency && (
          <div className="text-sm text-gray-500">Currency: {currency}</div>
        )}
        {fact && (
          <button
            onClick={() => onViewSource({
              url: fact.source_url,
              name: fact.source_name,
              retrieved_at: fact.retrieved_at,
              http_status: 200
            })}
            className="text-xs text-indigo-600 hover:text-indigo-800 mt-1"
          >
            Source: {fact.source_name} ({formatDate(fact.retrieved_at)})
          </button>
        )}
      </div>
    </div>
  );
}
