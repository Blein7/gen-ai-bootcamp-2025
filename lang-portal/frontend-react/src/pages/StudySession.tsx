import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import WordReviewsTable from '../components/WordReviewsTable'
import { fetchStudySession } from '../services/api'

interface Word {
  id: number
  kanji: string
  romaji: string
  english: string
  correct_count: number
  wrong_count: number
}

interface Session {
  id: number
  group_id: number
  group_name: string
  activity_id: number
  activity_name: string
  start_time: string
  end_time: string
  review_items_count: number
  correct_count: number
  wrong_count: number
}

const StudySession: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const [session, setSession] = useState<Session | null>(null)
  const [words, setWords] = useState<Word[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadSession = async () => {
      try {
        setLoading(true)
        const response = await fetchStudySession(Number(id))
        setSession(response.session)
        setWords(response.words)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load session')
      } finally {
        setLoading(false)
      }
    }

    loadSession()
  }, [id])

  if (loading) {
    return <div className="text-center py-4">Loading...</div>
  }

  if (error) {
    return <div className="text-red-500 text-center py-4">{error}</div>
  }

  if (!session) {
    return <div className="text-center py-4">Session not found</div>
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Study Session Details</h1>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <dl className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Group</dt>
            <dd className="mt-1 text-lg text-gray-900 dark:text-white">{session.group_name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Activity</dt>
            <dd className="mt-1 text-lg text-gray-900 dark:text-white">{session.activity_name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Start Time</dt>
            <dd className="mt-1 text-lg text-gray-900 dark:text-white">{session.start_time}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Reviews</dt>
            <dd className="mt-1 text-lg text-gray-900 dark:text-white">{session.review_items_count}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Results</dt>
            <dd className="mt-1 flex items-center space-x-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                {session.correct_count} ✓
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100">
                {session.wrong_count} ✗
              </span>
            </dd>
          </div>
        </dl>
      </div>
      <WordReviewsTable words={words} />
    </div>
  )
}

export default StudySession
