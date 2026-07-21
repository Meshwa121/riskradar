import React from 'react';

const riskColors = {
  Critical: { text: 'text-red-400', border: 'border-red-500', badge: 'bg-red-500 text-white' },
  High: { text: 'text-amber-400', border: 'border-amber-500', badge: 'bg-amber-500 text-white' },
  Medium: { text: 'text-blue-400', border: 'border-blue-500', badge: 'bg-blue-900 text-blue-300' },
  Low: { text: 'text-green-400', border: 'border-green-700', badge: 'bg-gray-800 text-gray-400' },
};

function WeatherAlerts({ weather, loading, fullPage = false }) {
  if (loading) {
    return (
      <div className="text-center py-12 text-gray-500 text-sm">
        Checking weather at 30 ports...
      </div>
    );
  }

  const alerts = fullPage
    ? (weather?.summary?.all_locations || weather?.alerts || [])
    : (weather?.alerts || []);

  if (alerts.length === 0) {
    return (
      <div className="rounded-xl p-8 text-center"
        style={{ background: 'rgba(26,26,26,0.8)', border: '1px solid rgba(255,255,255,0.06)' }}>
        <div className="text-green-400 text-sm font-medium">
          ✅ No elevated weather risks at any monitored location
        </div>
        <div className="text-gray-500 text-xs mt-2">
          {weather?.summary?.total_monitored || 30} ports and chokepoints monitored
        </div>
      </div>
    );
  }

  if (fullPage) {
    return (
      <div>
        <div className="flex items-center gap-2 mb-6 px-4 py-2 rounded-lg w-fit"
          style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
          <span className="w-2 h-2 rounded-full bg-green-400"></span>
          <span className="text-xs text-gray-400">System Status: Operational</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {alerts.map((alert, index) => {
            const colors = riskColors[alert.current_risk] || riskColors.Low;
            return (
              <div key={index} className={`rounded-xl p-5 border ${colors.border} border-opacity-30`}
                style={{ background: 'rgba(26,26,26,0.8)', backdropFilter: 'blur(12px)' }}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-white font-semibold text-base">{alert.location}</p>
                    <p className="text-gray-500 text-xs mt-0.5">{alert.region}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${colors.badge}`}>
                    {alert.current_risk?.toUpperCase()}
                  </span>
                </div>

                <div className="mb-4">
                  <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Primary Threat</p>
                  <p className={`text-sm font-medium ${colors.text}`}>{alert.condition}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Wind Speed</p>
                    <p className="text-sm text-white font-medium">{alert.wind_kph} km/h</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Visibility</p>
                    <p className="text-sm text-white font-medium">{alert.visibility_km} km</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Temperature</p>
                    <p className="text-sm text-white font-medium">{alert.temp_c}°C</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Checked</p>
                    <p className="text-xs text-gray-400">{alert.checked_at?.split(' ')[1]}</p>
                  </div>
                </div>

                {alert.upcoming_risks?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-800">
                    <p className="text-xs text-amber-400">
                      ⚠️ {alert.upcoming_risks.length} high risk period(s) in next 3 days
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Dashboard compact view — bigger fonts
  return (
    <div className="flex flex-col gap-3">
      {alerts.map((alert, index) => {
        const colors = riskColors[alert.current_risk] || riskColors.Low;
        return (
          <div key={index} className="rounded-xl p-4"
            style={{ background: 'rgba(26,26,26,0.8)', border: '1px solid rgba(255,255,255,0.06)' }}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-base font-semibold text-white">{alert.location}</span>
              <span className={`text-sm font-medium ${colors.text}`}>{alert.current_risk} Risk</span>
            </div>

            <div className="mb-2">
              <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Primary Threat</p>
              <p className={`text-sm font-medium ${colors.text}`}>{alert.condition}</p>
            </div>

            <div className="grid grid-cols-2 gap-2 mt-2">
              <div className="text-sm text-gray-400">💨 {alert.wind_kph} km/h</div>
              <div className="text-sm text-gray-400">👁 {alert.visibility_km} km visibility</div>
            </div>

            {alert.upcoming_risks?.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-800">
                <p className="text-sm text-amber-400">
                  ⚠️ {alert.upcoming_risks.length} high risk period(s) in next 3 days
                </p>
              </div>
            )}

            <div className="text-xs text-gray-500 mt-2">
              {alert.region} • Checked {alert.checked_at}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default WeatherAlerts;