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

  function updateField(field: "email" | "password", value: string) {
    if (field === "email") setEmail(value);
    else setPassword(value);
  }

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
      router.push(data.user.role === "ADMIN" ? "/admin" : "/");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to sign in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f4f7fb] px-4 py-8 lg:px-8">
      <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl overflow-hidden rounded-3xl bg-white shadow-2xl lg:grid-cols-[1.1fr_0.9fr]">
        <section className="relative hidden overflow-hidden bg-[#17243a] p-12 text-white lg:flex lg:flex-col lg:justify-between">
          <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full border-[40px] border-[#f1b24a]/30" />
          <div><div className="text-2xl font-bold text-[#f1b24a]">Signalpost</div><p className="mt-24 max-w-md text-5xl font-semibold leading-tight">Research with a clearer signal.</p><p className="mt-6 max-w-sm text-lg text-slate-300">Verified Norwegian company information, organized for decisions that need evidence.</p></div>
          <p className="text-sm text-slate-400">Registry-backed research workspace</p>
        </section>
        <section className="flex items-center p-8 sm:p-14">
          <div className="w-full max-w-md">
            <Link href="/" className="text-2xl font-bold text-[#17243a] lg:hidden">Signalpost</Link>
            <h1 className="mt-8 text-4xl font-semibold tracking-tight text-[#17243a]">Welcome back</h1>
            <p className="mt-3 text-gray-500">Sign in to open your research workspace.</p>
          <form noValidate onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-gray-700">
              Email
              <input type="email" value={email} onChange={(event) => updateField("email", event.target.value)} className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-[#4567d8] focus:ring-2 focus:ring-[#4567d8]/20" />
            </label>
            <label className="block text-sm font-medium text-gray-700">
              Password
              <input type="password" value={password} onChange={(event) => updateField("password", event.target.value)} className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-[#4567d8] focus:ring-2 focus:ring-[#4567d8]/20" />
            </label>
            {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            <button disabled={loading || !email || !password} className="w-full rounded-xl bg-[#4567d8] px-4 py-3 font-medium text-white transition hover:bg-[#3455c2] disabled:opacity-50">
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>
          <p className="mt-4 text-sm"><Link href="/forgot-password" className="font-medium text-[#4567d8]">Forgot password?</Link></p>
          <p className="mt-2 text-sm text-gray-600">New to Signalpost? <Link href="/register" className="font-medium text-[#4567d8]">Create an account</Link></p>
          </div>
        </section>
        </div>
    </main>
  );
}
