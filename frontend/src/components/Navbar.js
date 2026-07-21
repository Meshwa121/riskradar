import React from 'react';

function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 flex justify-between items-center px-10 py-4"
      style={{
        background: 'rgba(17, 17, 17, 0.85)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)'
      }}>

      {/* Logo */}
      <div className="flex items-center gap-2">
        <span className="text-purple-400 text-xl">⚡</span>
        <span className="text-white font-semibold text-xl tracking-tight">RiskRadar</span>
      </div>

      {/* Live indicator */}
      <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-semibold rounded-lg transition-colors">
        <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
        Live
      </button>
    </nav>
  );
}

export default Navbar;