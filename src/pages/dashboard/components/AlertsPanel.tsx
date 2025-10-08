
import { useState } from 'react';

interface Alert {
  id: number;
  type: string;
  location: string;
  timestamp: string;
  severity: string;
  image?: string;
  status?: string;
  confidence?: number;
  description?: string;
}

interface AlertsPanelProps {
  alerts: Alert[];
  onAcknowledge?: (alertId: number) => void;
  onDismiss?: (alertId: number) => void;
  onRefresh?: () => void;
}

export default function AlertsPanel({ alerts, onAcknowledge, onDismiss, onRefresh }: AlertsPanelProps) {
  const [filter, setFilter] = useState('all');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const filteredAlerts = alerts.filter(alert => 
    filter === 'all' || alert.severity === filter
  );

  const dismissAlert = (alertId: number) => {
    if (onDismiss) {
      onDismiss(alertId);
    }
    if (selectedAlert && selectedAlert.id === alertId) {
      setSelectedAlert(null);
    }
  };

  const acknowledgeAlert = (alertId: number) => {
    if (onAcknowledge) {
      onAcknowledge(alertId);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return 'ri-alarm-warning-fill';
      case 'medium': return 'ri-alert-fill';
      case 'low': return 'ri-information-fill';
      default: return 'ri-notification-3-fill';
    }
  };

  const getAlertTypeIcon = (type: string) => {
    switch (type) {
      case 'intruder': return 'ri-user-forbid-line';
      case 'suspicious_activity': return 'ri-eye-line';
      case 'motion': return 'ri-run-line';
      default: return 'ri-alarm-warning-line';
    }
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 sm:mb-6">
        <div>
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-1">Security Alerts</h2>
          <p className="text-sm text-gray-600">Real-time threat notifications and security events</p>
        </div>
        
        {/* Filter Buttons */}
        <div className="flex items-center space-x-1 sm:space-x-2 mt-3 sm:mt-0 overflow-x-auto">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="px-2 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-colors whitespace-nowrap bg-gray-100 text-gray-600 hover:bg-gray-200 mr-2"
            >
              <i className="ri-refresh-line mr-1"></i>
              Refresh
            </button>
          )}
          {['all', 'high', 'medium', 'low'].map((severity) => (
            <button
              key={severity}
              onClick={() => setFilter(severity)}
              className={`px-2 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-colors whitespace-nowrap ${
                filter === severity
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {severity === 'all' ? 'All Alerts' : `${severity.charAt(0).toUpperCase() + severity.slice(1)} Priority`}
            </button>
          ))}
        </div>
      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-4 sm:mb-6">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center ${
                    selectedAlert.severity === 'high' ? 'bg-red-100' :
                    selectedAlert.severity === 'medium' ? 'bg-yellow-100' : 'bg-blue-100'
                  }`}>
                    <i className={`${getAlertTypeIcon(selectedAlert.type)} text-lg sm:text-xl ${
                      selectedAlert.severity === 'high' ? 'text-red-600' :
                      selectedAlert.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                    }`}></i>
                  </div>
                  <div>
                    <h3 className="text-lg sm:text-xl font-semibold text-gray-900">
                      {selectedAlert.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Detected
                    </h3>
                    <p className="text-sm text-gray-600">{selectedAlert.location}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <i className="ri-close-line text-xl sm:text-2xl"></i>
                </button>
              </div>

              <div className="mb-4 sm:mb-6">
                {selectedAlert.image && (
                  <img
                    src={selectedAlert.image}
                    alt="Alert Evidence"
                    className="w-full h-48 sm:h-64 object-cover rounded-lg"
                  />
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 mb-4 sm:mb-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Alert Details</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Timestamp:</span>
                      <span className="font-medium">{formatTimestamp(selectedAlert.timestamp)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Location:</span>
                      <span className="font-medium">{selectedAlert.location}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Severity:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(selectedAlert.severity)}`}>
                        {selectedAlert.severity.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Detection Info</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span className="font-medium">
                        {selectedAlert.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Confidence:</span>
                      <span className="font-medium">94.7%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Camera ID:</span>
                      <span className="font-medium">CAM-{selectedAlert.id.toString().padStart(3, '0')}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 sm:justify-end">
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm sm:text-base"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    // Add to ignore list or mark as false positive
                    acknowledgeAlert(selectedAlert.id);
                    setSelectedAlert(null);
                  }}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 text-sm sm:text-base"
                >
                  Mark as False Positive
                </button>
                <button
                  onClick={() => {
                    // Send to security team or escalate
                    alert('Alert escalated to security team');
                    dismissAlert(selectedAlert.id);
                  }}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm sm:text-base"
                >
                  Escalate Alert
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alerts List */}
      {filteredAlerts.length === 0 ? (
        <div className="text-center py-8 sm:py-12">
          <div className="w-16 h-16 sm:w-20 sm:h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i className="ri-shield-check-line text-green-600 text-2xl sm:text-3xl"></i>
          </div>
          <h3 className="text-lg sm:text-xl font-medium text-gray-900 mb-2">No Active Alerts</h3>
          <p className="text-sm sm:text-base text-gray-600">
            {filter === 'all' 
              ? 'All systems are operating normally. No security threats detected.'
              : `No ${filter} priority alerts at this time.`
            }
          </p>
        </div>
      ) : (
        <div className="space-y-3 sm:space-y-4">
          {filteredAlerts.map((alert) => (
            <div key={alert.id} className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6 hover:shadow-md transition-shadow">
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                {/* Alert Image */}
                <div className="w-full sm:w-24 h-32 sm:h-16 flex-shrink-0">
                  {alert.image ? (
                    <img
                      src={alert.image}
                      alt="Alert Evidence"
                      className="w-full h-full object-cover rounded-lg cursor-pointer hover:opacity-80 transition-opacity"
                      onClick={() => setSelectedAlert(alert)}
                    />
                  ) : (
                    <div 
                      className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors"
                      onClick={() => setSelectedAlert(alert)}
                    >
                      <i className="ri-image-line text-gray-400 text-xl"></i>
                    </div>
                  )}
                </div>

                {/* Alert Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-4 mb-2">
                    <div className="flex items-center space-x-2">
                      <i className={`${getAlertTypeIcon(alert.type)} text-lg ${
                        alert.severity === 'high' ? 'text-red-600' :
                        alert.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                      }`}></i>
                      <h3 className="font-medium text-gray-900 text-sm sm:text-base">
                        {alert.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Detected
                      </h3>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(alert.severity)} whitespace-nowrap`}>
                      <i className={`${getSeverityIcon(alert.severity)} mr-1`}></i>
                      {alert.severity.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div className="text-sm text-gray-600">
                      <div className="flex items-center space-x-4">
                        <span>
                          <i className="ri-map-pin-line mr-1"></i>
                          {alert.location}
                        </span>
                        <span>
                          <i className="ri-time-line mr-1"></i>
                          {formatTimestamp(alert.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-row sm:flex-col gap-2 sm:gap-1">
                  <button
                    onClick={() => setSelectedAlert(alert)}
                    className="flex-1 sm:flex-none px-3 py-1.5 text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors text-xs sm:text-sm whitespace-nowrap"
                  >
                    <i className="ri-eye-line mr-1"></i>
                    <span className="hidden sm:inline">View Details</span>
                    <span className="sm:hidden">View</span>
                  </button>
                  <button
                    onClick={() => dismissAlert(alert.id)}
                    className="flex-1 sm:flex-none px-3 py-1.5 text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors text-xs sm:text-sm whitespace-nowrap"
                  >
                    <i className="ri-close-line mr-1"></i>
                    <span className="hidden sm:inline">Dismiss</span>
                    <span className="sm:hidden">Dismiss</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
