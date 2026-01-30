import React, { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { getCurrentUser } from '../services/api'
import { UserIcon, EnvelopeIcon, ShieldCheckIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'

function Profile() {
  const [user, setUser] = useState(null)
  const [editingField, setEditingField] = useState(null)
  const [editValue, setEditValue] = useState('')
  const [saveMessage, setSaveMessage] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)
  const [stats, setStats] = useState({
    totalAnalyses: 12,
    projectsCreated: 3,
    avgQualityScore: 85.5,
  })

  // Email validation regex
  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  // Username validation (alphanumeric, underscore, 3-20 chars)
  const isValidUsername = (username) => {
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
    return usernameRegex.test(username)
  }

  useEffect(() => {
    // Try to get saved profile from localStorage first
    const savedProfile = localStorage.getItem('userProfile')
    if (savedProfile) {
      setUser(JSON.parse(savedProfile))
      return
    }

    const currentUser = getCurrentUser()
    if (currentUser) {
      setUser({
        username: currentUser.sub || 'developer',
        email: currentUser.email || 'user@example.com',
        role: currentUser.role || 'developer',
      })
    } else {
      // Mock user for demo
      setUser({
        username: 'developer',
        email: 'developer@example.com',
        role: 'developer',
      })
    }
  }, [])

  const handleEdit = (field, currentValue) => {
    setEditingField(field)
    setEditValue(currentValue)
    setErrorMessage(null)
  }

  const handleSave = (field) => {
    const trimmedValue = editValue.trim()
    
    // Empty field validation
    if (!trimmedValue) {
      setErrorMessage(`${field.charAt(0).toUpperCase() + field.slice(1)} cannot be empty`)
      return
    }

    // Field-specific validation
    if (field === 'email') {
      if (!isValidEmail(trimmedValue)) {
        setErrorMessage('Please enter a valid email address (e.g., user@example.com)')
        return
      }
    }

    if (field === 'username') {
      if (!isValidUsername(trimmedValue)) {
        setErrorMessage('Username must be 3-20 characters and contain only letters, numbers, and underscores')
        return
      }
    }

    const updatedUser = {
      ...user,
      [field]: trimmedValue
    }
    
    setUser(updatedUser)
    localStorage.setItem('userProfile', JSON.stringify(updatedUser))
    setEditingField(null)
    setEditValue('')
    setErrorMessage(null)
    
    // Show save confirmation
    setSaveMessage(`${field.charAt(0).toUpperCase() + field.slice(1)} updated successfully!`)
    setTimeout(() => setSaveMessage(null), 3000)
  }

  const handleCancel = () => {
    setEditingField(null)
    setEditValue('')
    setErrorMessage(null)
  }

  const handleKeyDown = (e, field) => {
    if (e.key === 'Enter') {
      handleSave(field)
    } else if (e.key === 'Escape') {
      handleCancel()
    }
  }

  const getRoleColor = (role) => {
    return role === 'team_lead' ? 'text-purple-400' : 'text-blue-400'
  }

  return (
    <Layout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Profile</h1>
          <p className="text-gray-400">Manage your account settings</p>
        </div>

        {/* Save Confirmation Message */}
        {saveMessage && (
          <div className="bg-green-500/20 border border-green-500/50 text-green-400 px-4 py-3 rounded-lg flex items-center space-x-2">
            <CheckIcon className="w-5 h-5" />
            <span>{saveMessage}</span>
          </div>
        )}

        {/* Error Message */}
        {errorMessage && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg flex items-center space-x-2">
            <XMarkIcon className="w-5 h-5" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Profile Card */}
        <div className="cyber-card">
          <div className="flex items-center space-x-6 mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-full flex items-center justify-center">
              <UserIcon className="w-10 h-10 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{user?.username}</h2>
              <p className="text-gray-400">{user?.email}</p>
              <span className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-medium bg-[#202835] ${getRoleColor(user?.role)}`}>
                {user?.role === 'team_lead' ? 'Team Lead' : 'Developer'}
              </span>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-4 pt-6 border-t border-[#2d3748]">
            <StatItem label="Total Analyses" value={stats.totalAnalyses} />
            <StatItem label="Projects" value={stats.projectsCreated} />
            <StatItem label="Avg Quality" value={`${stats.avgQualityScore}%`} />
          </div>
        </div>

        {/* Account Information */}
        <div className="cyber-card">
          <h2 className="text-xl font-semibold text-white mb-4">Account Information</h2>
          <div className="space-y-4">
            {/* Username Field */}
            <div className="flex items-center justify-between p-4 bg-[#202835] rounded-lg border border-[#2d3748]">
              <div className="flex items-center space-x-3 flex-1">
                <UserIcon className="w-5 h-5 text-cyan-400" />
                <div className="flex-1">
                  <div className="text-sm text-gray-400">Username</div>
                  {editingField === 'username' ? (
                    <input
                      type="text"
                      value={editValue}
                      onChange={(e) => {
                        setEditValue(e.target.value)
                        setErrorMessage(null)
                      }}
                      onKeyDown={(e) => handleKeyDown(e, 'username')}
                      className={`w-full bg-[#1a2332] border rounded px-3 py-1 text-white focus:outline-none focus:ring-2 ${
                        errorMessage ? 'border-red-500 focus:ring-red-500' : 'border-cyan-500 focus:ring-cyan-500'
                      }`}
                      autoFocus
                      placeholder="Enter username (3-20 chars)"
                    />
                  ) : (
                    <div className="text-white">{user?.username}</div>
                  )}
                </div>
              </div>
              {editingField === 'username' ? (
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleSave('username')}
                    className="p-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors"
                    title="Save"
                  >
                    <CheckIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleCancel}
                    className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                    title="Cancel"
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => handleEdit('username', user?.username)}
                  className="text-cyan-400 hover:text-cyan-300 text-sm"
                >
                  Edit
                </button>
              )}
            </div>

            {/* Email Field */}
            <div className="flex items-center justify-between p-4 bg-[#202835] rounded-lg border border-[#2d3748]">
              <div className="flex items-center space-x-3 flex-1">
                <EnvelopeIcon className="w-5 h-5 text-cyan-400" />
                <div className="flex-1">
                  <div className="text-sm text-gray-400">Email</div>
                  {editingField === 'email' ? (
                    <input
                      type="email"
                      value={editValue}
                      onChange={(e) => {
                        setEditValue(e.target.value)
                        setErrorMessage(null)
                      }}
                      onKeyDown={(e) => handleKeyDown(e, 'email')}
                      className={`w-full bg-[#1a2332] border rounded px-3 py-1 text-white focus:outline-none focus:ring-2 ${
                        errorMessage ? 'border-red-500 focus:ring-red-500' : 'border-cyan-500 focus:ring-cyan-500'
                      }`}
                      placeholder="Enter email (e.g., user@example.com)"
                      autoFocus
                    />
                  ) : (
                    <div className="text-white">{user?.email}</div>
                  )}
                </div>
              </div>
              {editingField === 'email' ? (
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleSave('email')}
                    className="p-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors"
                    title="Save"
                  >
                    <CheckIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleCancel}
                    className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                    title="Cancel"
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => handleEdit('email', user?.email)}
                  className="text-cyan-400 hover:text-cyan-300 text-sm"
                >
                  Edit
                </button>
              )}
            </div>

            {/* Role Field (not editable) */}
            <div className="flex items-center justify-between p-4 bg-[#202835] rounded-lg border border-[#2d3748]">
              <div className="flex items-center space-x-3">
                <ShieldCheckIcon className="w-5 h-5 text-cyan-400" />
                <div>
                  <div className="text-sm text-gray-400">Role</div>
                  <div className="text-white">{user?.role === 'team_lead' ? 'Team Lead' : 'Developer'}</div>
                </div>
              </div>
              <span className="text-gray-500 text-sm">Contact admin to change</span>
            </div>
          </div>
        </div>

        {/* Preferences - Hidden for now (toggles not functional)
        <div className="cyber-card">
          <h2 className="text-xl font-semibold text-white mb-4">Preferences</h2>
          <div className="space-y-3">
            <PreferenceItem label="Email Notifications" enabled />
            <PreferenceItem label="Analysis Reports" enabled />
            <PreferenceItem label="Project Updates" enabled={false} />
          </div>
        </div>
        */}
      </div>
    </Layout>
  )
}

function StatItem({ label, value }) {
  return (
    <div className="text-center">
      <div className="text-2xl font-bold text-cyan-400 mb-1">{value}</div>
      <div className="text-sm text-gray-400">{label}</div>
    </div>
  )
}

function PreferenceItem({ label, enabled }) {
  return (
    <div className="flex items-center justify-between p-4 bg-[#202835] rounded-lg border border-[#2d3748]">
      <span className="text-white">{label}</span>
      <button
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          enabled ? 'bg-cyan-500' : 'bg-gray-600'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            enabled ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  )
}

export default Profile
