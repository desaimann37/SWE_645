// Survey form component for submitting campus visit feedback
import { useState } from 'react'
import axios from 'axios'

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

export default function SurveyForm() {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    street_address: '',
    city: '',
    state: '',
    zip: '',
    telephone: '',
    email: '',
    date_of_survey: '',
    liked_most: '',
    interested_via: '',
    recommend_likelihood: ''
  })
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = e =>
    setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      await axios.post(`${API}/surveys/`, form)
      setMessage('✅ Survey submitted successfully!')
      setForm({
        first_name: '', last_name: '', street_address: '', city: '',
        state: '', zip: '', telephone: '', email: '', date_of_survey: '',
        liked_most: '', interested_via: '', recommend_likelihood: ''
      })
    } catch {
      setMessage('❌ Error submitting survey. Please try again.')
    }
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', padding: '0 1rem' }}>
      <h2 style={{ color: '#003366' }}>Campus Visit Survey</h2>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        Please fill out all required fields marked with *
      </p>

      {message && (
        <p style={{
          padding: '10px',
          borderRadius: '4px',
          background: message.startsWith('✅') ? '#e6f4ea' : '#fce8e6',
          color: message.startsWith('✅') ? 'green' : 'red',
          marginBottom: '1rem'
        }}>
          {message}
        </p>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
          <div>
            <label style={lbl}>First Name *</label>
            <input style={inp} name="first_name" value={form.first_name}
              onChange={handleChange} required />
          </div>
          <div>
            <label style={lbl}>Last Name *</label>
            <input style={inp} name="last_name" value={form.last_name}
              onChange={handleChange} required />
          </div>
        </div>

        <label style={lbl}>Street Address *</label>
        <input style={inp} name="street_address" value={form.street_address}
          onChange={handleChange} required />

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '0 1rem' }}>
          <div>
            <label style={lbl}>City *</label>
            <input style={inp} name="city" value={form.city}
              onChange={handleChange} required />
          </div>
          <div>
            <label style={lbl}>State *</label>
            <select style={inp} name="state" value={form.state}
              onChange={handleChange} required>
              <option value="">Select</option>
              {STATES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label style={lbl}>Zip *</label>
            <input style={inp} name="zip" value={form.zip}
              onChange={handleChange} required />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
          <div>
            <label style={lbl}>Telephone *</label>
            <input style={inp} name="telephone" value={form.telephone}
              onChange={handleChange} required />
          </div>
          <div>
            <label style={lbl}>Email *</label>
            <input style={inp} type="email" name="email" value={form.email}
              onChange={handleChange} required />
          </div>
        </div>

        <label style={lbl}>Date of Survey *</label>
        <input style={inp} type="date" name="date_of_survey"
          value={form.date_of_survey} onChange={handleChange} required />

        <label style={lbl}>What did you like most about the campus? *</label>
        <select style={inp} name="liked_most" value={form.liked_most}
          onChange={handleChange} required>
          <option value="">Select one</option>
          {['Students', 'Location', 'Campus', 'Atmosphere', 'Dorm Rooms', 'Sports']
            .map(o => <option key={o} value={o}>{o}</option>)}
        </select>

        <label style={lbl}>How did you become interested in this university? *</label>
        <select style={inp} name="interested_via" value={form.interested_via}
          onChange={handleChange} required>
          <option value="">Select one</option>
          {['Friends', 'Television', 'Internet', 'Other']
            .map(o => <option key={o} value={o}>{o}</option>)}
        </select>

        <label style={lbl}>Likelihood of recommending this school? *</label>
        <select style={inp} name="recommend_likelihood"
          value={form.recommend_likelihood} onChange={handleChange} required>
          <option value="">Select one</option>
          {['Very Likely', 'Likely', 'Unlikely']
            .map(o => <option key={o} value={o}>{o}</option>)}
        </select>

        <button
          type="submit"
          disabled={loading}
          style={{
            background: '#003366',
            color: 'white',
            padding: '10px 28px',
            border: 'none',
            cursor: loading ? 'not-allowed' : 'pointer',
            borderRadius: '4px',
            fontSize: '15px',
            marginTop: '8px',
            opacity: loading ? 0.7 : 1
          }}>
          {loading ? 'Submitting...' : 'Submit Survey'}
        </button>
      </form>
    </div>
  )
}