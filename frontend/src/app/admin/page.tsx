"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface AdminStats {
  total_users: number;
  active_users: number;
  total_companies: number;
  verified_facts: number;
  total_sources: number;
  searches_today: number;
  api_requests: number;
  estimated_cost: number;
}

interface AdminUser {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
}

interface AdminCompany {
  id: number;
  organization_number: string;
  name: string;
  status: string | null;
  company_type: string | null;
}

interface AdminFact {
  id: number;
  field: string;
  value: string | null;
  source_name: string;
  verified: boolean;
}

interface AdminSource {
  id: number;
  name: string;
  url: string;
  http_status: number | null;
}

interface AdminSearch {
  id: string;
  organization_number: string;
  company_name: string | null;
  status: string;
  searched_at: string | null;
}

interface AdminAuditLog {
  id: string;
  action: string;
  target_type: string;
  created_at: string | null;
}

export default function AdminPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [companies, setCompanies] = useState<AdminCompany[]>([]);
  const [facts, setFacts] = useState<AdminFact[]>([]);
  const [sources, setSources] = useState<AdminSource[]>([]);
  const [searches, setSearches] = useState<AdminSearch[]>([]);
  const [auditLogs, setAuditLogs] = useState<AdminAuditLog[]>([]);
  const [system, setSystem] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAdminData() {
      const token = localStorage.getItem("signalpost_access_token");
      if (!token) {
        setError("Please sign in with an administrator account.");
        setLoading(false);
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };
      try {
        const endpoints = ["stats", "users", "companies", "facts?verified_only=true", "sources", "searches", "audit-logs", "system"];
        const responses = await Promise.all(endpoints.map((endpoint) => fetch(`${API_URL}/api/admin/${endpoint}`, { headers })));
        const failedResponse = responses.find((response) => !response.ok);
        if (failedResponse) {
          throw new Error(failedResponse.status === 403 ? "Admin access required." : "Unable to load admin data.");
        }
        const [statsData, usersData, companiesData, factsData, sourcesData, searchesData, auditData, systemData] = await Promise.all(responses.map((response) => response.json()));
        setStats(statsData);
        setUsers(usersData);
        setCompanies(companiesData);
        setFacts(factsData);
        setSources(sourcesData);
        setSearches(searchesData.searches || []);
        setAuditLogs(auditData.logs || []);
        setSystem(systemData);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unable to load admin data.");
      } finally {
        setLoading(false);
      }
    }

    void loadAdminData();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-10">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between">
          <div>
            <Link href="/" className="text-2xl font-bold text-indigo-600">Signalpost</Link>
            <h1 className="mt-6 text-3xl font-bold text-gray-900">Admin dashboard</h1>
          </div>
          <Link href="/dashboard" className="text-indigo-600 hover:text-indigo-800">User dashboard</Link>
        </div>

        {loading && <p className="mt-10 text-gray-600">Loading admin data...</p>}
        {error && <div className="mt-10 rounded-lg border border-red-200 bg-red-50 p-6 text-red-700">{error}</div>}

        {stats && (
          <>
            <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
              {[
                ["Users", stats.total_users],
                ["Companies", stats.total_companies],
                ["Verified facts", stats.verified_facts],
                ["Sources", stats.total_sources],
              ].map(([label, value]) => (
                <div key={label} className="rounded-lg bg-white p-5 shadow-md">
                  <p className="text-sm text-gray-600">{label}</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
                </div>
              ))}
            </div>
            <div className="mt-8 rounded-lg bg-white p-6 shadow-md">
              <h2 className="text-xl font-semibold text-gray-900">Registered users</h2>
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="border-b text-gray-500"><tr><th className="px-3 py-2">Name</th><th className="px-3 py-2">Email</th><th className="px-3 py-2">Role</th><th className="px-3 py-2">Status</th></tr></thead>
                  <tbody className="divide-y">{users.map((user) => <tr key={user.id}><td className="px-3 py-3">{user.name}</td><td className="px-3 py-3">{user.email}</td><td className="px-3 py-3">{user.role}</td><td className="px-3 py-3">{user.is_active ? "Active" : "Inactive"}</td></tr>)}</tbody>
                </table>
              </div>
            </div>
            <div className="mt-8 grid gap-8 lg:grid-cols-2">
              <DataSection title="Companies">
                <DataTable headers={["Organization", "Name", "Type", "Status"]} rows={companies.map((company) => [company.organization_number, company.name, company.company_type || "Unavailable", company.status || "Unavailable"])} />
              </DataSection>
              <DataSection title="Verified facts">
                <DataTable headers={["Field", "Value", "Source", "Verified"]} rows={facts.map((fact) => [fact.field, fact.value || "Unavailable", fact.source_name, fact.verified ? "Yes" : "No"])} />
              </DataSection>
              <DataSection title="Sources">
                <DataTable headers={["Name", "URL", "HTTP"]} rows={sources.map((source) => [source.name, source.url, String(source.http_status || "-")])} />
              </DataSection>
              <DataSection title="Search history">
                <DataTable headers={["Organization", "Company", "Status"]} rows={searches.map((search) => [search.organization_number, search.company_name || "Unknown", search.status])} />
              </DataSection>
              <DataSection title="Audit logs">
                <DataTable headers={["Action", "Target", "Created"]} rows={auditLogs.map((log) => [log.action, log.target_type, log.created_at ? new Date(log.created_at).toLocaleString() : "-"])} />
              </DataSection>
              <DataSection title="System health">
                <DataTable headers={["Service", "Status"]} rows={Object.entries(system || {}).filter(([key]) => key !== "budget").map(([key, value]) => [key, value])} />
              </DataSection>
            </div>
          </>
        )}
      </div>
    </main>
  );
}

function DataSection({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="rounded-lg bg-white p-6 shadow-md"><h2 className="text-xl font-semibold text-gray-900">{title}</h2><div className="mt-4">{children}</div></section>;
}

function DataTable({ headers, rows }: { headers: string[]; rows: string[][] }) {
  if (!rows.length) return <p className="text-sm text-gray-500">No records available.</p>;
  return <div className="overflow-x-auto"><table className="min-w-full text-left text-sm"><thead className="border-b text-gray-500"><tr>{headers.map((header) => <th key={header} className="px-3 py-2">{header}</th>)}</tr></thead><tbody className="divide-y">{rows.map((row, rowIndex) => <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={`${rowIndex}-${cellIndex}`} className="max-w-xs truncate px-3 py-3">{cell}</td>)}</tr>)}</tbody></table></div>;
}
