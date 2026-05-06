// ⚠️ Change this to match your backend URL
// In development: http://localhost:8000
// After deployment: your Railway backend URL
const BASE_URL = 'http://localhost:8000'

// ⚠️ Change this prefix to match how you included the router in your main.py
// If your main.py does: app.include_router(router, prefix="/users") → use "/users"
// If no prefix: use ""
const PROJECT_PREFIX = '/user/project'
const TASK_PREFIX = (projectId) => `/user/project/${projectId}/task`
const USER_PREFIX = '/user'  // adjust to whatever prefix your user router uses


const projectUrl = (path = '') => `${BASE_URL}${PROJECT_PREFIX}${path}`
const taskUrl = (projectId, path = '') => `${BASE_URL}${TASK_PREFIX(projectId)}${path}`
const userUrl = (path = '') => `${BASE_URL}${USER_PREFIX}${path}`

// const url = (path) => `${BASE_URL}${PREFIX}${path}`

// Builds headers — automatically includes JWT token if logged in
const headers = (isForm = false) => ({
  ...(isForm
    ? { 'Content-Type': 'application/x-www-form-urlencoded' }
    : { 'Content-Type': 'application/json' }),
  ...(localStorage.getItem('token') && {
    Authorization: `Bearer ${localStorage.getItem('token')}`,
  }),
})

// Helper — throws error if response is not OK, otherwise returns JSON
const handle = async (res) => {
  if (!res.ok) {
    if (res.status === 401) {
      // 🔥 Token expired → force logout
      localStorage.removeItem('token')

      // redirect to login
      window.location.href = '/login'
      return
    }

    const err = await res.json().catch(() => ({ detail: 'Something went wrong' }))
    throw new Error(err.detail || 'Something went wrong')
  }
  if (res.status === 204) return null
  return res.json()
}

// Decode JWT to get current user's id (stored as "sub" in token payload)
export const getCurrentUserId = () => {
  const token = localStorage.getItem('token')
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return parseInt(payload.sub)
  } catch {
    return null
  }
}

export const api = {
  // ── AUTH ──────────────────────────────────────────────────────────────────

  signup: (username, email, password) =>
    fetch(userUrl(''), {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ username, email, password }),
    }).then(handle),

  // OAuth2PasswordRequestForm expects form data, not JSON
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email) // FastAPI OAuth2 form uses "username" field for email
    form.append('password', password)
    return fetch(userUrl('/token'), {
      method: 'POST',
      headers: headers(true),
      body: form,
    }).then(handle)
  },

  // ── PROJECTS ──────────────────────────────────────────────────────────────

  getProjects: () =>
    fetch(projectUrl(''), { headers: headers() }).then(handle),

  getMemberProjects: () =>
    fetch(`${BASE_URL}/user/member-projects`, { headers: headers() }).then(handle),


  createProject: (name) =>
    fetch(projectUrl(''), {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ name }),
    }).then(handle),

  deleteProject: (projectId) =>
    fetch(projectUrl(`/${projectId}`), { method: 'DELETE', headers: headers() }).then(handle),


  // ── TASKS ─────────────────────────────────────────────────────────────────

  getTasks: (projectId, filters = {}) => {
    const params = new URLSearchParams()
    if (filters.task_status) params.set('task_status', 'true')
    if (filters.overdue) params.set('overdue', 'true')
    if (filters.per_user) params.set('per_user', 'true')
    const qs = params.toString() ? `?${params}` : ''
    return fetch(taskUrl(projectId, `${qs}`), { headers: headers() }).then(handle)
  },

  createTask: (projectId, taskData) =>
    fetch(taskUrl(projectId), {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify(taskData),
    }).then(handle),

  updateTaskStatus: (projectId, taskId, newStatus) =>
    fetch(taskUrl(projectId, `/${taskId}?new_status=${encodeURIComponent(newStatus)}`), {
      method: 'PATCH',
      headers: headers(),
    }).then(handle),

  deleteTask: (projectId, taskId) =>
    fetch(taskUrl(projectId, `/${taskId}`), {
      method: 'DELETE',
      headers: headers(),
    }).then(handle),


  assignTask: (projectId, taskId, memberEmail) =>
    fetch(taskUrl(projectId, `/${taskId}`), {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ member_email: memberEmail }),  // Body(embed=True)
    }).then(handle),

  // ── MEMBERS ───────────────────────────────────────────────────────────────

  getMembers: (projectId) =>
    fetch(projectUrl(`/${projectId}/members`), { headers: headers() }).then(handle),


  addMember: (projectId, email) =>
    fetch(projectUrl(`/${projectId}/add`), {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ member_email: email }),  // Body(embed=True)
    }).then(handle),


  removeMember: (projectId, memberId) =>
    fetch(projectUrl(`/${projectId}/members/${memberId}`), {
      method: 'DELETE',
      headers: headers(),
    }).then(handle),

  // ── DASHBOARD ─────────────────────────────────────────────────────────────

  getDashboard: (projectId) =>
    fetch(projectUrl(`/${projectId}/admin-dashboard-summary`), { headers: headers() }).then(handle),

  getMemberDashboard: (projectId) =>
    fetch(projectUrl(`/${projectId}/member-dashboard-summary`), { headers: headers() }).then(handle),
}
