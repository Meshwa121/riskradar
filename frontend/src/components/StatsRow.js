import React from 'react';

function StatsRow({ risks, weather }) {
  const criticalRisks = risks.filter(r => r.severity === 'Critical').length;
  const weatherAlerts = weather?.alerts?.length || 0;
  const portsMonitored = weather?.summary?.total_monitored || 30;

  const stats = [
    {
      label: 'Total Risk Alerts',
      value: risks.length,
      color: 'border-purple-500',
      valueColor: 'text-white',
      sub: 'Active'
    },
    {
      label: 'Critical Risks',
      value: criticalRisks,
      color: 'border-red-500',
      valueColor: 'text-red-400',
      sub: 'Active'
    },
    {
      label: 'Ports Monitored',
      value: portsMonitored,
      color: 'border-blue-500',
      valueColor: 'text-white',
      sub: 'Operational'
    },
    {
      label: 'Weather Alerts',
      value: weatherAlerts,
      color: 'border-amber-500',
      valueColor: 'text-amber-400',
      sub: 'Detected'
    },
  ];

  return (
  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    {stats.map((stat, i) => (
      <div
        key={i}
        className="rounded-xl p-5 flex flex-col"
        style={{
          background: 'rgba(26, 26, 26, 0.8)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255,255,255,0.06)',
          borderTop: `2px solid ${
            i === 0 ? '#a78bfa' :
            i === 1 ? '#ef4444' :
            i === 2 ? '#60a5fa' :
            '#f59e0b'
          }`
        }}
      >
        <p className="text-xs text-gray-400 uppercase tracking-widest mb-3">
          {stat.label}
        </p>
        <div className="flex items-baseline gap-2 mb-3">
          <span className={`text-5xl font-bold ${stat.valueColor}`}>
            {stat.value}
          </span>
          <span className="text-xs text-gray-500">{stat.sub}</span>
        </div>
        <div className="mt-auto h-0.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full"
            style={{
              width: `${Math.min((stat.value / 30) * 100, 100)}%`,
              background: i === 0 ? '#a78bfa' : i === 1 ? '#ef4444' : i === 2 ? '#60a5fa' : '#f59e0b'
            }}
          ></div>
        </div>
      </div>
    ))}
  </div>
);
}

export default StatsRow;