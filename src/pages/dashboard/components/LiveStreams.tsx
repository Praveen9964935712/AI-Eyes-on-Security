
import { useState } from 'react';

interface Camera {
  id: string | number;  // Support both MongoDB ObjectId (string) and simple IDs (number)
  name: string;
  location: string;
  status: string;
  url?: string;
  type?: string;
  image?: string;
}

interface LiveStreamsProps {
  cameras?: Camera[];
}

export default function LiveStreams({ cameras: propCameras }: LiveStreamsProps) {
  const [showFullscreenModal, setShowFullscreenModal] = useState(false);
  const [fullscreenCamera, setFullscreenCamera] = useState<Camera | null>(null);
  const [showAddCameraModal, setShowAddCameraModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newCamera, setNewCamera] = useState({
    name: '',
    location: '',
    url: '',
    type: 'farm' as 'farm' | 'bank',
    username: '',
    password: ''
  });

  // Use only prop cameras (from API), no mock data
  const cameras = propCameras || [];

  const handleAddCamera = () => {
    setShowAddCameraModal(true);
  };

  const handleSaveCamera = async () => {
    if (!newCamera.name || !newCamera.location || !newCamera.url) {
      alert('Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);
    try {
      // In a real system, this would make an API call to add the camera
      const response = await fetch('http://localhost:5000/api/camera/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newCamera)
      });

      if (response.ok) {
        await response.json(); // Parse response to ensure it's valid
        alert(`Camera "${newCamera.name}" added successfully!`);
        setShowAddCameraModal(false);
        setNewCamera({
          name: '',
          location: '',
          url: '',
          type: 'farm',
          username: '',
          password: ''
        });
        // You could call a refresh function here if available
      } else {
        const error = await response.json();
        alert(`Failed to add camera: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error adding camera:', error);
      alert('Error adding camera. Please check your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelAddCamera = () => {
    setShowAddCameraModal(false);
    setNewCamera({
      name: '',
      location: '',
      url: '',
      type: 'farm',
      username: '',
      password: ''
    });
  };

  const handleTakeSnapshot = async (cameraId: string | number) => {
    try {
      const response = await fetch(`http://localhost:5000/api/camera/${cameraId}/snapshot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Snapshot captured successfully! Saved to: ${result.image_path}`);
      } else {
        const error = await response.json();
        alert(`Failed to capture snapshot: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error taking snapshot:', error);
      alert('Error capturing snapshot. Please check your connection and try again.');
    }
  };

  const handleOpenFullscreen = (camera: Camera) => {
    setFullscreenCamera(camera);
    setShowFullscreenModal(true);
  };

  const handleCloseFullscreen = () => {
    setShowFullscreenModal(false);
    setFullscreenCamera(null);
  };

  return (
    <div>
      {/* Fullscreen Camera Modal */}
      {showFullscreenModal && fullscreenCamera && (
        <div className="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-50">
          <div className="relative w-full h-full flex flex-col">
            {/* Header with camera info and controls */}
            <div className="bg-black bg-opacity-75 text-white p-4 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <div>
                  <h2 className="text-xl font-semibold">{fullscreenCamera.name}</h2>
                  <p className="text-gray-300 text-sm">{fullscreenCamera.location}</p>
                </div>
                <div className="bg-red-600 text-white px-3 py-1 rounded text-sm flex items-center">
                  <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></div>
                  LIVE
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => handleTakeSnapshot(fullscreenCamera.id)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center space-x-2"
                >
                  <i className="ri-camera-line"></i>
                  <span>Snapshot</span>
                </button>
                <button
                  onClick={handleCloseFullscreen}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded flex items-center space-x-2"
                >
                  <i className="ri-close-line"></i>
                  <span>Close</span>
                </button>
              </div>
            </div>

            {/* Main video area */}
            <div className="flex-1 flex items-center justify-center bg-black">
              {fullscreenCamera.url && fullscreenCamera.url !== '0' ? (
                <iframe
                  src={fullscreenCamera.url}
                  className="w-full h-full max-w-6xl max-h-[80vh] border-0"
                  title={`${fullscreenCamera.name} Live Stream`}
                  allow="camera; microphone"
                  onError={() => {
                    console.log('Stream failed to load');
                  }}
                />
              ) : (
                <div className="text-center text-white">
                  <i className="ri-camera-off-line text-6xl mb-4 text-gray-400"></i>
                  <h3 className="text-xl mb-2">Camera Stream Unavailable</h3>
                  <p className="text-gray-400">
                    {fullscreenCamera.url === '0' ? 'Webcam stream not accessible' : 'IP camera stream not reachable'}
                  </p>
                </div>
              )}
            </div>

            {/* Footer with stream info */}
            <div className="bg-black bg-opacity-75 text-white p-4 flex items-center justify-between">
              <div className="flex items-center space-x-6 text-sm">
                <span>Resolution: 1920x1080</span>
                <span>FPS: 30</span>
                <span>Quality: HD</span>
                <span>AI Detection: Active</span>
              </div>
              <div className="text-sm text-gray-300">
                {new Date().toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Camera Modal */}
      {showAddCameraModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-4 sm:mb-6">
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900">Add New Camera</h3>
                <button
                  onClick={handleCancelAddCamera}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <i className="ri-close-line text-xl sm:text-2xl"></i>
                </button>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); handleSaveCamera(); }} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Camera Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={newCamera.name}
                    onChange={(e) => setNewCamera({...newCamera, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Main Entrance Camera"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={newCamera.location}
                    onChange={(e) => setNewCamera({...newCamera, location: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Farm Gate A"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Camera Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={newCamera.type}
                    onChange={(e) => setNewCamera({...newCamera, type: e.target.value as 'farm' | 'bank'})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="farm">Farm Security</option>
                    <option value="bank">Bank Security</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Camera URL / Source <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={newCamera.url}
                    onChange={(e) => setNewCamera({...newCamera, url: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., http://192.168.1.100:8080/video"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Enter IP camera stream URL (MJPEG, RTSP) or '0' for default webcam
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Username (Optional)
                  </label>
                  <input
                    type="text"
                    value={newCamera.username}
                    onChange={(e) => setNewCamera({...newCamera, username: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Camera username (if required)"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password (Optional)
                  </label>
                  <input
                    type="password"
                    value={newCamera.password}
                    onChange={(e) => setNewCamera({...newCamera, password: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Camera password (if required)"
                  />
                </div>

                <div className="flex flex-col sm:flex-row gap-3 sm:justify-end pt-4">
                  <button
                    type="button"
                    onClick={handleCancelAddCamera}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm sm:text-base"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                  >
                    {isSubmitting ? (
                      <>
                        <i className="ri-loader-4-line animate-spin mr-2"></i>
                        Adding...
                      </>
                    ) : (
                      <>
                        <i className="ri-camera-line mr-2"></i>
                        Add Camera
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 sm:mb-6">
        <div>
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-1">Live Camera Streams</h2>
          <p className="text-sm text-gray-600">Monitor all camera feeds in real-time</p>
        </div>
        <div className="flex items-center space-x-2 mt-3 sm:mt-0">
          <button 
            onClick={handleAddCamera}
            className="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm whitespace-nowrap"
          >
            <i className="ri-add-line mr-1 sm:mr-2"></i>
            <span className="hidden sm:inline">Add Camera</span>
            <span className="sm:hidden">Add</span>
          </button>
          <button className="px-3 sm:px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm whitespace-nowrap">
            <i className="ri-settings-3-line mr-1 sm:mr-2"></i>
            <span className="hidden sm:inline">Settings</span>
            <span className="sm:hidden">Config</span>
          </button>
        </div>
      </div>

      {/* Camera Grid */}
      {cameras.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {cameras.map((camera) => (
            <div key={camera.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="relative">
                {/* For IP webcams, show the live stream URL or a placeholder */}
                {camera.url && camera.url !== '0' ? (
                  <iframe
                    src={camera.url}
                    className="w-full h-40 sm:h-48 object-cover"
                    title={`${camera.name} Live Stream`}
                    onError={(e) => {
                      // Fallback to placeholder if stream fails
                      const target = e.target as HTMLIFrameElement;
                      target.style.display = 'none';
                      const placeholder = target.nextElementSibling as HTMLDivElement;
                      if (placeholder) placeholder.style.display = 'flex';
                    }}
                  />
                ) : (
                  <div className="w-full h-40 sm:h-48 bg-gray-200 flex items-center justify-center">
                    <i className="ri-camera-line text-gray-400 text-3xl"></i>
                  </div>
                )}
                
                {/* Fallback placeholder for failed streams */}
                <div 
                  className="w-full h-40 sm:h-48 bg-gray-200 flex-col items-center justify-center hidden"
                  style={{ display: 'none' }}
                >
                  <i className="ri-camera-off-line text-gray-400 text-3xl mb-2"></i>
                  <span className="text-gray-500 text-sm">Stream Unavailable</span>
                </div>

                <div className={`absolute top-2 sm:top-3 right-2 sm:right-3 px-2 py-1 rounded text-xs font-medium ${
                  camera.status === 'online' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-red-600 text-white'
                }`}>
                  {camera.status === 'online' ? (
                    <div className="flex items-center">
                      <div className="w-1.5 h-1.5 bg-white rounded-full mr-1 animate-pulse"></div>
                      <span className="hidden sm:inline">LIVE</span>
                      <span className="sm:hidden">●</span>
                    </div>
                  ) : (
                    <span className="hidden sm:inline">OFFLINE</span>
                  )}
                </div>
                {camera.status === 'online' && (
                  <button
                    onClick={() => handleOpenFullscreen(camera)}
                    className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-30 transition-all group"
                  >
                    <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-600 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <i className="ri-fullscreen-line text-white text-lg sm:text-xl"></i>
                    </div>
                  </button>
                )}
              </div>
              
              <div className="p-3 sm:p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900 text-sm sm:text-base">{camera.name}</h3>
                  <div className={`w-2 h-2 rounded-full ${
                    camera.status === 'online' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                </div>
                <p className="text-xs sm:text-sm text-gray-600 mb-2">{camera.location}</p>
                <p className="text-xs text-gray-500 mb-3 font-mono">{camera.url === '0' ? 'Webcam' : camera.url}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex space-x-1 sm:space-x-2">
                    <button 
                      className="p-1.5 sm:p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="Record"
                    >
                      <i className="ri-record-circle-line text-sm sm:text-base"></i>
                    </button>
                    <button 
                      className="p-1.5 sm:p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="Snapshot"
                      onClick={() => handleTakeSnapshot(camera.id)}
                    >
                      <i className="ri-camera-line text-sm sm:text-base"></i>
                    </button>
                    <button 
                      className="p-1.5 sm:p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="Settings"
                    >
                      <i className="ri-settings-3-line text-sm sm:text-base"></i>
                    </button>
                  </div>
                  
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    camera.status === 'online' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {camera.status === 'online' ? 'Online' : 'Offline'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 sm:py-12">
          <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i className="ri-camera-line text-gray-400 text-2xl sm:text-3xl"></i>
          </div>
          <h3 className="text-lg sm:text-xl font-medium text-gray-900 mb-2">No Cameras Connected</h3>
          <p className="text-sm sm:text-base text-gray-600 mb-4">
            Add IP cameras or webcams to start monitoring your surveillance network
          </p>
          <button 
            onClick={handleAddCamera}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <i className="ri-add-line mr-2"></i>
            Add Your First Camera
          </button>
        </div>
      )}

      {/* Add Camera Card */}
      <div className="mt-4 sm:mt-6">
        <div 
          onClick={handleAddCamera}
          className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-6 sm:p-12 text-center hover:border-blue-400 hover:bg-blue-50 transition-colors cursor-pointer"
        >
          <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
            <i className="ri-add-line text-gray-400 text-xl sm:text-2xl"></i>
          </div>
          <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-2">Add New Camera</h3>
          <p className="text-sm text-gray-600 mb-4">
            Connect IP cameras, webcams, or mobile devices to expand your surveillance network
          </p>
          <button 
            onClick={(e) => { e.stopPropagation(); handleAddCamera(); }}
            className="px-4 sm:px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm sm:text-base whitespace-nowrap"
          >
            <i className="ri-camera-line mr-1 sm:mr-2"></i>
            Add Camera
          </button>
        </div>
      </div>
    </div>
  );
}
