import { Link, useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">📋 Task Manager</Link>
      <div className="navbar-right">
        <button onClick={logout}>Logout</button>
      </div>
    </nav>
  )
}
