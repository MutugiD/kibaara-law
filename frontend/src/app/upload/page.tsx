'use client';

import { useState } from 'react';
import { DocumentType } from '../../../src/models/case_models';

const UploadPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<DocumentType>('case_law');
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      setFile(files[0]);
      setError('');
      setMessage('');
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    setIsUploading(true);
    setMessage('');
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);

    const apiUrl = 'http://localhost:8080/api/v1/cases/upload';

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        let errorMessage = 'An unknown error occurred.';
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            errorMessage = data.detail.map((d: any) => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join('; ');
          } else {
            errorMessage = data.detail;
          }
        }
        throw new Error(errorMessage);
      }

      setMessage(`File uploaded successfully: ${data.filename}`);
      setFile(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Upload Document</h1>
      <div className="max-w-2xl mx-auto">
        <form onSubmit={handleSubmit} className="p-6 bg-white rounded-lg shadow-md border border-gray-200 space-y-6">
          <div>
            <label htmlFor="document-type" className="block text-sm font-medium text-gray-700 mb-1">
              Document Type
            </label>
            <select
              id="document-type"
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value as DocumentType)}
              className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="case_law">Case Law</option>
              <option value="pleadings">Pleadings</option>
            </select>
          </div>

          <div>
            <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-1">
              Select PDF File
            </label>
            <input
              id="file-upload"
              type="file"
              onChange={handleFileChange}
              accept=".pdf"
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
             {file && <p className="text-sm text-gray-600 mt-2">Selected file: {file.name}</p>}
          </div>

          <button
            type="submit"
            disabled={isUploading || !file}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {isUploading ? 'Uploading...' : 'Upload Document'}
          </button>

          {message && <p className="mt-2 text-sm text-green-600">{message}</p>}
          {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        </form>

        <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Upload Instructions</h2>
          <ul className="list-disc list-inside text-gray-600 space-y-1">
              <li><span className="font-semibold">Case Law:</span> Upload the main case document. This should contain the ruling and, if available, the pleadings.</li>
              <li><span className="font-semibold">Pleadings:</span> If you have a separate document for pleadings, upload it here.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;