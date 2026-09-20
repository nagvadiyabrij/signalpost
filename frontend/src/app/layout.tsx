import type { Metadata } from "next";
import "./globals.css";
import AuthGate from "../components/AuthGate";

export const metadata: Metadata = {
  title: "Signalpost",
  description: "Verified Norwegian company information.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col"><AuthGate>{children}</AuthGate></body>
    </html>
  );
}
