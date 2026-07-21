import React from 'react';

const severityConfig = {
  Critical: {
    badge: 'bg-red-900 bg-opacity-30 text-red-400 border border-red-500 border-opacity-30',
    border: 'border-l-red-500',
    glow: '0 0 15px rgba(239,68,68,0.1)'
  },
  High: {
    badge: 'bg-amber-900 bg-opacity-30 text-amber-400 border border-amber-500 border-opacity-30',
    border: 'border-l-amber-500',
    glow: '0 0 15px rgba(245,158,11,0.1)'
  },
  Medium: {
    badge: 'bg-blue-900 bg-opacity-30 text-blue-400 border border-blue-500 border-opacity-30',
    border: 'border-l-blue-500',
    glow: '0 0 15px rgba(59,130,246,0.1)'
  },
  Low: {
    badge: 'bg-gray-800 text-gray-400 border border-gray-700',
    border: 'border-l-gray-600',
    glow: 'none'
  },
};

function RiskFeed({ risks, loading }) {
  if (loading) {
    return (
      <div className="text-center py-12 text-gray-500 text-sm">
        Scanning live news...
      </div>
    );
  }

  if (risks.length === 0) {
    return (
      <div className="rounded-xl p-8 text-center"
        style={{ background: 'rgba(26,26,26,0.8)', border: '1px solid rgba(255,255,255,0.06)' }}>
        <p className="text-2xl mb-3">📡</p>
        <p className="text-gray-400 text-sm font-medium">Click Scan News to fetch live supply chain risk alerts</p>
        <p className="text-gray-600 text-xs mt-2">Powered by NewsAPI + LangGraph pipeline</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {risks.map(function(risk, index) {
        const config = severityConfig[risk.severity] || severityConfig.Low;
        return (
          <div
            key={index}
            className="rounded-xl p-4"
            style={{
              background: 'rgba(26,26,26,0.8)',
              borderTop: '1px solid rgba(255,255,255,0.06)',
              borderRight: '1px solid rgba(255,255,255,0.06)',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
              borderLeft: `4px solid ${
                 risk.severity === 'Critical' ? '#ef4444' :
                 risk.severity === 'High' ? '#f59e0b' :
                 risk.severity === 'Medium' ? '#3b82f6' :
                 '#6b7280'
             }`,
              boxShadow: config.glow
           }}
          >
            {/* Header */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <span className="text-sm font-semibold text-white leading-tight">
                {risk.title}
              </span>
              <span className={`text-xs px-2 py-1 rounded-full flex-shrink-0 ${config.badge}`}>
                {risk.severity}
              </span>
            </div>

            {/* Summary */}
            <p className="text-xs text-gray-400 leading-relaxed mb-3">
              {risk.alert_summary}
            </p>

            {/* Routes + Industries */}
            {(risk.affected_routes?.length > 0 || risk.affected_industries?.length > 0) && (
              <div className="flex flex-wrap gap-1 mb-3">
                {risk.affected_routes?.slice(0, 2).map((route, i) => (
                  <span key={i} className="text-xs px-2 py-0.5 rounded"
                    style={{ background: 'rgba(255,255,255,0.05)', color: '#9ca3af' }}>
                    {route}
                  </span>
                ))}
                {risk.affected_industries?.slice(0, 2).map((industry, i) => (
                  <span key={i} className="text-xs px-2 py-0.5 rounded"
                    style={{ background: 'rgba(167,139,250,0.1)', color: '#a78bfa' }}>
                    {industry}
                  </span>
                ))}
              </div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between mt-2 pt-2"
              style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
              <span className="text-xs text-gray-500">{risk.source}</span>
              
                <a href={risk.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-purple-400 hover:text-purple-300 underline"
              >
                Read more
              </a>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default RiskFeed;