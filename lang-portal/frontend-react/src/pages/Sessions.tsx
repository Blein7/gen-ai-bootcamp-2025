import { useState, useEffect } from 'react'
import StudySessionsTable from '../components/StudySessionsTable'
import { type StudySession, fetchStudySessions } from '../services/api'

// Writing Practice activity ID is typically 2
const WRITING_PRACTICE_ACTIVITY_ID = 2;

export default function Sessions() {
  const [sessions, setSessions] = useState<StudySession[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filterByWritingPractice, setFilterByWritingPractice] = useState(true)
  const itemsPerPage = 10

  const loadSessions = async () => {
    try {
      setLoading(true)
      
      // If filter is enabled, pass the Writing Practice activity ID
      const activityId = filterByWritingPractice ? WRITING_PRACTICE_ACTIVITY_ID : undefined;
      
      const response = await fetchStudySessions(currentPage, itemsPerPage, activityId)
      setSessions(response.items)
      setTotalPages(response.total_pages)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSessions()
  }, [currentPage, filterByWritingPractice])

  const handleRefresh = async () => {
    await loadSessions()
  }

  const toggleFilter = () => {
    setFilterByWritingPractice(!filterByWritingPractice)
    setCurrentPage(1) // Reset to first page when changing filter
  }

  if (loading) {
    return <div className="text-center py-4">Loading...</div>
  }

  if (error) {
    return <div className="text-red-500 text-center py-4">{error}</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Study Sessions</h1>
        
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={filterByWritingPractice}
              onChange={toggleFilter}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span>Show only Writing Practice sessions</span>
          </label>
          
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Refresh
          </button>
        </div>
      </div>

      {sessions.length > 0 ? (
        <StudySessionsTable 
          sessions={sessions} 
          onRefresh={handleRefresh}
        />
      ) : (
        <div className="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-gray-600 dark:text-gray-300">
            {filterByWritingPractice 
              ? "No Writing Practice sessions found. Try disabling the filter or create a new session."
              : "No study sessions found."}
          </p>
        </div>
      )}

      {totalPages > 1 && (
        <div className="mt-8 flex justify-center">
          <nav className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-600 dark:text-gray-300">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              Next
            </button>
          </nav>
        </div>
      )}
    </div>
  )
}