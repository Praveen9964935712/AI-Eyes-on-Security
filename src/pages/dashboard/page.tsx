
import { useState } from 'react';
import Header from './components/Header';
import LiveStreams from './components/LiveStreams';
import AlertsPanel from './components/AlertsPanel';
import LogsTableSimple from './components/LogsTableSimple';
import StatsCards from './components/StatsCards';
import { useApi } from '../../hooks/useApiSimple';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('live');
  const { 
    alerts, 
    cameras, 
    stats,
    logs,
    isConnected,
    refreshAlerts,
    refreshCameras,
    refreshLogs,
    acknowledgeAlert, 
    dismissAlert 
  } = useApi();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header isConnected={isConnected} />
      
      <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6 py-4 sm:py-6">
        <div className="mb-4 sm:mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-1 sm:mb-2">AI Eyes Security Dashboard</h1>
          <p className="text-sm sm:text-base text-gray-600">Real-time surveillance monitoring with AI-powered detection</p>
          {!isConnected && (
            <div className="mt-2 p-2 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded text-sm">
              ⚠️ Connection to backend server lost. Operating in offline mode.
            </div>
          )}
        </div>

        <StatsCards alerts={alerts} logs={logs} stats={stats} isConnected={isConnected} />

        {/* Surveillance Quick Access */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4 sm:mb-6">
          <div className="p-4 sm:p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">🔍 AI Surveillance System</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <a
                href="/surveillance"
                className="flex items-center p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <div className="flex-shrink-0">
                  <span className="text-2xl">📹</span>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-900">Live Surveillance</h3>
                  <p className="text-xs text-blue-700">Monitor real-time detection</p>
                </div>
              </a>
              
              <a
                href="/surveillance/config"
                className="flex items-center p-4 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
              >
                <div className="flex-shrink-0">
                  <span className="text-2xl">⚙️</span>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-900">Configuration</h3>
                  <p className="text-xs text-green-700">Manage zones & faces</p>
                </div>
              </a>
              
              <div className="flex items-center p-4 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="flex-shrink-0">
                  <span className="text-2xl">🛡️</span>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-gray-700">Security Status</h3>
                  <p className="text-xs text-gray-600">
                    {isConnected ? "🟢 System Online" : "🔴 System Offline"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4 sm:mb-6">
          <div className="border-b border-gray-200 overflow-x-auto">
            <nav className="flex space-x-4 sm:space-x-8 px-3 sm:px-6 min-w-max">
              <button
                onClick={() => setActiveTab('live')}
                className={`py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm whitespace-nowrap ${
                  activeTab === 'live'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className="ri-live-line mr-1 sm:mr-2"></i>
                <span className="hidden sm:inline">Live Streams</span>
                <span className="sm:hidden">Live</span>
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm whitespace-nowrap ${
                  activeTab === 'alerts'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className="ri-alarm-warning-line mr-1 sm:mr-2"></i>
                <span className="hidden sm:inline">Alerts ({alerts.length})</span>
                <span className="sm:hidden">Alerts ({alerts.length})</span>
              </button>
              <button
                onClick={() => setActiveTab('logs')}
                className={`py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm whitespace-nowrap ${
                  activeTab === 'logs'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className="ri-file-list-3-line mr-1 sm:mr-2"></i>
                <span className="hidden sm:inline">Event Logs</span>
                <span className="sm:hidden">Logs</span>
              </button>
            </nav>
          </div>

          <div className="p-3 sm:p-6">
            {activeTab === 'live' && <LiveStreams cameras={cameras} onRefreshCameras={refreshCameras} />}
            {activeTab === 'alerts' && (
              <AlertsPanel 
                alerts={alerts} 
                onAcknowledge={acknowledgeAlert}
                onDismiss={dismissAlert}
                onRefresh={refreshAlerts}
              />
            )}
            {activeTab === 'logs' && <LogsTableSimple logs={logs} onRefresh={refreshLogs} />}
          </div>
        </div>
      </div>
    </div>
  );
}
