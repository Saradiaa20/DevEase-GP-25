import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { getProject } from '../services/api'
import AnalysisResults from '../components/AnalysisResults'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

function ProjectDetails() {
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProject()
  }, [id])

  const loadProject = async () => {
    try {
      const data = await getProject(id)
      setProject(data)
      // In production, fetch analyses for this project
      setAnalyses([
        {
          id: 1,
          file: 'main.py',
          date: '2026-01-09',
          analysisData: null, // Would contain full analysis
        },
      ])
    } catch (error) {
      console.error('Failed to load project:', error)
      // Mock data
      setProject({
        id: parseInt(id),
        name: 'Project Alpha',
        description: 'Main codebase project',
        created_at: '2026-01-09',
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="p-6">
          <div className="cyber-card text-center py-12">
            <div className="text-gray-400">Loading project...</div>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <Link
            to="/projects"
            className="p-2 hover:bg-[#202835] rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="w-5 h-5 text-gray-400" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-white">{project?.name}</h1>
            <p className="text-gray-400">{project?.description}</p>
          </div>
        </div>

        {/* Project Info */}
        <div className="cyber-card">
          <h2 className="text-xl font-semibold text-white mb-4">Project Information</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <span className="text-gray-400 text-sm">Created</span>
              <p className="text-white">
                {new Date(project?.created_at || project?.createdAt).toLocaleDateString()}
              </p>
            </div>
            <div>
              <span className="text-gray-400 text-sm">Total Analyses</span>
              <p className="text-white">{analyses.length}</p>
            </div>
          </div>
        </div>

        {/* Analyses List */}
        <div className="cyber-card">
          <h2 className="text-xl font-semibold text-white mb-4">Analyses</h2>
          {analyses.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No analyses yet. Upload files to start analyzing.
            </div>
          ) : (
            <div className="space-y-4">
              {analyses.map((analysis) => (
                <div
                  key={analysis.id}
                  className="p-4 bg-[#202835] rounded-lg border border-[#2d3748] hover:border-cyan-500/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-medium">{analysis.file}</h3>
                      <p className="text-gray-400 text-sm">{analysis.date}</p>
                    </div>
                    <button className="text-cyan-400 hover:text-cyan-300 text-sm">
                      View Details
                    </button>
                  </div>
                  {analysis.analysisData && (
                    <div className="mt-4">
                      <AnalysisResults data={analysis.analysisData} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default ProjectDetails
