import Link from "next/link";

export default function AboutPage() {
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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            About Signalpost
          </h1>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Mission
            </h2>
            <p className="text-gray-600">
              Signalpost is a research tool for Norwegian company information. Our mission is to provide 
              verified, source-backed company information while maintaining the highest standards of 
              accuracy and transparency.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Core Principles
            </h2>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>
                <strong>Correctness First:</strong> We prioritize accuracy over coverage. 
                A missing fact is better than a wrong fact.
              </li>
              <li>
                <strong>Evidence Required:</strong> Every factual claim must be backed by a source 
                with a URL and date.
              </li>
              <li>
                <strong>No Fabrication:</strong> We never invent information. If something cannot 
                be verified, it&apos;s shown as unavailable.
              </li>
              <li>
                <strong>Identity Verification:</strong> We rigorously verify that information 
                belongs to the correct company using organization numbers, not just names.
              </li>
              <li>
                <strong>Transparency:</strong> Users can trace every fact back to its source.
              </li>
              <li>
                <strong>Freshness:</strong> We provide retrieval dates and prefer newer sources 
                for current information.
              </li>
            </ul>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Technology Stack
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Frontend</h3>
                <ul className="list-disc list-inside text-gray-600">
                  <li>Next.js 15</li>
                  <li>React</li>
                  <li>TypeScript</li>
                  <li>Tailwind CSS</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Backend</h3>
                <ul className="list-disc list-inside text-gray-600">
                  <li>FastAPI</li>
                  <li>Python</li>
                  <li>SQLAlchemy</li>
                  <li>SQLite/PostgreSQL</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Data Sources
            </h2>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>
                <strong>Brønnøysundregistrene:</strong> The official Norwegian Register of Business 
                Enterprises - our primary source for company identity and registration information.
              </li>
              <li>
                <strong>Company Websites:</strong> Official company websites for contact information 
                and company descriptions.
              </li>
              <li>
                <strong>Annual Reports:</strong> Official annual reports for financial information.
              </li>
              <li>
                <strong>Public Financial Sources:</strong> Permitted public sources containing 
                financial information where legally and technically accessible.
              </li>
            </ul>
            <p className="text-gray-600 mt-4">
              We respect all robots.txt restrictions, CAPTCHAs, login requirements, and paywalls. 
              We only use information that is publicly accessible without authentication.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Request Limits & Cost
            </h2>
            <p className="text-gray-600 mb-4">
              The system is designed to operate within these limits:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>Maximum 2,000 outbound requests per research session</li>
              <li>Maximum 45 minutes execution time</li>
              <li>Maximum $10 declared external API costs</li>
            </ul>
            <p className="text-gray-600 mt-4">
              We implement caching, request deduplication, and source prioritization to stay 
              comfortably below these limits.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Challenge Submission
            </h2>
            <p className="text-gray-600">
              This project is built for the Signalpost challenge, which requires building an agent 
              that finds Norwegian company information with strict requirements for correctness, 
              evidence, and transparency.
            </p>
            <p className="text-gray-600 mt-4">
              The submission includes at least 1,000 verified company profiles, each with source-backed 
              evidence for every factual claim.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
