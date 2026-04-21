import axios from 'axios'

const api = axios.create({
  baseURL: '/',
})

// Attach JWT to every request if present
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth
export const register = (name, email, password) =>
  api.post('/api/auth/register', { name, email, password })

export const login = (email, password) =>
  api.post('/api/auth/login', { email, password })

// Users
export const getMe = () => api.get('/api/users/me')
export const updateProfile = (data) => api.put('/api/users/me/profile', data)
export const logCall = (groupId, durationMinutes) =>
  api.post(`/api/groups/${groupId}/log-call`, { duration_minutes: durationMinutes })
export const updateGuardianEmail = (email) => api.put('/api/users/me/guardian-email', { guardian_email: email })
export const sendGuardianReport = (seniorId) => api.post(`/api/guardian/${seniorId}/send-report`)

// Groups
export const getAllGroups = () => api.get('/api/groups')
export const getMyGroups = () => api.get('/api/groups/my')
export const getSuggestedGroups = () => api.get('/api/groups/suggested')
export const getGroup = (id) => api.get(`/api/groups/${id}`)
export const createGroup = (data) => api.post('/api/groups', data)
export const joinGroup = (id) => api.post(`/api/groups/${id}/join`)
export const toggleFavorite = (id) => api.post(`/api/groups/${id}/favorite`)

// Matching
export const runMatching = () => api.post('/api/match')

// Guardian
export const getGuardianDashboard = (seniorId) =>
  api.get(`/api/guardian/${seniorId}/dashboard`)

// Google OAuth
export const getGoogleAuthorizeUrl = (scope, state, codeChallenge) =>
  api.get('/api/auth/google/authorize-url-v2', {
    params: { scope, state, code_challenge: codeChallenge },
  })

export const googleCallback = (code, codeVerifier) =>
  api.post('/api/auth/google/callback', { code, code_verifier: codeVerifier })

export const createMeetLink = (groupId) =>
  api.post(`/api/groups/${groupId}/meet-link`)

export default api
