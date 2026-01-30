import React from 'react'
import { Link } from 'react-router-dom'
import {
  CodeBracketIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  StarIcon,
} from '@heroicons/react/24/outline'

function LandingPage() {
  return (
    <div className="min-h-screen cyber-bg relative overflow-hidden">
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <header className="px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center glow-cyan">
                <span className="text-white font-bold text-2xl">D</span>
              </div>
              <div>
                <span className="text-2xl font-bold text-white">DevEase</span>
                <span className="text-lg text-cyan-400 ml-1">AI</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
              >
                Login
              </Link>
              <Link
                to="/dashboard"
                className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg font-medium hover:shadow-lg hover:shadow-cyan-500/50 transition-all"
              >
                Get Started
              </Link>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-6 py-20 text-center">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
            Code Complexity
            <br />
            Analysis Platform
          </h1>
          <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Detect code smells, calculate technical debt, predict complexity, and improve code quality
            with AI-powered analysis. Built for developers who care about code quality.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4 mb-20">
            <Link
              to="/dashboard"
              className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg font-semibold text-lg hover:shadow-2xl hover:shadow-cyan-500/50 transition-all transform hover:scale-105"
            >
              Start Analyzing
            </Link>
            <Link
              to="/dashboard"
              className="px-8 py-4 bg-[#1a2332] border border-cyan-500/50 text-cyan-400 rounded-lg font-semibold text-lg hover:bg-[#202835] hover:border-cyan-500 transition-all"
            >
              View Demo
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-20">
            <FeatureCard
              icon={CodeBracketIcon}
              title="Code Smell Detection"
              description="Automatically detect code smells across multiple languages"
              color="cyan"
            />
            <FeatureCard
              icon={ChartBarIcon}
              title="Technical Debt"
              description="Calculate and track technical debt with actionable insights"
              color="blue"
            />
            <FeatureCard
              icon={StarIcon}
              title="ML Complexity"
              description="AI-powered complexity prediction using machine learning"
              color="purple"
            />
            <FeatureCard
              icon={ShieldCheckIcon}
              title="Quality Metrics"
              description="Comprehensive code quality scoring and recommendations"
              color="green"
            />
          </div>
        </section>

        {/* Stats Section */}
        <section className="max-w-7xl mx-auto px-6 py-20">
          <div className="grid md:grid-cols-4 gap-8">
            <StatCard number="100+" label="Languages Supported" />
            <StatCard number="50K+" label="Files Analyzed" />
            <StatCard number="95%" label="Accuracy Rate" />
            <StatCard number="24/7" label="Available" />
          </div>
        </section>
      </div>
    </div>
  )
}

function FeatureCard({ icon: Icon, title, description, color }) {
  const colorClasses = {
    cyan: 'text-cyan-400 bg-cyan-400/10',
    blue: 'text-blue-400 bg-blue-400/10',
    purple: 'text-purple-400 bg-purple-400/10',
    green: 'text-green-400 bg-green-400/10',
  }

  return (
    <div className="cyber-card hover:border-cyan-500/50">
      <div className={`w-12 h-12 ${colorClasses[color]} rounded-lg flex items-center justify-center mb-4`}>
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  )
}

function StatCard({ number, label }) {
  return (
    <div className="text-center">
      <div className="text-4xl font-bold text-cyan-400 mb-2">{number}</div>
      <div className="text-gray-400">{label}</div>
    </div>
  )
}

export default LandingPage
