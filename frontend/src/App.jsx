import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import Dashboard from './pages/Dashboard'
import Navbar from './components/Navbar'

// Wraps routes that require login
// If no token found, redirect to /login
function PrivateRoute({ children }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" />
  return (
    <>
      <Navbar />
      {children}
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        <Route path="/" element={
          <PrivateRoute><Projects /></PrivateRoute>
        } />

        <Route path="/project/:id" element={
          <PrivateRoute><ProjectDetail /></PrivateRoute>
        } />

        <Route path="/project/:id/dashboard" element={
          <PrivateRoute><Dashboard /></PrivateRoute>
        } />

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}
