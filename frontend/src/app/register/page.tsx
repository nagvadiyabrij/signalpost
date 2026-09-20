"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm_password: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function updateField(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const responseText = await response.text();
      let data: { detail?: string; message?: string; access_token?: string; user?: unknown };
      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error(`Server returned an invalid response (${response.status})`);
      }
      if (!response.ok) {
        throw new Error(data.detail || data.message || "Unable to create account");
      }
      if (!data.access_token || !data.user) throw new Error("Server returned an incomplete registration response");
      localStorage.setItem("signalpost_access_token", data.access_token);
      localStorage.setItem("signalpost_user", JSON.stringify(data.user));
      router.push("/");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to create account");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-16">
      <div className="mx-auto max-w-md">
        <Link href="/" className="text-2xl font-bold text-indigo-600">Signalpost</Link>
        <div className="mt-8 rounded-lg bg-white p-8 shadow-md">
          <h1 className="text-3xl font-bold text-gray-900">Create account</h1>
          <p className="mt-2 text-gray-600">Save companies and review your research history.</p>
          <form noValidate onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-gray-700">
              Name
              <input required value={form.name} onChange={(event) => updateField("name", event.target.value)} className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3" />
            </label>
            <label className="block text-sm font-medium text-gray-700">
              Email
              <input required type="email" value={form.email} onChange={(event) => updateField("email", event.target.value)} className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3" />
            </label>
            <label className="block text-sm font-medium text-gray-700">
              Password
              <input required type="password" minLength={8} value={form.password} onChange={(event) => updateField("password", event.target.value)} className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3" />
            </label>
            <label className="block text-sm font-medium text-gray-700">
              Confirm password
              <input required type="password" minLength={8} value={form.confirm_password} onChange={(event) => updateField("confirm_password", event.target.value)} className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3" />
            </label>
            {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            <button disabled={loading} className="w-full rounded-lg bg-indigo-600 px-4 py-3 font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
              {loading ? "Creating account..." : "Create account"}
            </button>
          </form>
          <p className="mt-6 text-sm text-gray-600">Already registered? <Link href="/login" className="font-medium text-indigo-600">Sign in</Link></p>
        </div>
      </div>
    </main>
  );
}
