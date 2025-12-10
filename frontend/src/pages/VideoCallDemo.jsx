import React, { useState } from 'react';
import VideoRoom from '../components/livekit/VideoRoom';
import '../styles/VideoCallDemo.css';

const VideoCallDemo = () => {
  const [roomName, setRoomName] = useState('veogen-demo-room');
  const [username, setUsername] = useState(`user-${Math.floor(Math.random() * 1000)}`);
  const [joined, setJoined] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleJoinRoom = (e) => {
    e.preventDefault();
    if (roomName.trim() && username.trim()) {
      setIsLoading(true);
      // Small delay to show loading state
      setTimeout(() => {
        setJoined(true);
        setIsLoading(false);
      }, 500);
    }
  };

  const handleLeaveRoom = () => {
    setJoined(false);
  };

  if (joined) {
    return (
      <div className="video-call-container">
        <div className="video-call-header">
          <h2>Video Call: {roomName}</h2>
          <button 
            onClick={handleLeaveRoom}
            className="leave-button"
          >
            Leave Room
          </button>
        </div>
        <div className="video-room-wrapper">
          <VideoRoom 
            roomName={roomName}
            identity={username}
            onLeave={handleLeaveRoom}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="join-room-container">
      <div className="join-room-card">
        <h2>Join Video Call</h2>
        <form onSubmit={handleJoinRoom} className="join-form">
          <div className="form-group">
            <label htmlFor="roomName">Room Name</label>
            <input
              type="text"
              id="roomName"
              value={roomName}
              onChange={(e) => setRoomName(e.target.value)}
              placeholder="Enter room name"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="username">Your Name</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your name"
              required
            />
          </div>
          <button 
            type="submit" 
            className="join-button"
            disabled={isLoading}
          >
            {isLoading ? 'Joining...' : 'Join Room'}
          </button>
        </form>
        <div className="instructions">
          <h3>How to use:</h3>
          <ol>
            <li>Share the room name with others to invite them</li>
            <li>Allow camera and microphone access when prompted</li>
            <li>Use the controls at the bottom to manage your call</li>
            <li>Click the screen share button to share your screen</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default VideoCallDemo;
