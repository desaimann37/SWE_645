// Survey list component displaying all submitted surveys with edit and delete options
import { useEffect, useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function SurveyList() {
  const [surveys, setSurveys] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const fetchSurveys = async () => {
    try {
      const res = await axios.get(`${API}/surveys/`)
      setSurveys(res.data)
    } catch {
      alert('Error fetching surveys.')
    }
    setLoading(false)
  }

  useEffect(() => { fetchSurveys() }, [])

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this survey?')) return
    try {
      await axios.delete(`${API}/surveys/${id}`)
      fetchSurveys()
    } catch {
      alert('Error deleting survey.')
    }
  }

  const th = {
    padding: '10px 8px',
    border: '1px solid #ddd',
    textAlign: 'left',
    whiteSpace: 'nowrap'
  }
  const td = { padding: '8px', border: '1px solid #ddd', fontSize: '13px' }

  if (loading) return <p style={{ padding: '2rem' }}>Loading surveys...</p>

  return (
    <div style={{ padding: '2rem', overflowX: 'auto' }}>
      <h2 style={{ color: '#003366' }}>
        All Surveys
        <span style={{
          marginLeft: '12px',
          background: '#003366',
          color: 'white',
          borderRadius: '12px',
          padding: '2px 10px',
          fontSize: '14px'
        }}>
          {surveys.length}
        </span>
      </h2>

      {surveys.length === 0 ? (
        <p style={{ color: '#666' }}>No surveys submitted yet.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
          <thead>
            <tr style={{ background: '#003366', color: 'white' }}>
              {['ID', 'First Name', 'Last Name', 'Email', 'City', 'State',
                'Zip', 'Phone', 'Date', 'Liked Most', 'Heard Via', 'Recommend', 'Actions']
                .map(h => <th key={h} style={th}>{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {surveys.map((s, i) => (
              <tr key={s.id}
                style={{ background: i % 2 === 0 ? '#f9f9f9' : 'white' }}>
                <td style={td}>{s.id}</td>
                <td style={td}>{s.first_name}</td>
                <td style={td}>{s.last_name}</td>
                <td style={td}>{s.email}</td>
                <td style={td}>{s.city}</td>
                <td style={td}>{s.state}</td>
                <td style={td}>{s.zip}</td>
                <td style={td}>{s.telephone}</td>
                <td style={td}>{s.date_of_survey}</td>
                <td style={td}>{s.liked_most}</td>
                <td style={td}>{s.interested_via}</td>
                <td style={td}>{s.recommend_likelihood}</td>
                <td style={td}>
                  <button
                    onClick={() => navigate(`/edit/${s.id}`)}
                    style={{
                      marginRight: '4px',
                      background: '#f0a500',
                      border: 'none',
                      padding: '4px 10px',
                      cursor: 'pointer',
                      borderRadius: '3px',
                      fontSize: '12px'
                    }}>
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(s.id)}
                    style={{
                      background: '#cc0000',
                      color: 'white',
                      border: 'none',
                      padding: '4px 10px',
                      cursor: 'pointer',
                      borderRadius: '3px',
                      fontSize: '12px'
                    }}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}