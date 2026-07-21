import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import StatsRow from './components/StatsRow';
import RiskFeed from './components/RiskFeed';
import WeatherAlerts from './components/WeatherAlerts';
import ShipmentTracker from './components/ShipmentTracker';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [risks, setRisks] = useState([]);
  const [weather, setWeather] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [weatherLoading, setWeatherLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setWeatherLoading(true);
    try {
      const weatherRes = await axios.get(`${API_BASE}/weather`);
      setWeather(weatherRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setWeatherLoading(false);
  };

  const fetchRisks = async () => {
    setLoading(true);
    try {
      const risksRes = await axios.get(`${API_BASE}/risks`);
      setRisks(risksRes.data.risks || []);
    } catch (error) {
      console.error('Error fetching risks:', error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <Navbar />

      <div className="flex pt-16">

        {/* Sidebar */}
        <aside
          className="hidden xl:flex flex-col fixed left-0 top-16 h-[calc(100vh-4rem)] w-56 py-6 px-3"
          style={{
            background: 'rgba(17, 17, 17, 0.85)',
            backdropFilter: 'blur(20px)',
            borderRight: '1px solid rgba(255,255,255,0.05)',
          }}
        >
          <div
            className="flex items-center gap-3 p-3 mb-6 rounded-xl"
            style={{ background: 'rgba(255,255,255,0.04)' }}
          >
            <div className="w-9 h-9 rounded-full bg-purple-500 bg-opacity-20 border border-purple-500 border-opacity-30 flex items-center justify-center">
              <span className="text-purple-400 text-xs">👤</span>
            </div>
            <div>
              <p className="text-xs font-semibold text-purple-400">Risk Management</p>
              <p className="text-xs text-gray-500">Operational Focus</p>
            </div>
          </div>

          <div className="flex flex-col gap-1">
            {[
              { icon: '🌐', label: 'Global View', tab: 'dashboard' },
              { icon: '🌤️', label: 'Weather', tab: 'weather' },
              { icon: '📦', label: 'Shipment Tracker', tab: 'shipment' },
              { icon: 'ℹ️', label: 'About', tab: 'about' },
            ].map((item) => (
              <div
                key={item.label}
                onClick={() => setActiveTab(item.tab)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all text-sm ${
                  activeTab === item.tab
                    ? 'bg-purple-500 bg-opacity-10 text-purple-400 font-semibold'
                    : 'text-gray-400 hover:bg-white hover:bg-opacity-5 hover:text-white'
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </div>
            ))}
          </div>

          <div className="mt-auto px-2">
            <div
              className="rounded-xl p-3 text-center"
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.05)',
              }}
            >
              <p className="text-xs text-green-400 font-medium">● System Operational</p>
              <p className="text-xs text-gray-600 mt-1">30 ports monitored</p>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 xl:ml-56 px-6 md:px-10 py-8 pb-24 xl:pb-8">

          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <>
              <div className="mb-6">
                <h1 className="text-2xl font-semibold text-white mb-1">Operations Command</h1>
                <p className="text-gray-400 text-sm">
                  Global logistics risk landscape across primary trade corridors.
                </p>
              </div>
              <StatsRow risks={risks} weather={weather} />
              <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-medium text-gray-100">Live Risk Alerts</h2>
                    <button
                      onClick={fetchRisks}
                      disabled={loading}
                      className="bg-purple-600 hover:bg-purple-700 text-white text-sm px-4 py-2 rounded-lg disabled:opacity-50"
                    >
                      {loading ? 'Scanning...' : 'Scan News'}
                    </button>
                  </div>
                  <RiskFeed risks={risks} loading={loading} />
                </div>
                <div>
                  <h2 className="text-lg font-medium text-gray-100 mb-4">Weather Alerts</h2>
                  <WeatherAlerts weather={weather} loading={weatherLoading} />
                </div>
              </div>
            </>
          )}

          {/* Weather Tab */}
          {activeTab === 'weather' && (
            <div>
              <div className="mb-6">
                <h1 className="text-2xl font-semibold text-white mb-1">Weather Risk Intelligence</h1>
                <p className="text-gray-400 text-sm">
                  Real-time monitoring of meteorological hazards across primary shipping corridors.
                </p>
              </div>
              <WeatherAlerts weather={weather} loading={weatherLoading} fullPage={true} />
            </div>
          )}

          {/* Shipment Tab */}
          {activeTab === 'shipment' && (
            <ShipmentTracker apiBase={API_BASE} />
          )}

          {/* About Tab */}
          {activeTab === 'about' && (
            <div className="max-w-4xl">
              <div className="mb-4">
                <span className="text-xs text-purple-400 border border-purple-500 border-opacity-40 px-3 py-1 rounded-full">
                  About Our Mission
                </span>
              </div>
              <h1 className="text-5xl font-bold text-white mb-6 leading-tight">
                Ensuring global supply chain resilience through predictive intelligence.
              </h1>
              <p className="text-gray-400 text-base leading-relaxed mb-12 max-w-2xl">
                RiskRadar is the technical authority in real-time logistical vigilance. We empower
                global organizations with the high-fidelity data needed to navigate a world of
                constant disruption.
              </p>

              <h2 className="text-xl font-semibold text-white mb-1">Advanced Capabilities</h2>
              <p className="text-gray-500 text-sm mb-6">
                Precision-engineered tools for the modern risk analyst.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
                {[
                  {
                    icon: '📡',
                    title: 'Live News Intelligence',
                    desc: 'LangGraph 2-node pipeline analyzes global news in real time, classifying supply chain risks with cited sources automatically.',
                  },
                  {
                    icon: '🌤️',
                    title: 'Weather Monitoring',
                    desc: 'Real-time weather tracking across 30 major ports and critical chokepoints worldwide with 3-day forecasts.',
                  },
                  {
                    icon: '📦',
                    title: 'Shipment Risk Advisory',
                    desc: 'AI-powered delay estimation based on live weather data and ChromaDB RAG knowledge base of 13 historical disruptions.',
                  },
                ].map((cap, i) => (
                  <div
                    key={i}
                    className="rounded-xl p-5 transition-all"
                    style={{
                      background: 'rgba(26,26,26,0.8)',
                      border: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    <div className="text-2xl mb-3">{cap.icon}</div>
                    <h3 className="text-white font-semibold mb-2">{cap.title}</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">{cap.desc}</p>
                  </div>
                ))}
              </div>

              <h2 className="text-xl font-semibold text-white mb-1">Tech Stack</h2>
              <p className="text-gray-500 text-sm mb-6">Built with production-grade tools.</p>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-12">
                {[
                  { label: 'LangGraph', desc: 'Agentic pipeline' },
                  { label: 'ChromaDB', desc: 'Vector RAG' },
                  { label: 'FastAPI', desc: 'Backend server' },
                  { label: 'React.js', desc: 'Frontend' },
                  { label: 'Gemini API', desc: 'LLM' },
                  { label: 'NewsAPI', desc: 'Live news' },
                  { label: 'WeatherAPI', desc: '30 ports' },
                  { label: 'LangChain', desc: 'AI framework' },
                ].map((tech, i) => (
                  <div
                    key={i}
                    className="rounded-lg p-3 text-center"
                    style={{
                      background: 'rgba(167,139,250,0.05)',
                      border: '1px solid rgba(167,139,250,0.15)',
                    }}
                  >
                    <p className="text-purple-400 font-medium text-sm">{tech.label}</p>
                    <p className="text-gray-500 text-xs mt-0.5">{tech.desc}</p>
                  </div>
                ))}
              </div>

              <div
                className="flex items-center gap-2 px-4 py-3 rounded-lg w-fit"
                style={{
                  background: 'rgba(74,222,128,0.05)',
                  border: '1px solid rgba(74,222,128,0.15)',
                }}
              >
                <span className="w-2 h-2 rounded-full bg-green-400"></span>
                <span className="text-xs text-green-400 font-medium">System Status: Operational</span>
                <span className="text-gray-600 text-xs ml-2">
                  • 30 ports monitored • All systems nominal
                </span>
              </div>
            </div>
          )}

        </main>

        {/* Mobile Bottom Navigation */}
        <nav className="xl:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center py-3 px-4"
          style={{
            background: 'rgba(17,17,17,0.95)',
            backdropFilter: 'blur(20px)',
            borderTop: '1px solid rgba(255,255,255,0.06)'
          }}>
          {[
            { icon: '🌐', label: 'Dashboard', tab: 'dashboard' },
            { icon: '🌤️', label: 'Weather', tab: 'weather' },
            { icon: '📦', label: 'Shipment', tab: 'shipment' },
            { icon: 'ℹ️', label: 'About', tab: 'about' },
          ].map((item) => (
            <button
              key={item.tab}
              onClick={() => setActiveTab(item.tab)}
              className={`flex flex-col items-center gap-1 px-3 py-1 rounded-lg transition-all ${
                activeTab === item.tab
                  ? 'text-purple-400'
                  : 'text-gray-500'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

      </div>
    </div>
  );
}

export default App;