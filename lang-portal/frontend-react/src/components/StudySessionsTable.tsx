import { useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { StudySession, fetchStudySession } from '../services/api'
import WordReviewsTable from './WordReviewsTable'

interface StudySessionsTableProps {
  sessions: StudySession[]
  onRefresh?: () => Promise<void>
}

export default function StudySessionsTable({ sessions, onRefresh }: StudySessionsTableProps) {
  const [sessionWords, setSessionWords] = useState<Record<number, any[]>>({})
  const [loading, setLoading] = useState<Record<number, boolean>>({})
  const [refreshing, setRefreshing] = useState<Record<number, boolean>>({})

  // Fetch words for a single session
  const fetchSessionWords = async (sessionId: number) => {
    setLoading(prev => ({ ...prev, [sessionId]: true }))
    try {
      const response = await fetchStudySession(sessionId)
      setSessionWords(prev => ({ ...prev, [sessionId]: response.words }))
    } catch (error) {
      console.error('Error fetching session words:', error)
    } finally {
      setLoading(prev => ({ ...prev, [sessionId]: false }))
    }
  }

  // Refresh a single session
  const refreshSession = async (sessionId: number) => {
    setRefreshing(prev => ({ ...prev, [sessionId]: true }))
    try {
      // First refresh the session list
      if (onRefresh) {
        await onRefresh()
      }
      // Then refresh the words
      await fetchSessionWords(sessionId)
    } finally {
      setRefreshing(prev => ({ ...prev, [sessionId]: false }))
    }
  }

  // Fetch words for all sessions on mount
  useEffect(() => {
    const fetchAllSessionWords = async () => {
      for (const session of sessions) {
        if (!sessionWords[session.id]) {
          await fetchSessionWords(session.id)
        }
      }
    }

    fetchAllSessionWords()
  }, [sessions])

  return (
    <div className="space-y-8">
      {sessions.map((session) => (
        <div key={session.id} className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          {/* Session header */}
          <div className="px-6 py-4 bg-gray-50 dark:bg-gray-900">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Session #{session.id}</span>
                <span className="text-sm text-gray-500 dark:text-gray-400">{session.activity_name}</span>
                <span className="text-sm text-gray-500 dark:text-gray-400">{session.group_name}</span>
                <span className="text-sm text-gray-500 dark:text-gray-400">{session.start_time}</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                    {session.correct_count || 0} ✓
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100">
                    {session.wrong_count || 0} ✗
                  </span>
                </div>
                <button 
                  onClick={() => refreshSession(session.id)}
                  disabled={refreshing[session.id]}
                  className="p-1.5 rounded-full text-gray-500 hover:text-gray-700 hover:bg-gray-200 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-700 focus:outline-none transition-colors"
                >
                  <RefreshCw className={`h-4 w-4 ${refreshing[session.id] ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>
          </div>

          {/* Word reviews */}
          <div className="px-6 py-4">
            {loading[session.id] ? (
              <div className="text-center py-4">Loading words...</div>
            ) : (
              <WordReviewsTable words={sessionWords[session.id] || []} />
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
