import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api, getCurrentUserId } from '../api'


export default function Dashboard() {
  const { id: projectId } = useParams()
  const currentUserId = getCurrentUserId()
  const [isAdmin, setIsAdmin] = useState(false)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getProjects()
      .then((projects) => {
        const project = projects.find((p) => p.id === parseInt(projectId))
        const adminCheck = project?.created_by === currentUserId
        setIsAdmin(adminCheck)
        return adminCheck
          ? api.getDashboard(projectId)
          : api.getMemberDashboard(projectId)
      })
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [projectId])


  if (loading) return <div className="page"><p>Loading dashboard...</p></div>
  if (error) return <div className="page"><div className="error-msg">{error}</div></div>

  return (
    <div className="page">
      <Link to={`/project/${projectId}`} className="back-link">
        ← Back to Project
      </Link>

      <div className="page-header">
        <h1>📊 Project Dashboard</h1>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{data.total_tasks}</div>
          <div className="stat-label">Total Tasks</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#9ca3af' }}>
            {data.by_status?.['To Do'] ?? 0}
          </div>
          <div className="stat-label">To Do</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#f59e0b' }}>
            {data.by_status?.['In Progress'] ?? 0}
          </div>
          <div className="stat-label">In Progress</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#10b981' }}>
            {data.by_status?.['Done'] ?? 0}
          </div>
          <div className="stat-label">Done</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#ef4444' }}>
            {data.overdue_tasks?.length ?? 0}
          </div>
          <div className="stat-label">Overdue</div>
        </div>
      </div>

      <div className="section-row">
        {/* Tasks per user */}
        {isAdmin && (
          <div>
            <div className="section-title">Tasks Per Member</div>
            <div className="card">
              {Object.keys(data.tasks_per_user || {}).length === 0 ? (
                <div className="empty-state">No assigned tasks yet</div>
              ) : (
                Object.entries(data.tasks_per_user).map(([username, count]) => (
                  <div
                    key={username}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.7rem 0',
                      borderBottom: '1px solid #f3f4f6',
                    }}
                  >
                    <span style={{ color: '#374151', fontSize: '0.9rem', fontWeight: 600 }}>
                      👤 {username}
                    </span>
                    <span
                      style={{
                        background: '#ede9fe',
                        color: '#5b21b6',
                        padding: '0.2rem 0.7rem',
                        borderRadius: '20px',
                        fontWeight: 700,
                        fontSize: '0.85rem',
                      }}
                    >
                      {count} task{count !== 1 ? 's' : ''}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Overdue Tasks */}
        <div>
          <div className="section-title">⚠ Overdue Tasks</div>
          <div className="card">
            {(data.overdue_tasks || []).length === 0 ? (
              <div className="empty-state">No overdue tasks 🎉</div>
            ) : (
              data.overdue_tasks.map((task) => (
                <div
                  key={task.id}
                  style={{
                    padding: '0.7rem 0',
                    borderBottom: '1px solid #f3f4f6',
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{task.title}</div>
                  <div style={{ fontSize: '0.78rem', color: '#ef4444', marginTop: '0.2rem' }}>
                    Due: {new Date(task.due_date).toLocaleDateString()}
                  </div>
                  <div
                    style={{
                      fontSize: '0.75rem',
                      color: '#6b7280',
                      marginTop: '0.15rem',
                    }}
                  >
                    Status: {task.status}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
