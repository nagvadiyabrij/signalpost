"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Company {
  organization_number: string;
  name: string;
  status: string | null;
  company_type: string | null;
  municipality: string | null;
  industry: string | null;
  industry_code: string | null;
}

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      async function loadCompanies() {
        setLoading(true);
        setError(null);
        try {
          const query = search ? `?search=${encodeURIComponent(search)}&limit=100` : "?limit=100";
          const response = await fetch(`${API_URL}/api/companies${query}`);
          const data = await response.json();
          if (!response.ok) throw new Error(data.detail || "Unable to load companies");
          setCompanies(data.companies || []);
          setTotal(data.total || 0);
        } catch (loadError) {
          setError(loadError instanceof Error ? loadError.message : "Unable to load companies");
        } finally {
          setLoading(false);
        }
      }
      void loadCompanies();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [search]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-10">
      <div className="mx-auto max-w-7xl">
        <nav className="flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-bold text-indigo-600">Signalpost</Link>
          <div className="flex flex-wrap gap-4 text-sm text-gray-700">
            <Link href="/search" className="hover:text-indigo-600">Search</Link>
            <Link href="/companies" className="font-medium text-indigo-600">Companies</Link>
            <Link href="/login" className="hover:text-indigo-600">Login</Link>
          </div>
        </nav>

        <div className="mt-12 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-indigo-600">Starter-kit registry data</p>
            <h1 className="mt-2 text-4xl font-bold text-gray-900">Company directory</h1>
            <p className="mt-2 text-gray-600">Browse the first 100 imported Norwegian company profiles.</p>
          </div>
          <label className="w-full md:w-80">
            <span className="sr-only">Search companies</span>
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name or organization number" className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3" />
          </label>
        </div>

        {error && <div className="mt-8 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
        <div className="mt-8 overflow-hidden rounded-lg bg-white shadow-md">
          <div className="border-b px-6 py-4 text-sm text-gray-600">Showing {companies.length} of {total} companies</div>
          {loading ? <p className="p-8 text-gray-600">Loading companies...</p> : companies.length === 0 ? <p className="p-8 text-gray-600">No companies match your search.</p> : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500"><tr><th className="px-6 py-3">Company</th><th className="px-6 py-3">Organization</th><th className="px-6 py-3">Type</th><th className="px-6 py-3">Municipality</th><th className="px-6 py-3">Industry</th><th className="px-6 py-3">Action</th></tr></thead>
                <tbody className="divide-y">{companies.map((company) => <tr key={company.organization_number} className="hover:bg-indigo-50"><td className="px-6 py-4 font-medium text-gray-900">{company.name}</td><td className="px-6 py-4 text-gray-600">{company.organization_number}</td><td className="px-6 py-4 text-gray-600">{company.company_type || "Unavailable"}</td><td className="px-6 py-4 text-gray-600">{company.municipality || "Unavailable"}</td><td className="max-w-xs px-6 py-4 text-gray-600">{company.industry || "Unavailable"}</td><td className="px-6 py-4"><Link href={`/company/${company.organization_number}`} className="font-medium text-indigo-600 hover:text-indigo-800">View</Link></td></tr>)}</tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
