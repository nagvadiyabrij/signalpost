"use client";

import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

const PUBLIC_PATHS = ["/login", "/register", "/forgot-password"];

function destinationForRole() {
  try {
    const user = JSON.parse(localStorage.getItem("signalpost_user") || "null");
    return user?.role === "ADMIN" ? "/admin" : "/";
  } catch {
    return "/dashboard";
  }
}

export default function AuthGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("signalpost_access_token");
    const isPublic = PUBLIC_PATHS.includes(pathname);
    const user = (() => {
      try {
        return JSON.parse(localStorage.getItem("signalpost_user") || "null");
      } catch {
        return null;
      }
    })();

    if (!token && !isPublic) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
      return;
    }
    if (token && pathname === "/login") {
      router.replace(destinationForRole());
      return;
    }
    if (token && pathname === "/admin" && user?.role !== "ADMIN") {
      router.replace("/dashboard");
      return;
    }
    const timer = window.setTimeout(() => setReady(true), 0);
    return () => window.clearTimeout(timer);
  }, [pathname, router]);

  if (!ready) {
    return <div className="min-h-screen bg-[#f4f7fb]" />;
  }
  return children;
}
