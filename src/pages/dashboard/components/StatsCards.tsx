
interface Alert {
  id: number;
  type: string;
  location: string;
  timestamp: string;
  severity: string;
  image?: string;
}

interface Log {
  id: number;
  timestamp: string;
  event: string;
  location: string;
  confidence?: number;
  action?: string;
  image?: string;
}

interface Stats {
  total_cameras?: number;
  active_cameras?: number;
  total_alerts_today?: number;
  detection_accuracy?: number;
  uptime?: string;
}

interface StatsCardsProps {
  alerts: Alert[];
  logs: Log[];
  stats?: Stats;
}

export default function StatsCards({ alerts, logs, stats }: StatsCardsProps) {
  const highSeverityAlerts = alerts.filter(alert => alert.severity === 'high').length;
  const recentLogs = logs.filter(log => {
    const logTime = new Date(log.timestamp).getTime();
    const oneHourAgo = Date.now() - (60 * 60 * 1000);
    return logTime > oneHourAgo;
  }).length;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
      {/* Active Cameras */}
      <div className="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Active Cameras</p>
            <p className="text-xl sm:text-3xl font-bold text-gray-900">{stats?.active_cameras || 5}</p>
            <p className="text-xs text-green-600 mt-1">
              <i className="ri-arrow-up-line mr-1"></i>
              <span className="hidden sm:inline">All systems operational</span>
              <span className="sm:hidden">Online</span>
            </p>
          </div>
          <div className="w-8 h-8 sm:w-12 sm:h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <i className="ri-camera-line text-green-600 text-lg sm:text-2xl"></i>
          </div>
        </div>
      </div>

      {/* Active Alerts */}
      <div className="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Active Alerts</p>
            <p className="text-xl sm:text-3xl font-bold text-gray-900">{alerts.length}</p>
            <p className="text-xs text-red-600 mt-1">
              <i className="ri-alert-line mr-1"></i>
              <span className="hidden sm:inline">{highSeverityAlerts} high priority</span>
              <span className="sm:hidden">{highSeverityAlerts} high</span>
            </p>
          </div>
          <div className="w-8 h-8 sm:w-12 sm:h-12 bg-red-100 rounded-lg flex items-center justify-center">
            <i className="ri-alarm-warning-line text-red-600 text-lg sm:text-2xl"></i>
          </div>
        </div>
      </div>

      {/* Detection Rate */}
      <div className="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Detection Rate</p>
            <p className="text-xl sm:text-3xl font-bold text-gray-900">{stats?.detection_accuracy || 97.5}%</p>
            <p className="text-xs text-blue-600 mt-1">
              <i className="ri-line-chart-line mr-1"></i>
              <span className="hidden sm:inline">Excellent performance</span>
              <span className="sm:hidden">Excellent</span>
            </p>
          </div>
          <div className="w-8 h-8 sm:w-12 sm:h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <i className="ri-radar-line text-blue-600 text-lg sm:text-2xl"></i>
          </div>
        </div>
      </div>

      {/* Recent Events */}
      <div className="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Recent Events</p>
            <p className="text-xl sm:text-3xl font-bold text-gray-900">{recentLogs}</p>
            <p className="text-xs text-purple-600 mt-1">
              <i className="ri-time-line mr-1"></i>
              <span className="hidden sm:inline">Last hour</span>
              <span className="sm:hidden">1hr</span>
            </p>
          </div>
          <div className="w-8 h-8 sm:w-12 sm:h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <i className="ri-file-list-3-line text-purple-600 text-lg sm:text-2xl"></i>
          </div>
        </div>
      </div>
    </div>
  );
}
