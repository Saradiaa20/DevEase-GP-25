import React, { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { getProjects, createProject } from '../services/api'
import { FolderIcon, PlusIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

function Projects() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newProject, setNewProject] = useState({ name: '', description: '' })

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const data = await getProjects()
      setProjects(data || [])
    } catch (error) {
      console.error('Failed to load projects:', error)
      // Use mock data if API fails
      setProjects([
        { id: 1, name: 'Project Alpha', description: 'Main codebase', created_at: '2026-01-09' },
        { id: 2, name: 'Project Beta', description: 'Experimental features', created_at: '2026-01-08' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()
    try {
      const project = await createProject(newProject)
      setProjects([...projects, project])
      setShowCreateModal(false)
      setNewProject({ name: '', description: '' })
    } catch (error) {
      console.error('Failed to create project:', error)
      alert('Failed to create project. Make sure you are logged in as Team Lead.')
    }
  }

  return (
    <Layout>
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Projects</h1>
            <p className="text-gray-400">Manage your code analysis projects</p>
          </div>
          {/* New Project button hidden - feature not fully implemented
          <button
            onClick={() => setShowCreateModal(true)}
            className="cyber-btn-primary flex items-center space-x-2"
          >
            <PlusIcon className="w-5 h-5" />
            <span>New Project</span>
          </button>
          */}
        </div>

        {loading ? (
          <div className="cyber-card text-center py-12">
            <div className="text-gray-400">Loading projects...</div>
          </div>
        ) : projects.length === 0 ? (
          <div className="cyber-card text-center py-12">
            <FolderIcon className="w-16 h-16 mx-auto mb-4 text-gray-500" />
            <p className="text-gray-400">No projects available</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Link
                key={project.id}
                to={`/projects/${project.id}`}
                className="cyber-card hover:border-cyan-500/50 transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <FolderIcon className="w-8 h-8 text-cyan-400 group-hover:text-cyan-300" />
                  <span className="text-xs text-gray-500">
                    {new Date(project.created_at || project.createdAt).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-cyan-400 transition-colors">
                  {project.name}
                </h3>
                <p className="text-gray-400 text-sm">{project.description || 'No description'}</p>
                <div className="mt-4 pt-4 border-t border-[#2d3748] flex items-center justify-between">
                  <span className="text-xs text-gray-500">View Details</span>
                  <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Create Project Modal - Hidden for now (feature not fully implemented)
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="cyber-card max-w-md w-full mx-4">
              <h2 className="text-2xl font-bold text-white mb-4">Create New Project</h2>
              <form onSubmit={handleCreateProject} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Project Name
                  </label>
                  <input
                    type="text"
                    required
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="w-full px-4 py-2 bg-[#202835] border border-[#2d3748] rounded-lg text-white focus:outline-none focus:border-cyan-500"
                    placeholder="Enter project name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    className="w-full px-4 py-2 bg-[#202835] border border-[#2d3748] rounded-lg text-white focus:outline-none focus:border-cyan-500"
                    rows="3"
                    placeholder="Enter project description"
                  />
                </div>
                <div className="flex space-x-3">
                  <button
                    type="submit"
                    className="flex-1 cyber-btn-primary"
                  >
                    Create Project
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 bg-[#202835] border border-[#2d3748] text-gray-300 rounded-lg hover:bg-[#1a2332]"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        */}
      </div>
    </Layout>
  )
}

export default Projects
