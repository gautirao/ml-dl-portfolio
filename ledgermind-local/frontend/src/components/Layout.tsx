import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Upload,
  Table,
  BarChart3,
  MessageSquare,
  ShieldCheck,
  Menu,
  X,
} from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const location = useLocation();

  const navigation = [
    { name: "Upload", href: "/", icon: Upload },
    { name: "Transactions", href: "/transactions", icon: Table },
    { name: "Analytics", href: "/analytics", icon: BarChart3 },
    { name: "Chat", href: "/chat", icon: MessageSquare },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Local Privacy Banner */}
      <div className="bg-indigo-600 text-white py-2 px-4 text-center text-sm font-medium flex items-center justify-center gap-2">
        <ShieldCheck size={16} />
        <span>
          LedgerMind Local: Your bank statements are processed locally. The LLM
          plans; deterministic tools calculate.
        </span>
      </div>

      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold text-indigo-700">
                  LedgerMind<span className="text-gray-900">Local</span>
                </span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                      isActive(item.href)
                        ? "border-indigo-500 text-gray-900"
                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                    }`}
                  >
                    <item.icon className="mr-2" size={18} />
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
            <div className="-mr-2 flex items-center sm:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
              >
                {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="sm:hidden">
            <div className="pt-2 pb-3 space-y-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setIsMenuOpen(false)}
                  className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                    isActive(item.href)
                      ? "bg-indigo-50 border-indigo-500 text-indigo-700"
                      : "border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700"
                  }`}
                >
                  <div className="flex items-center">
                    <item.icon className="mr-3" size={20} />
                    {item.name}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </nav>

      <main className="flex-grow">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">{children}</div>
      </main>

      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          &copy; 2026 LedgerMind Local - Built for Portfolio. Privacy-first
          finance analysis.
        </div>
      </footer>
    </div>
  );
};

export default Layout;
