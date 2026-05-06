import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api, getCurrentUserId } from '../api'

const STATUSES = ['To Do', 'In Progress', 'Done']
const PRIORITIES = ['low', 'medium', 'high']

// ── Small helper components ───────────────────────────────

function TaskCard({ task, isAdmin, onStatusChange, onDelete, onAssign }) {
  const isOverdue =
    task.due_date &&
    new Date(task.due_date) < new Date() &&
    task.status !== 'Done'

  const priorityClass = task.priority ? `priority-${task.priority}` : ''

  return (
    <div className={`task-card ${priorityClass}`}>
      <div className="task-title">{task.title}</div>

      {task.description && (
        <div className="task-desc">{task.description}</div>
      )}

      <div className="task-meta">
        {task.priority && (
          <span className={`badge badge-priority-${task.priority}`}>
            {task.priority}
          </span>
        )}
        {task.due_date && (
          <span className={`badge ${isOverdue ? 'badge-overdue' : 'badge-due'}`}>
            {isOverdue ? '⚠ Overdue' : '📅'}{' '}
            {new Date(task.due_date).toLocaleDateString()}
          </span>
        )}
        {task.assigned_to ? (
          <span className="badge" style={{ background: '#e0e7ff', color: '#3730a3' }}>
            👤 Assigned
          </span>
        ) : (
          <span className="badge" style={{ background: '#f3f4f6', color: '#6b7280' }}>
            Unassigned
          </span>
        )}
      </div>

      <div className="task-actions">
        {/* Status change — admin can change any, member can change their own */}
        <select
          value={task.status}
          onChange={(e) => onStatusChange(task.id, e.target.value)}
          style={{
            fontSize: '0.78rem',
            padding: '0.25rem 0.5rem',
            borderRadius: '6px',
            border: '1.5px solid #d1d5db',
            cursor: 'pointer',
          }}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        {/* Admin-only actions */}
        {isAdmin && (
          <>
            {!task.assigned_to && (
              <button
                className="btn btn-sm btn-outline"
                onClick={() => onAssign(task)}
              >
                Assign
              </button>
            )}
            <button
              className="btn btn-sm btn-danger"
              onClick={() => onDelete(task.id)}
            >
              Delete
            </button>
          </>
        )}
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────

export default function ProjectDetail() {
  const { id: projectId } = useParams()
  const currentUserId = getCurrentUserId()

  const [project, setProject] = useState(null)
  // const [tasks, setTasks] = useState({ 'To Do': [], 'In Progress': [], Done: [] })
  const [members, setMembers] = useState([])
  const [isAdmin, setIsAdmin] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('tasks') // 'tasks' | 'members'
  const [filter, setFilter] = useState('all')
  const [allTasks, setAllTasks] = useState([])
  const [statusTasks, setStatusTasks] = useState({ 'To Do': [], 'In Progress': [], Done: [] })
  const [overdueTasks, setOverdueTasks] = useState([])
  const [perUserTasks, setPerUserTasks] = useState({})

  // Create task modal
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [taskForm, setTaskForm] = useState({
    title: '', description: '', due_date: '', priority: '', status: 'To Do',
  })
  const [taskError, setTaskError] = useState('')
  const [taskLoading, setTaskLoading] = useState(false)

  // Assign task modal
  const [assignTask, setAssignTask] = useState(null) // task being assigned
  const [assignEmail, setAssignEmail] = useState('')
  const [assignError, setAssignError] = useState('')

  // Add member
  const [memberEmail, setMemberEmail] = useState('')
  const [memberError, setMemberError] = useState('')
  const [memberSuccess, setMemberSuccess] = useState('')

  useEffect(() => {
    loadAll()
  }, [projectId])

  const loadAll = async () => {
    setLoading(true)
    try {
      // const [projectData, tasksData, membersData] = await Promise.all([
      //   api.getProjects().then((ps) => ps.find((p) => p.id === parseInt(projectId))),
      //   api.getTasks(projectId),
      //   api.getMembers(projectId).catch(() => []), // members endpoint is admin-only
      // ])
      const projectIdInt = parseInt(projectId)

      // fetch BOTH
      const [adminProjects, memberProjects] = await Promise.all([
        api.getProjects().catch(() => []),
        api.getMemberProjects().catch(() => []),
      ])

      const allProjects = [...adminProjects, ...memberProjects]

      const projectData = allProjects.find(
        (p) => p.id === projectIdInt
      )

      // fetch rest
      const [tasksData, membersData] = await Promise.all([
        api.getTasks(projectId),
        api.getMembers(projectId).catch(() => []),
      ])

      setProject(projectData)
      setAllTasks(tasksData || [])
      setMembers(membersData || [])

      // Determine if current user is admin
      const adminCheck = projectData?.created_by === currentUserId
      setIsAdmin(adminCheck)
      if (adminCheck) {
        const pu = await api.getTasks(projectId, { per_user: true })
        setPerUserTasks(pu)
      }
      const [byStatus, overdue] = await Promise.all([
        api.getTasks(projectId, { task_status: true }),
        api.getTasks(projectId, { overdue: true }),
      ])
      setStatusTasks(byStatus)
      setOverdueTasks(overdue)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadTasks = async () => {
    const [all, byStatus, overdue] = await Promise.all([
      api.getTasks(projectId),
      api.getTasks(projectId, { task_status: true }),
      api.getTasks(projectId, { overdue: true }),
    ])
    setAllTasks(all)
    setStatusTasks(byStatus)
    setOverdueTasks(overdue)

    if (isAdmin) {
      const pu = await api.getTasks(projectId, { per_user: true })
      setPerUserTasks(pu)
    }
  }

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await api.updateTaskStatus(projectId, taskId, newStatus)
      // Reload tasks after update
      const [all, byStatus, overdue] = await Promise.all([
        api.getTasks(projectId),
        api.getTasks(projectId, { task_status: true }),
        api.getTasks(projectId, { overdue: true }),
      ])
      setAllTasks(all)
      setStatusTasks(byStatus)
      setOverdueTasks(overdue)
    } catch (err) {
      alert(err.message)
    }
  }

  const handleDeleteTask = async (taskId) => {
    if (!confirm('Delete this task?')) return
    try {
      await api.deleteTask(projectId, taskId)
      const [all, byStatus, overdue] = await Promise.all([
        api.getTasks(projectId),
        api.getTasks(projectId, { task_status: true }),
        api.getTasks(projectId, { overdue: true }),
      ])
      setAllTasks(all)
      setStatusTasks(byStatus)
      setOverdueTasks(overdue)
    } catch (err) {
      alert(err.message)
    }
  }

  const handleCreateTask = async (e) => {
    e.preventDefault()
    setTaskError('')
    setTaskLoading(true)
    try {
      // Clean up empty optional fields before sending
      const payload = { ...taskForm }
      if (!payload.description) delete payload.description
      if (!payload.due_date) delete payload.due_date
      if (!payload.priority) delete payload.priority

      await api.createTask(projectId, payload)
      const [all, byStatus, overdue] = await Promise.all([
        api.getTasks(projectId),
        api.getTasks(projectId, { task_status: true }),
        api.getTasks(projectId, { overdue: true }),
      ])
      setAllTasks(all)
      setStatusTasks(byStatus)
      setOverdueTasks(overdue)
      setShowTaskModal(false)
      setTaskForm({ title: '', description: '', due_date: '', priority: '', status: 'To Do' })
    } catch (err) {
      setTaskError(err.message)
    } finally {
      setTaskLoading(false)
    }
  }

  const handleAssign = async (e) => {
    e.preventDefault()
    setAssignError('')
    try {
      await api.assignTask(projectId, assignTask.id, assignEmail)
      // const tasksData = await api.getTasksGrouped(projectId)
      // setAllTasks(tasksData)
      await loadTasks()
      setAssignTask(null)
      setAssignEmail('')
    } catch (err) {
      setAssignError(err.message)
    }
  }

  const handleAddMember = async (e) => {
    e.preventDefault()
    setMemberError('')
    setMemberSuccess('')
    try {
      await api.addMember(projectId, memberEmail)
      setMemberSuccess(`${memberEmail} added successfully`)
      setMemberEmail('')
      const membersData = await api.getMembers(projectId)
      setMembers(membersData)
    } catch (err) {
      setMemberError(err.message)
    }
  }

  const handleRemoveMember = async (memberId) => {
    if (!confirm('Remove this member from the project?')) return
    try {
      await api.removeMember(projectId, memberId)
      setMembers(members.filter((m) => m.user_id !== memberId))
    } catch (err) {
      alert(err.message)
    }
  }

  if (loading) return <div className="page"><p>Loading project...</p></div>
  if (error) return <div className="page"><div className="error-msg">{error}</div></div>
  if (!project) return <div className="page"><p>Project not found.</p></div>

  const dotClass = { 'To Do': 'dot-todo', 'In Progress': 'dot-progress', Done: 'dot-done' }

  return (
    <div className="page">
      {/* Header */}
      <Link to="/" className="back-link">← Back to Projects</Link>

      <div className="page-header">
        <div>
          <h1>{project.name}</h1>
          <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>
            {isAdmin ? '👑 You are the Admin' : '👤 You are a Member'}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '0.8rem' }}>
          <Link to={`/project/${projectId}/dashboard`} className="btn btn-secondary btn-sm">
            📊 Dashboard
          </Link>
          {isAdmin && (
            <button className="btn btn-outline btn-sm" onClick={() => setShowTaskModal(true)}>
              + New Task
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'tasks' ? 'active' : ''}`}
          onClick={() => setActiveTab('tasks')}
        >
          Tasks
        </button>
        {isAdmin && (
          <button
            className={`tab ${activeTab === 'members' ? 'active' : ''}`}
            onClick={() => setActiveTab('members')}
          >
            Members ({members.length})
          </button>
        )}
      </div>

      {/* Tasks Tab — Kanban Board */}
      {activeTab === 'tasks' && (
        <div>
          {/* Filter bar */}
          <div style={{ display: 'flex', gap: '0.6rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
            {[
              { label: '📋 All Tasks', value: 'all' },
              { label: '🗂 By Status', value: 'status' },
              { label: '⚠ Overdue', value: 'overdue' },
              ...(isAdmin ? [{ label: '👥 Per User', value: 'per_user' }] : []),
            ].map((f) => (
              <button
                key={f.value}
                className={`btn btn-sm ${filter === f.value ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setFilter(f.value)}
                style={{ width: 'auto' }} 
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* All Tasks — flat list */}
          {/* {filter === 'all' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              {allTasks.length === 0
                ? <div className="empty-state">No tasks yet</div>
                : allTasks.map((task) => (
                  <TaskCard key={task.id} task={task} isAdmin={isAdmin}
                    onStatusChange={handleStatusChange}
                    onDelete={handleDeleteTask}
                    onAssign={setAssignTask}
                  />
                ))}
            </div>
          )} */}
          <div style={{ display: filter === 'all' ? 'flex' : 'none', flexDirection: 'column', gap: '0.8rem', minHeight: '400px' }}>
            {allTasks.length === 0
              ? <div className="empty-state">No tasks yet</div>
              : allTasks.map((task) => (
                <TaskCard key={task.id} task={task} isAdmin={isAdmin}
                  onStatusChange={handleStatusChange}
                  onDelete={handleDeleteTask}
                  onAssign={setAssignTask}
                />
              ))}
          </div>

          {/* By Status — kanban columns */}
          <div style={{ display: filter === 'status' ? 'grid' : 'none', gridTemplateColumns: 'repeat(3,1fr)', gap: '1.2rem', minHeight: '400px' }}>
            {STATUSES.map((status) => (
              <div className="kanban-col" key={status}>
                <div className="kanban-col-header">
                  <span className={`dot ${dotClass[status]}`} />
                  {status}
                  <span style={{ marginLeft: 'auto', color: '#9ca3af', fontWeight: 400 }}>
                    {(statusTasks[status] || []).length}
                  </span>
                </div>
                {(statusTasks[status] || []).length === 0
                  ? <div className="empty-state">No tasks</div>
                  : (statusTasks[status] || []).map((task) => (
                    <TaskCard key={task.id} task={task} isAdmin={isAdmin}
                      onStatusChange={handleStatusChange}
                      onDelete={handleDeleteTask}
                      onAssign={setAssignTask}
                    />
                  ))}
              </div>
            ))}
          </div>


          <div style={{ display: filter === 'overdue' ? 'flex' : 'none', flexDirection: 'column', gap: '0.8rem', minHeight: '400px' }}>
            {overdueTasks.length === 0
              ? <div className="empty-state">No overdue tasks 🎉</div>
              : overdueTasks.map((task) => (
                <TaskCard key={task.id} task={task} isAdmin={isAdmin}
                  onStatusChange={handleStatusChange}
                  onDelete={handleDeleteTask}
                  onAssign={setAssignTask}
                />
              ))}
          </div>

          {/* Per User — admin only */}
          <div style={{ display: filter === 'per_user' && isAdmin ? 'block' : 'none', minHeight: '400px' }}>
            {Object.entries(perUserTasks).map(([userId, tasks]) => (
              <div key={userId} style={{ marginBottom: '1.5rem' }}>
                <div className="section-title">User #{userId}</div>
                {tasks.map((task) => (
                  <TaskCard key={task.id} task={task} isAdmin={isAdmin}
                    onStatusChange={handleStatusChange}
                    onDelete={handleDeleteTask}
                    onAssign={setAssignTask}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Members Tab */}
      {activeTab === 'members' && isAdmin && (
        <div style={{ maxWidth: '600px' }}>
          {/* Add member form */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <div className="section-title">Add Member</div>
            {memberError && <div className="error-msg">{memberError}</div>}
            {memberSuccess && <div className="success-msg">{memberSuccess}</div>}
            <form onSubmit={handleAddMember} style={{ display: 'flex', gap: '0.8rem' }}>
              <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                <input
                  type="email"
                  value={memberEmail}
                  onChange={(e) => setMemberEmail(e.target.value)}
                  placeholder="member@email.com"
                  required
                />
              </div>
              <button type="submit" className="btn btn-success">Add</button>
            </form>
          </div>

          {/* Members list */}
          <div className="section-title">Project Members</div>
          <div className="members-list">
            {members.map((m) => (
              <div className="member-row" key={m.user_id}>
                <div className="member-info">
                  <span className="member-name">{m.username}</span>
                  <span className="member-email">{m.email}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <span className={`member-role ${m.role === 'admin' ? 'admin' : ''}`}>
                    {m.role}
                  </span>
                  {m.role !== 'admin' && (
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleRemoveMember(m.user_id)}
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Task Modal */}
      {showTaskModal && (
        <div className="modal-overlay" onClick={() => setShowTaskModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Task</h2>
            {taskError && <div className="error-msg">{taskError}</div>}
            <form onSubmit={handleCreateTask}>
              <div className="form-group">
                <label>Title *</label>
                <input
                  value={taskForm.title}
                  onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
                  placeholder="Task title"
                  required
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={taskForm.description}
                  onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
                  placeholder="Optional description..."
                />
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select
                  value={taskForm.priority}
                  onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}
                >
                  <option value="">No priority</option>
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Due Date</label>
                <input
                  type="date"
                  value={taskForm.due_date}
                  onChange={(e) => setTaskForm({ ...taskForm, due_date: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Initial Status</label>
                <select
                  value={taskForm.status}
                  onChange={(e) => setTaskForm({ ...taskForm, status: e.target.value })}
                >
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowTaskModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-success" disabled={taskLoading}>
                  {taskLoading ? 'Creating...' : 'Create Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Assign Task Modal */}
      {assignTask && (
        <div className="modal-overlay" onClick={() => setAssignTask(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Assign Task</h2>
            <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
              Assigning: <strong>{assignTask.title}</strong>
            </p>
            {assignError && <div className="error-msg">{assignError}</div>}
            <form onSubmit={handleAssign}>
              <div className="form-group">
                <label>Member Email</label>
                <input
                  type="email"
                  value={assignEmail}
                  onChange={(e) => setAssignEmail(e.target.value)}
                  placeholder="member@email.com"
                  required
                  autoFocus
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setAssignTask(null)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-success">Assign</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
