import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Pagination from '@/components/Pagination'
import type { Word, StudySession } from '@/services/api'

interface SessionResponse {
  session: StudySession
  words: Word[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export default function StudySessionShow() {
  const { id } = useParams<{ id: string }>()
  const [session, setSession] = useState<StudySession | null>(null)
  const [words, setWords] = useState<Word[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return
      
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(
          `http://localhost:5000/api/study-sessions/${id}?page=${currentPage}&per_page=10`
        )
        if (!response.ok) {
          throw new Error('Failed to fetch session data')
        }
        const data: SessionResponse = await response.json()
        console.log('Fetched data:', data)
        setSession(data.session)
        setWords(data.words)
        setTotalPages(data.total_pages)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [id, currentPage])

  if (loading) {
    return <div className="text-center py-4">Loading...</div>
  }

  if (error || !session) {
    return <div className="text-red-500 text-center py-4">{error || 'Session not found'}</div>
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Study Session Details</h1>
        <Link
          to="/sessions"
          className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 dark:text-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
        >
          Back to Sessions
        </Link>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400">Activity</h2>
            <Link to={`/study-activities/${session.activity_id}`} className="text-blue-600 dark:text-blue-400 hover:underline">
              {session.activity_name}
            </Link>
          </div>
          <div>
            <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400">Group</h2>
            <Link to={`/groups/${session.group_id}`} className="text-blue-600 dark:text-blue-400 hover:underline">
              {session.group_name}
            </Link>
          </div>
          <div>
            <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400">Start Time</h2>
            <p className="text-gray-900 dark:text-gray-100">{session.start_time}</p>
          </div>
          <div>
            <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400">Review Items</h2>
            <p className="text-gray-900 dark:text-gray-100">{session.review_items_count}</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Words Reviewed</h2>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Kanji
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Romaji
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  English
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Correct
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Wrong
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {words.map((word) => (
                <tr key={word.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-gray-900 dark:text-gray-100">
                    {word.kanji}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-900 dark:text-gray-100">
                    {word.romaji}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-900 dark:text-gray-100">
                    {word.english}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                      {word.correct_count || 0} ✓
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100">
                      {word.wrong_count || 0} ✗
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="mt-4">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          </div>
        )}
      </div>
    </div>
  )
}
