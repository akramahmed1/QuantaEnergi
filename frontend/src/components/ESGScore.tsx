import React from 'react';

interface ESGScoreProps {
  score: number;
  breakdown: {
    environmental: number;
    social: number;
    governance: number;
  };
}

const ESGScore: React.FC<ESGScoreProps> = ({ score, breakdown }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        ESG Score
      </h3>
      
      {/* Overall Score */}
      <div className="text-center mb-6">
        <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${getScoreBgColor(score)}`}>
          <span className={`text-2xl font-bold ${getScoreColor(score)}`}>
            {score}
          </span>
        </div>
        <p className="text-sm text-gray-600 mt-2">Overall ESG Score</p>
      </div>

      {/* Breakdown */}
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Environmental</span>
            <span className="font-medium">{breakdown.environmental}/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${breakdown.environmental}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Social</span>
            <span className="font-medium">{breakdown.social}/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${breakdown.social}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Governance</span>
            <span className="font-medium">{breakdown.governance}/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${breakdown.governance}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ESGScore;
