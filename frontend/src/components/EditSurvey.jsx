// Edit survey component for updating an existing student survey record
import { useEffect, useState } from 'react'
import axios from 'axios'
import { useParams, useNavigate } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const STATES = [
  'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA',
  'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD',
  'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
  'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC',
  'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC'
]

const inp = {
  width: '100%',
  padding: '8px',
  marginBottom: '12px',
  boxSizing: 'border-box',
  border: '1px solid #ccc',
  borderRadius: '4px',
  fontSize: '14px'
}
const lbl = {
  fontWeight: 'bold',
  display: 'block',
  marginBottom: '4px',
  fontSize: '14px'
}

export default function EditSurvey() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    axios.get(`${API}/surveys/${id}`)
      .then(res => setForm(res.data))
      .catch(() => alert('Error loading survey.'))
  }, [id])

  const handleChange = e =>
    setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      await axios.put(`${API}/surveys/${id}`, form)
      navigate('/surveys')
    } catch {
      alert('Error updating survey.')
    }
    setLoading(false)
  }

  if (!form) return <p style={{ padding: '2rem' }}>Loading...</p>

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', padding: '0 1rem' }}>
      <h2 style={{ color: '#003366' }}>Edit Survey #{id}</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
          <div>
            <label style={lbl}>First Name</label>
            <input style={inp} name="first_name" value={form.first_name || ''}
              onChange={handleChange} />
          </div>
          <div>
            <label style={lbl}>Last Name</label>
            <input style={inp} name="last_name" value={form.last_name || ''}
              onChange={handleChange} />
          </div>
        </div>

        <label style={lbl}>Street Address</label>
        <input style={inp} name="street_address" value={form.street_address || ''}
          onChange={handleChange} />

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '0 1rem' }}>
          <div>
            <label style={lbl}>City</label>
            <input style={inp} name="city" value={form.city || ''}
              onChange={handleChange} />
          </div>
          <div>
            <label style={lbl}>State</label>
            <select style={inp} name="state" value={form.state || ''}
              onChange={handleChange}>
              {STATES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label style={lbl}>Zip</label>
            <input style={inp} name="zip" value={form.zip || ''}
              onChange={handleChange} />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
          <div>
            <label style={lbl}>Telephone</label>
            <input style={inp} name="telephone" value={form.telephone || ''}
              onChange={handleChange} />
          </div>
          <div>
            <label style={lbl}>Email</label>
            <input style={inp} type="email" name="email" value={form.email || ''}
              onChange={handleChange} />
          </div>
        </div>

        <label style={lbl}>Date of Survey</label>
        <input style={inp} type="date" name="date_of_survey"
          value={form.date_of_survey || ''} onChange={handleChange} />

        <label style={lbl}>What did you like most about the campus?</label>
        <select style={inp} name="liked_most" value={form.liked_most || ''}
          onChange={handleChange}>
          {['Students', 'Location', 'Campus', 'Atmosphere', 'Dorm Rooms', 'Sports']
            .map(o => <option key={o} value={o}>{o}</option>)}
        </select>

        <label style={lbl}>How did you become interested in this university?</label>
        <select style={inp} name="interested_via" value={form.interested_via || ''}
          onChange={handleChange}>
          {['Friends', 'Television', 'Internet', 'Other']
            .map(o => <option key={o} value={o}>{o}</option>)}
        </select>

        <label style={lbl}>Likelihood of recommending this school?</label>
        <select style={inp} name="recommend_likelihood"
          value={form.recommend_likelihood || ''} onChange={handleChange}>
          {['Very Likely', 'Likely', 'Unlikely']
            .map(o => <option key={o} value={o}>{o}</option>)}
        </select>

        <div style={{ marginTop: '8px', display: 'flex', gap: '8px' }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              background: '#003366',
              color: 'white',
              padding: '10px 24px',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              borderRadius: '4px',
              fontSize: '15px',
              opacity: loading ? 0.7 : 1
            }}>
            {loading ? 'Updating...' : 'Update Survey'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/surveys')}
            style={{
              padding: '10px 24px',
              border: '1px solid #ccc',
              cursor: 'pointer',
              borderRadius: '4px',
              fontSize: '15px',
              background: 'white'
            }}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}