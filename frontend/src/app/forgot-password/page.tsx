"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const response = await fetch(`${API_URL}/api/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to request a reset");
      setMessage(data.message || "Check your email for reset instructions.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to request a reset");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-16">
      <div className="mx-auto max-w-md">
        <Link href="/" className="text-2xl font-bold text-indigo-600">Signalpost</Link>
        <div className="mt-8 rounded-lg bg-white p-8 shadow-md">
          <h1 className="text-3xl font-bold text-gray-900">Reset password</h1>
          <p className="mt-2 text-gray-600">Enter your email to request a password reset.</p>
          <form noValidate onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-gray-700">
              Email
              <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3" />
            </label>
            {message && <p className="rounded-lg bg-green-50 p-3 text-sm text-green-700">{message}</p>}
            {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            <button disabled={loading} className="w-full rounded-lg bg-indigo-600 px-4 py-3 font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
              {loading ? "Requesting reset..." : "Request reset"}
            </button>
          </form>
          <p className="mt-6 text-sm text-gray-600"><Link href="/login" className="font-medium text-indigo-600">Back to sign in</Link></p>
        </div>
      </div>
    </main>
  );
}
