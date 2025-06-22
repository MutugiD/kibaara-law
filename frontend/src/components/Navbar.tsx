import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="bg-gray-800 text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-white hover:text-gray-300">
          Kibaara Law
        </Link>
        <div className="flex items-center space-x-6">
          <Link href="/" className="text-lg hover:text-gray-300">
            Portal
          </Link>
          <Link href="/upload" className="text-lg hover:text-gray-300">
            Upload
          </Link>
        </div>
      </div>
    </nav>
  );
}