"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Unable to sign in");
      }
      localStorage.setItem("signalpost_access_token", data.access_token);
      localStorage.setItem("signalpost_user", JSON.stringify(data.user));
      router.push(data.user.role === "ADMIN" ? "/admin" : "/dashboard");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to sign in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-16">
      <div className="mx-auto max-w-md">
        <Link href="/" className="text-2xl font-bold text-indigo-600">Signalpost</Link>
        <div className="mt-8 rounded-lg bg-white p-8 shadow-md">
          <h1 className="text-3xl font-bold text-gray-900">Sign in</h1>
          <p className="mt-2 text-gray-600">Access your saved research and account.</p>
          <form noValidate onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-gray-700">
              Email
              <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3" />
            </label>
            <label className="block text-sm font-medium text-gray-700">
              Password
              <input required type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3" />
            </label>
            {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            <button disabled={loading} className="w-full rounded-lg bg-indigo-600 px-4 py-3 font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>
          <p className="mt-4 text-sm"><Link href="/forgot-password" className="font-medium text-indigo-600">Forgot password?</Link></p>
          <p className="mt-2 text-sm text-gray-600">New to Signalpost? <Link href="/register" className="font-medium text-indigo-600">Create an account</Link></p>
        </div>
      </div>
    </main>
  );
}
