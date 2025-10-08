import { useState, useEffect } from 'react';

// Type definitions
interface Alert {
  id: number;
  type: string;
  location: string;
  timestamp: string;
  severity: string;
  confidence?: number;
  description?: string;
  status?: string;
  image?: string;
}

interface Camera {
  id: string | number;  // Support both MongoDB ObjectId (string) and simple IDs (number)
  name: string;
  location: string;
  status: string;
  url: string;
  type: string;
  image?: string;
}

interface Stats {
  total_cameras?: number;
  active_cameras?: number;
  total_alerts_today?: number;
  detection_accuracy?: number;
  uptime?: string;
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

// Simple API hook without WebSocket for now
export const useApi = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  const [cameras, setCameras] = useState<Camera[]>([]);

  const [stats, setStats] = useState<Stats>({});

  const [logs, setLogs] = useState<Log[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Fetch data from backend API
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Test connection to backend
        const response = await fetch('http://localhost:5000/api/status');
        if (response.ok) {
          setIsConnected(true);
          
          // Fetch real data from backend
          const [alertsRes, camerasRes, statsRes, logsRes] = await Promise.all([
            fetch('http://localhost:5000/api/alerts/list'),
            fetch('http://localhost:5000/api/camera/list'),
            fetch('http://localhost:5000/api/stats'),
            fetch('http://localhost:5000/api/logs')
          ]);

          if (alertsRes.ok) {
            const alertsData = await alertsRes.json();
            setAlerts(alertsData);
          }

          if (camerasRes.ok) {
            const camerasData = await camerasRes.json();
            setCameras(camerasData);
          }

          if (statsRes.ok) {
            const statsData = await statsRes.json();
            setStats(statsData);
          }

          if (logsRes.ok) {
            const logsData = await logsRes.json();
            setLogs(logsData);
          }
        }
      } catch (error) {
        console.log('Backend not available, clearing all data');
        setIsConnected(false);
        // Clear all data when backend is not available
        setAlerts([]);
        setCameras([]);
        setStats({});
        setLogs([]);
      }
    };

    fetchData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const refreshAlerts = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/alerts/list');
      if (response.ok) {
        const data = await response.json();
        setAlerts(data);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const refreshCameras = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/camera/list');
      if (response.ok) {
        const data = await response.json();
        setCameras(data);
      }
    } catch (error) {
      console.error('Error fetching cameras:', error);
    }
  };

  const refreshStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const refreshLogs = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/logs');
      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      }
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  const acknowledgeAlert = async (alertId: number) => {
    try {
      const response = await fetch(`http://localhost:5000/api/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setAlerts(prev =>
          prev.map(alert =>
            alert.id === alertId
              ? { ...alert, status: 'acknowledged' }
              : alert
          )
        );
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const dismissAlert = async (alertId: number) => {
    try {
      const response = await fetch(`http://localhost:5000/api/alerts/${alertId}/dismiss`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setAlerts(prev =>
          prev.map(alert =>
            alert.id === alertId
              ? { ...alert, status: 'dismissed' }
              : alert
          )
        );
      }
    } catch (error) {
      console.error('Error dismissing alert:', error);
    }
  };

  return {
    alerts,
    cameras,
    stats,
    logs,
    socket: null,
    refreshAlerts,
    refreshCameras,
    refreshStats,
    refreshLogs,
    acknowledgeAlert,
    dismissAlert,
    isConnected,
  };
};
