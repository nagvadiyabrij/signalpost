import Link from "next/link";

export default function HowItWorksPage() {
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
            How Signalpost Works
          </h1>

          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                1. Enter Organization Number
              </h2>
              <p className="text-gray-600">
                You enter a Norwegian organization number (9 digits). Our system validates the format 
                and ensures it's a proper Norwegian organization number.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                2. Company Identity Resolution
              </h2>
              <p className="text-gray-600">
                We query the official Norwegian company registry (Brønnøysundregistrene) to resolve 
                the company identity. This gives us the canonical company name, status, type, and 
                registration details.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                3. Multi-Source Research
              </h2>
              <p className="text-gray-600">
                We search multiple permitted public sources:
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
                <li>Official Norwegian government registries</li>
                <li>Company official websites</li>
                <li>Annual reports and investor relations</li>
                <li>Public financial information sources</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                4. Identity Verification
              </h2>
              <p className="text-gray-600">
                Before accepting any information, we verify it belongs to the correct company using:
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
                <li>Exact organization number match (primary identifier)</li>
                <li>Company name verification</li>
                <li>Address cross-referencing</li>
                <li>Domain validation</li>
              </ul>
              <p className="text-gray-600 mt-4">
                If information cannot be verified to belong to the requested company, it is rejected.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                5. Evidence Collection
              </h2>
              <p className="text-gray-600">
                Every factual value is linked to its source:
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
                <li>Source URL (the actual page where information was found)</li>
                <li>Source name (e.g., Brønnøysundregistrene)</li>
                <li>Retrieval date (when we fetched the information)</li>
                <li>Publication/update date (when available)</li>
              </ul>
              <p className="text-gray-600 mt-4">
                Financial data also includes currency and financial year.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                6. Fact Validation
              </h2>
              <p className="text-gray-600">
                We validate every fact before accepting it:
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
                <li>Source URL must be valid and accessible</li>
                <li>Financial facts must include currency and year</li>
                <li>Values must be parseable and reasonable</li>
                <li>Dates must be in valid format</li>
              </ul>
              <p className="text-gray-600 mt-4">
                If validation fails, the fact is rejected rather than guessed.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                7. Conflict Resolution
              </h2>
              <p className="text-gray-600">
                When sources disagree, we use a priority system:
              </p>
              <ol className="list-decimal list-inside text-gray-600 mt-2 space-y-1">
                <li>Official government registry (highest priority)</li>
                <li>Official company source</li>
                <li>Official annual report</li>
                <li>Reliable public financial source</li>
                <li>Other permitted public source</li>
              </ol>
              <p className="text-gray-600 mt-4">
                For current facts, we prefer newer information. For historical financial data, 
                we preserve the financial year distinction.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                8. Freshness
              </h2>
              <p className="text-gray-600">
                Information that changes frequently (status, address, management, board, website, employees) 
                is refreshed on each research run. Historical financial information preserves its financial year.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                9. No Fabrication
              </h2>
              <p className="text-gray-600">
                We never fabricate information. If a fact cannot be verified from a source, 
                it is shown as unavailable rather than guessed. Missing information is acceptable; 
                incorrect information is not.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                10. Result Display
              </h2>
              <p className="text-gray-600">
                The final company profile displays:
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
                <li>Company overview (name, status, type, registration)</li>
                <li>Address information</li>
                <li>Contact details (website, phone, email)</li>
                <li>Industry classification</li>
                <li>Financial information (with year and currency)</li>
                <li>People (board, management) when available</li>
                <li>Source list with URLs and retrieval dates</li>
              </ul>
              <p className="text-gray-600 mt-4">
                Every field includes a link to its source for verification.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
