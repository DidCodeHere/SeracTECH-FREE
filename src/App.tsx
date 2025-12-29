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
        <header className="bg-white shadow-sm border-b-4 border-orange-500">
          <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex items-center gap-4">
            <img 
              src={`${import.meta.env.BASE_URL}logo.png`}
              alt="SeracTECH-FREE Logo - Free UK Planning Application Search" 
              className="h-12 w-12 object-contain"
            />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">SeracTECH-FREE</h1>
              <p className="text-sm text-gray-500">Free UK Planning Applications & Construction Leads</p>
            </div>
          </div>
        </header>

        <main className="py-8">
          <div className="text-center mb-8 px-4">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Find UK Planning Applications
            </h2>
            <p className="mt-4 text-lg text-gray-500 max-w-2xl mx-auto">
              Search thousands of planning applications across England, Scotland, and Wales. 
              Generate construction leads for builders, contractors, and tradespeople — completely free.
            </p>
          </div>

          <Search onSearch={handleSearch} />
          
          <ResultsList postcode={postcode} radiusKm={radius} />
        </main>
        
        <footer className="bg-gray-800 text-white py-8 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-3 gap-8">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <img src={`${import.meta.env.BASE_URL}logo.png`} alt="SeracTECH-FREE" className="h-10 w-10" />
                  <span className="font-bold text-xl">SeracTECH-FREE</span>
                </div>
                <p className="text-gray-400 text-sm">
                  Free, open-source UK planning application search and construction lead generation platform.
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Features</h3>
                <ul className="text-gray-400 text-sm space-y-2">
                  <li>✓ UK-Wide Planning Search</li>
                  <li>✓ Interactive Map View</li>
                  <li>✓ CSV & PDF Export</li>
                  <li>✓ Radius-Based Filtering</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Links</h3>
                <ul className="text-gray-400 text-sm space-y-2">
                  <li>
                    <a href="https://github.com/DidCodeHere/SeracTECH-FREE" className="hover:text-orange-400 transition-colors" target="_blank" rel="noopener noreferrer">
                      GitHub Repository
                    </a>
                  </li>
                  <li>
                    <a href="https://github.com/DidCodeHere/SeracTECH-FREE/issues" className="hover:text-orange-400 transition-colors" target="_blank" rel="noopener noreferrer">
                      Report an Issue
                    </a>
                  </li>
                  <li>
                    <a href="https://github.com/DidCodeHere" className="hover:text-orange-400 transition-colors" target="_blank" rel="noopener noreferrer">
                      Made by DidCodeHere
                    </a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-700 mt-8 pt-6 text-center text-gray-400 text-sm">
              <p>© {new Date().getFullYear()} SeracTECH-FREE. Open source under MIT Licence. Made with ❤️ in the United Kingdom 🇬🇧</p>
            </div>
          </div>
        </footer>
        
        <Cart />
      </div>
    </QueryClientProvider>
  );
}

export default App;
