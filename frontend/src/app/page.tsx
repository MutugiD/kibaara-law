'use client';

import { useEffect, useState, useMemo } from 'react';

// Define a type for the case data
interface Case {
  id: number;
  filename: string;
  upload_date: string;
  status: string;
  document_type: string;
}

const CaseRow = ({
  caseData,
  onAnalyze,
  onDownload
}: {
  caseData: Case,
  onAnalyze: (filename: string) => void,
  onDownload: (filename: string) => void
}) => {
  const getStatusChip = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Completed</span>;
      case 'PROCESSING':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Processing</span>;
      case 'UPLOADED':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">Uploaded</span>;
      case 'FAILED':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Failed</span>;
      default:
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">{status}</span>;
    }
  };

  // Trim whitespace and compare against the exact, case-sensitive values from the backend
  const status = caseData.status.trim();
  const isAnalyzeDisabled = status !== 'Uploaded';
  const isDownloadDisabled = status !== 'Completed';
  const isProcessing = status === 'Processing';

  return (
    <tr className="bg-white hover:bg-gray-50">
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{caseData.filename}</td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(caseData.upload_date).toLocaleDateString()}</td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{getStatusChip(caseData.status)}</td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{caseData.document_type}</td>
      <td className="px-6 py-4 whitespace-nowrap text-left text-sm font-medium">
        <div className="flex justify-start items-center space-x-4">
          <button
            onClick={() => onAnalyze(caseData.filename)}
            className="px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-md hover:bg-indigo-100 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
            disabled={isAnalyzeDisabled || isProcessing}
          >
            {isProcessing ? 'Analyzing...' : 'Analyze Case'}
          </button>
          <button
            onClick={() => onDownload(caseData.filename)}
            className="px-4 py-2 text-sm font-medium text-green-600 bg-green-50 rounded-md hover:bg-green-100 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
            disabled={isDownloadDisabled}
          >
            Download Analysis
          </button>
        </div>
      </td>
    </tr>
  );
};

export default function PortalPage() {
  const [allCases, setAllCases] = useState<Case[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = 'http://localhost:8000';

  const fetchCases = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/cases/`);
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      const data = await response.json();
      setAllCases(data);
      setError(null); // Clear previous errors on successful fetch
    } catch (err: any) {
      setError(err.message); // Set error state
    } finally {
      setIsLoading(false); // Always stop loading after a fetch attempt
    }
  };

  // Fetch all cases on initial load and then poll for updates
  useEffect(() => {
    fetchCases(); // Initial fetch
    const interval = setInterval(fetchCases, 5000); // Poll for updates
    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  // Memoize filtered cases to avoid re-calculating on every render
  const filteredCases = useMemo(() => {
    if (!searchTerm) {
      return allCases;
    }
    const lowercasedSearchTerm = searchTerm.toLowerCase().trim();
    return allCases.filter(caseData =>
      caseData.filename.toLowerCase().replace(/\.pdf$/, '').includes(lowercasedSearchTerm)
    );
  }, [allCases, searchTerm]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleAnalyze = async (filename: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/cases/analyze/${filename}`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to start analysis.');
      }
      await fetchCases(); // Re-fetch immediately to get the latest status
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDownload = async (filename: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/cases/download/${filename}`);
      if (!response.ok) {
        throw new Error('Failed to download summary.');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${filename.split('.')[0]}_summary.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Case Portal</h1>

      <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
            <div className="md:col-span-2">
                <label htmlFor="search-filename" className="block text-sm font-medium text-gray-700 mb-1">
                    Search by Filename
                </label>
                <input
                  type="text"
                  id="search-filename"
                  placeholder="Enter all or part of the filename..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                />
            </div>
            <div>
                <label htmlFor="court-level" className="block text-sm font-medium text-gray-700 mb-1">Court Level</label>
                <select
                    id="court-level"
                    className="w-full p-2 border border-gray-300 rounded-md shadow-sm bg-gray-100 cursor-not-allowed"
                    disabled
                >
                    <option>Appellate</option>
                </select>
            </div>
        </div>
      </div>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
        <strong className="font-bold">Error:</strong>
        <span className="block sm:inline"> {error}</span>
      </div>}

      {isLoading && <p className="text-center py-4">Loading initial case data...</p>}

      {!isLoading && (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Filename</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Uploaded On</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredCases.length > 0 ? (
                  filteredCases.map(caseData => <CaseRow key={caseData.id} caseData={caseData} onAnalyze={handleAnalyze} onDownload={handleDownload}/>)
                ) : (
                  <tr>
                    <td colSpan={5} className="text-center py-4">
                      {searchTerm
                        ? "No matching cases found for your search."
                        : "No cases have been uploaded yet."
                      }
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
