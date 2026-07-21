import React, { useState } from 'react';
import axios from 'axios';

function ShipmentTracker({ apiBase }) {
  const [form, setForm] = useState({
    origin: '',
    destination: '',
    expected_delivery: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!form.origin || !form.destination || !form.expected_delivery) {
      setError('Please fill in all fields');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await axios.post(`${apiBase}/shipment`, form);
      setResult(response.data);
    } catch (err) {
      setError('Error analyzing shipment. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white mb-1">Shipment Risk Advisory</h1>
        <p className="text-gray-400 text-sm">Enter your shipment details to get a risk assessment and delay estimate based on live data.</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Routes Monitored', value: '8', sub: 'Active', color: '#a78bfa' },
          { label: 'Chokepoints Tracked', value: '10', sub: 'Global', color: '#f59e0b' },
          { label: 'Ports Covered', value: '20', sub: 'Worldwide', color: '#60a5fa' },
          { label: 'Avg Transit Days', value: '18', sub: 'Est.', color: '#4ade80' },
        ].map((stat, i) => (
          <div key={i} className="rounded-xl p-5"
            style={{
              background: 'rgba(26,26,26,0.8)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderTop: `2px solid ${stat.color}`
            }}>
            <p className="text-xs text-gray-400 uppercase tracking-widest mb-2">{stat.label}</p>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white">{stat.value}</span>
              <span className="text-xs text-gray-500">{stat.sub}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="rounded-xl p-6"
          style={{ background: 'rgba(26,26,26,0.8)', border: '1px solid rgba(255,255,255,0.06)' }}>
          <h2 className="text-lg font-semibold text-white mb-1">Route Risk Analysis</h2>
          <p className="text-gray-500 text-sm mb-6">Get AI-powered delay estimates based on live weather and historical disruption data</p>

          <div className="flex flex-col gap-4">
            <div>
              <label className="text-xs text-gray-400 uppercase tracking-widest mb-2 block">
                Seller / Origin Location
              </label>
              <input
                type="text"
                placeholder="e.g. Shanghai, China"
                value={form.origin}
                onChange={e => setForm({...form, origin: e.target.value})}
                className="w-full rounded-lg px-4 py-3 text-white text-sm placeholder-gray-600 outline-none transition-colors"
                style={{
                  background: 'rgba(15,15,15,0.8)',
                  border: '1px solid rgba(255,255,255,0.08)'
                }}
                onFocus={e => e.target.style.borderColor = '#a78bfa'}
                onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.08)'}
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 uppercase tracking-widest mb-2 block">
                Your Location / Destination
              </label>
              <input
                type="text"
                placeholder="e.g. Rotterdam, Netherlands"
                value={form.destination}
                onChange={e => setForm({...form, destination: e.target.value})}
                className="w-full rounded-lg px-4 py-3 text-white text-sm placeholder-gray-600 outline-none transition-colors"
                style={{
                  background: 'rgba(15,15,15,0.8)',
                  border: '1px solid rgba(255,255,255,0.08)'
                }}
                onFocus={e => e.target.style.borderColor = '#a78bfa'}
                onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.08)'}
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 uppercase tracking-widest mb-2 block">
                Expected Delivery Date
              </label>
              <input
                type="date"
                value={form.expected_delivery}
                onChange={e => setForm({...form, expected_delivery: e.target.value})}
                className="w-full rounded-lg px-4 py-3 text-white text-sm outline-none"
                style={{
                  background: 'rgba(15,15,15,0.8)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  colorScheme: 'dark'
                }}
              />
            </div>

            {error && (
              <p className="text-red-400 text-sm">{error}</p>
            )}

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full py-3 rounded-lg text-sm font-semibold transition-all disabled:opacity-50"
              style={{ background: '#a78bfa', color: '#1a0f2e' }}
            >
              {loading ? 'Analyzing route...' : 'Get Risk Advisory'}
            </button>
          </div>
        </div>

        {/* Result */}
        <div>
          {!result && !loading && (
            <div className="rounded-xl p-8 h-full flex flex-col items-center justify-center text-center"
              style={{ background: 'rgba(26,26,26,0.4)', border: '1px dashed rgba(255,255,255,0.08)' }}>
              <p className="text-4xl mb-4">📦</p>
              <p className="text-gray-400 text-sm font-medium">Enter shipment details to get risk advisory</p>
              <p className="text-gray-600 text-xs mt-2">Powered by live weather + ChromaDB RAG analysis</p>
            </div>
          )}

          {loading && (
            <div className="rounded-xl p-8 h-full flex flex-col items-center justify-center text-center"
              style={{ background: 'rgba(26,26,26,0.4)', border: '1px solid rgba(255,255,255,0.06)' }}>
              <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-gray-400 text-sm">Analyzing route risks...</p>
            </div>
          )}

          {result && (
            <div className="rounded-xl p-6"
              style={{ background: 'rgba(26,26,26,0.8)', border: '1px solid rgba(255,255,255,0.06)' }}>
              <h3 className="text-lg font-semibold text-white mb-4">Risk Advisory Result</h3>

              {/* Key metrics */}
              <div className="grid grid-cols-2 gap-3 mb-5">
                <div className="rounded-lg p-3"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Route</p>
                  <p className="text-sm text-white font-medium">{result.route_description}</p>
                </div>
                <div className="rounded-lg p-3"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Estimated Delay</p>
                  <p className={`text-lg font-bold ${result.estimated_delay_days > 0 ? 'text-amber-400' : 'text-green-400'}`}>
                    {result.estimated_delay_days > 0 ? `+${result.estimated_delay_days} days` : 'No delay'}
                  </p>
                </div>
                <div className="rounded-lg p-3"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Original Delivery</p>
                  <p className="text-sm text-white font-medium">{result.original_delivery}</p>
                </div>
                <div className="rounded-lg p-3"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Revised Delivery</p>
                  <p className={`text-sm font-bold ${result.estimated_delay_days > 0 ? 'text-amber-400' : 'text-green-400'}`}>
                    {result.revised_delivery}
                  </p>
                </div>
              </div>

              {/* Delay Reasons */}
              {result.delay_reasons?.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs text-gray-500 uppercase tracking-widest mb-2">Delay Reasons</p>
                  {result.delay_reasons.map((reason, i) => (
                    <div key={i} className="flex items-start gap-2 mb-1.5">
                      <span className="text-amber-400 mt-0.5 text-xs">→</span>
                      <span className="text-sm text-gray-300">{reason}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Affected Chokepoints */}
              {result.affected_chokepoints?.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs text-gray-500 uppercase tracking-widest mb-2">Affected Chokepoints</p>
                  <div className="flex flex-wrap gap-2">
                    {result.affected_chokepoints.map((cp, i) => (
                      <span key={i} className="text-xs px-2 py-1 rounded-full"
                        style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}>
                        {cp}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Rerouting */}
              {result.alternate_route && result.estimated_delay_days > 2 && (
                <div className="rounded-lg p-3 mt-3"
                  style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)' }}>
                  <p className="text-xs text-amber-400 font-semibold mb-1">⚠️ Rerouting Suggestion</p>
                  <p className="text-xs text-amber-300">Consider: {result.alternate_route}</p>
                  <p className="text-xs text-amber-400 mt-1">+{result.alternate_extra_days} days extra but avoids current disruptions</p>
                </div>
              )}

              {/* Confidence */}
              <div className="mt-4 pt-3 border-t border-gray-800">
                <p className="text-xs text-gray-600">
                  Confidence: {result.confidence} • Based on live weather + ChromaDB RAG analysis
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ShipmentTracker;