import Link from "next/link";

export default function SourcesPage() {
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
            Data Sources
          </h1>

          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-2xl font-semibold text-gray-900">
                  Brønnøysundregistrene
                </h2>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  Primary
                </span>
              </div>
              <p className="text-gray-600 mb-4">
                The official Norwegian Register of Business Enterprises. This is our primary source 
                for company identity, registration information, and official company details.
              </p>
              <div className="space-y-2 text-sm text-gray-600">
                <div><strong>Priority:</strong> 1 (Highest)</div>
                <div><strong>Type:</strong> Official Government Registry</div>
                <div><strong>Cost:</strong> Free</div>
                <div><strong>API:</strong> https://data.brreg.no/enhetsregisteret/api/</div>
              </div>
              <div className="mt-4">
                <a
                  href="https://data.brreg.no/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                >
                  Visit Official Source →
                </a>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-2xl font-semibold text-gray-900">
                  Company Websites
                </h2>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  Secondary
                </span>
              </div>
              <p className="text-gray-600 mb-4">
                Official company websites provide contact information, company descriptions, 
                and sometimes additional details not available in official registries.
              </p>
              <div className="space-y-2 text-sm text-gray-600">
                <div><strong>Priority:</strong> 2</div>
                <div><strong>Type:</strong> Official Company Source</div>
                <div><strong>Cost:</strong> Free</div>
                <div><strong>Access:</strong> Public web scraping (robots.txt respected)</div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-2xl font-semibold text-gray-900">
                  Annual Reports
                </h2>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  Secondary
                </span>
              </div>
              <p className="text-gray-600 mb-4">
                Official annual reports provide detailed financial information including revenue, 
                profit, assets, and equity. These are authoritative sources for financial data.
              </p>
              <div className="space-y-2 text-sm text-gray-600">
                <div><strong>Priority:</strong> 3</div>
                <div><strong>Type:</strong> Official Company Document</div>
                <div><strong>Cost:</strong> Free</div>
                <div><strong>Access:</strong> Publicly available PDFs and web pages</div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-2xl font-semibold text-gray-900">
                  Public Financial Sources
                </h2>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                  Tertiary
                </span>
              </div>
              <p className="text-gray-600 mb-4">
                Permitted public sources containing financial information where legally and 
                technically accessible. Used only when official sources are unavailable.
              </p>
              <div className="space-y-2 text-sm text-gray-600">
                <div><strong>Priority:</strong> 4</div>
                <div><strong>Type:</strong> Public Financial Information</div>
                <div><strong>Cost:</strong> Free (where available)</div>
                <div><strong>Access:</strong> Public APIs and websites</div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Source Priority System
              </h2>
              <p className="text-gray-600 mb-4">
                When multiple sources provide conflicting information, we use this priority system:
              </p>
              <ol className="list-decimal list-inside space-y-2 text-gray-600">
                <li>Official government registry (Brønnøysundregistrene)</li>
                <li>Official company source (website, official documents)</li>
                <li>Official annual report</li>
                <li>Reliable public financial source</li>
                <li>Other permitted public source</li>
              </ol>
              <p className="text-gray-600 mt-4">
                For current facts (status, address, etc.), we prefer newer information. 
                For historical financial data, we preserve the financial year distinction.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Access Restrictions
              </h2>
              <p className="text-gray-600 mb-4">
                We respect all access restrictions and only use information that is:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-600">
                <li>Publicly accessible without authentication</li>
                <li>Not behind CAPTCHAs or login requirements</li>
                <li>Not behind paywalls</li>
                <li>Respectful of robots.txt restrictions</li>
                <li>Compliant with anti-bot protection systems</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
