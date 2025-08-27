import React from 'react'
// import { motion } from 'framer-motion'
import {
  // LeafIcon, 
  HeartIcon, 
  ShieldCheckIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

const ESGScore: React.FC = () => {
  const esgData = {
    overall: 78,
    environmental: 82,
    social: 75,
    governance: 79,
    breakdown: {
      carbonEmissions: 85,
      renewableEnergy: 78,
      waterManagement: 80,
      laborRights: 72,
      communityImpact: 78,
      boardDiversity: 81,
      transparency: 76,
      antiCorruption: 82
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success-600'
    if (score >= 60) return 'text-warning-600'
    return 'text-danger-600'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-success-100'
    if (score >= 60) return 'bg-warning-100'
    return 'bg-danger-100'
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-secondary-900">ESG Score</h2>
        <div className="flex items-center space-x-2">
          <LeafIcon className="w-5 h-5 text-success-500" />
          <span className="text-sm text-success-600 font-medium">Sustainability</span>
        </div>
      </div>
      
      {/* Overall Score */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br from-success-100 to-success-200 border-4 border-success-300 mb-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-success-700">{esgData.overall}</div>
            <div className="text-sm text-success-600">Overall</div>
          </div>
        </div>
        <div className="text-lg font-medium text-secondary-900">Good ESG Rating</div>
        <div className="text-sm text-secondary-600">Above industry average</div>
      </div>

      {/* Pillar Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="text-center">
          <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${getScoreBg(esgData.environmental)} mb-3`}>
            <LeafIcon className="w-8 h-8 text-success-600" />
          </div>
          <div className={`text-2xl font-bold ${getScoreColor(esgData.environmental)} mb-1`}>
            {esgData.environmental}
          </div>
          <div className="text-sm text-secondary-600">Environmental</div>
        </div>
        
        <div className="text-center">
          <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${getScoreBg(esgData.social)} mb-3`}>
            <HeartIcon className="w-8 h-8 text-primary-600" />
          </div>
          <div className={`text-2xl font-bold ${getScoreColor(esgData.social)} mb-1`}>
            {esgData.social}
          </div>
          <div className="text-sm text-secondary-600">Social</div>
        </div>
        
        <div className="text-center">
          <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${getScoreBg(esgData.governance)} mb-3`}>
            <ShieldCheckIcon className="w-8 h-8 text-blue-600" />
          </div>
          <div className={`text-2xl font-bold ${getScoreColor(esgData.governance)} mb-1`}>
            {esgData.governance}
          </div>
          <div className="text-sm text-secondary-600">Governance</div>
        </div>
      </div>

      {/* Detailed Breakdown */}
      <div>
        <h3 className="text-lg font-medium text-secondary-900 mb-4">Detailed Breakdown</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(esgData.breakdown).map(([key, score]) => (
            <div key={key} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <ChartBarIcon className="w-4 h-4 text-secondary-500" />
                <span className="text-sm font-medium text-secondary-700 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </span>
              </div>
              <div className={`text-lg font-bold ${getScoreColor(score)}`}>
                {score}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ESG Insights */}
      <div className="mt-6 p-4 bg-success-50 rounded-lg border border-success-200">
        <div className="flex items-center space-x-2 mb-2">
          <LeafIcon className="w-5 h-5 text-success-500" />
          <span className="text-sm font-medium text-success-700">ESG Insights</span>
        </div>
        <p className="text-sm text-success-700">
          Strong environmental performance with excellent carbon emissions management. 
          Social score shows room for improvement in labor rights and community impact. 
          Governance practices are solid with good board diversity and transparency.
        </p>
      </div>
    </div>
  )
}

export default ESGScore
