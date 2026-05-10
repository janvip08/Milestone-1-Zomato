'use client'

export function Sidebar() {
  return (
    <aside className="w-64 bg-white shadow-sm border-r h-screen">
      <div className="p-4">
        <nav className="space-y-2">
          <div className="space-y-1">
            <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Main
            </h3>
            <a href="/dashboard" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
              Dashboard
            </a>
            <a href="/recommendations" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
              Recommendations
            </a>
            <a href="/profile" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
              Profile
            </a>
          </div>
          
          <div className="space-y-1 pt-4">
            <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Advanced
            </h3>
            <a href="/experiments" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
              A/B Testing
            </a>
            <a href="/analytics" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
              Analytics
            </a>
            <a href="/vector-search" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
              Vector Search
            </a>
          </div>
        </nav>
      </div>
    </aside>
  )
}
