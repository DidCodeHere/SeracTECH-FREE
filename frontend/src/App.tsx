import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Search } from './components/Search';
import { ResultsList } from './components/ResultsList';
import { Cart } from './components/Cart';

// Create a client
const queryClient = new QueryClient();

function App() {
  const [postcode, setPostcode] = useState('');
  const [radius, setRadius] = useState(5);

  const handleSearch = (newPostcode: string, newRadius: number) => {
    setPostcode(newPostcode);
    setRadius(newRadius);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50 pb-32">
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
            <h1 className="text-2xl font-bold text-gray-900">SeracTECH-FREE</h1>
            <p className="text-sm text-gray-500">Open Source Construction Leads</p>
          </div>
        </header>

        <main className="py-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Find Planning Applications
            </h2>
            <p className="mt-4 text-lg text-gray-500">
              Enter a postcode to see recent planning applications in your area.
            </p>
          </div>

          <Search onSearch={handleSearch} />
          
          <ResultsList postcode={postcode} radiusKm={radius} />
        </main>
        
        <Cart />
      </div>
    </QueryClientProvider>
  );
}

export default App;
