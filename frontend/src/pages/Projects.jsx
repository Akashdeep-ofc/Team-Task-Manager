import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'

export default function Projects() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Create project modal state
  const [showModal, setShowModal] = useState(false)
  const [view, setView] = useState('admin')
  const [newProjectName, setNewProjectName] = useState('')
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState('')

  useEffect(() => {
    loadProjects()
  }, [view])



  const loadProjects = async () => {
    try {
      const data = view === 'admin'
        ? await api.getProjects()
        : await api.getMemberProjects()
      setProjects(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreateError('')
    setCreating(true)
    try {
      const project = await api.createProject(newProjectName)
      setProjects([...projects, project])
      setNewProjectName('')
      setShowModal(false)
    } catch (err) {
      setCreateError(err.message)
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (e, projectId) => {
    // Stop the click from navigating to the project
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('Delete this project? All tasks will be removed.')) return
    try {
      await api.deleteProject(projectId)
      setProjects(projects.filter((p) => p.id !== projectId))
    } catch (err) {
      alert(err.message)
    }
  }

  if (loading) return <div className="page"><p>Loading projects...</p></div>

  return (
    <div className="page">
      <div className="page-header">
        <h1>My Projects</h1>
        <div style={{ display: 'flex', gap: '1.8rem', alignItems: 'center' }}>
          
          {/* Button — compact */}
          <div style={{ width: '180px' }}>
            <button
              className="btn btn-primary"
              onClick={handleCreate}
              disabled={view !== 'admin'}
              style={{
                width: '100%',
                opacity: view === 'admin' ? 1 : 0.5,
                cursor: view === 'admin' ? 'pointer' : 'not-allowed'
              }}
            >
              + New Project
            </button>
          </div>
          
          {/* Toggle — wider */}
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', background: '#e5e7eb', borderRadius: '8px', padding: '3px', width: '100%' }}>
              <button
                className={`btn btn-sm ${view === 'admin' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setView('admin')}
                style={{ flex: 1, borderRadius: '6px' }}
              >
                👑 Admin View
              </button>

              <button
                className={`btn btn-sm ${view === 'member' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setView('member')}
                style={{ flex: 1, borderRadius: '6px' }}
              >
                👤 Member View
              </button>
            </div>
          </div>


        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {projects.length === 0 ? (
        <div className="empty-state">
          <p style={{ fontSize: '3rem', marginBottom: '1rem' }}>📂</p>
          <p>No projects yet. Create your first one!</p>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <Link
              to={`/project/${project.id}`}
              className="project-card"
              key={project.id}
            >
              <h3>{project.name}</h3>
              <p style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
                Created {new Date(project.created_at).toLocaleDateString()}
              </p>
              <div className="project-card-footer">
                <Link
                  to={`/project/${project.id}/dashboard`}
                  className="link"
                  style={{ fontSize: '0.82rem' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  📊 Dashboard
                </Link>
                {view === 'admin' && (
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={(e) => handleDelete(e, project.id)}
                  >
                    Delete
                  </button>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Create Project Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Project</h2>
            {createError && <div className="error-msg">{createError}</div>}
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Project Name</label>
                <input
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="e.g. Website Redesign"
                  required
                  autoFocus
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-success" disabled={creating}>
                  {creating ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
