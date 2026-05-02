import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import SurveyForm from './components/SurveyForm'
import SurveyList from './components/SurveyList'
import EditSurvey from './components/EditSurvey'
import AISurveyAssistant from './components/AISurveyAssistant'

const navLink = {
  color: 'white',
  textDecoration: 'none',
  padding: '4px 10px',
  borderRadius: '4px',
}

function NavBar() {
  const location = useLocation()
  const active = { background: 'rgba(255,255,255,0.2)', borderRadius: '4px' }
  return (
    <nav style={{
      padding: '0.75rem 2rem',
      background: '#003366',
      color: 'white',
      display: 'flex',
      gap: '1.5rem',
      alignItems: 'center',
      height: '56px',
      boxSizing: 'border-box',
    }}>
      <span style={{ fontWeight: 'bold', fontSize: '1.1rem', marginRight: '8px' }}>
        University Survey Portal
      </span>
      <Link to="/" style={{ ...navLink, ...(location.pathname === '/' ? active : {}) }}>
        Submit Survey
      </Link>
      <Link to="/surveys" style={{ ...navLink, ...(location.pathname === '/surveys' ? active : {}) }}>
        View All Surveys
      </Link>
      <Link to="/chat" style={{ ...navLink, ...(location.pathname === '/chat' ? active : {}), background: location.pathname === '/chat' ? 'rgba(255,255,255,0.2)' : '#1a56a0', border: '1px solid rgba(255,255,255,0.4)' }}>
        AI Survey Assistant
      </Link>
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<SurveyForm />} />
        <Route path="/surveys" element={<SurveyList />} />
        <Route path="/edit/:id" element={<EditSurvey />} />
        <Route path="/chat" element={<AISurveyAssistant />} />
      </Routes>
    </BrowserRouter>
  )
}