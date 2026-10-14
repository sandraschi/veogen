import React, { useState, useEffect, useRef } from 'react';
import { livekitService } from '../../services/livekit';
import './VideoRoom.css';

const VideoRoom = ({ roomName, identity, onLeave }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [_participants, setParticipants] = useState([]);
  const [isAudioMuted, setIsAudioMuted] = useState(false);
  const [isVideoMuted, setIsVideoMuted] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [error, setError] = useState(null);

  const localVideoRef = useRef(null);
  const screenShareRef = useRef(null);
  const participantsRef = useRef({});

  useEffect(() => {
    const connectToRoom = async () => {
      try {
        // Connect to the LiveKit room
        await livekitService.connect(roomName, identity);

        // Publish local media tracks
        const stream = await livekitService.publishTracks();

        // Set up local video element
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }

        // Update state
        setIsConnected(true);
        updateParticipants();

        // Set up event listeners
        const room = livekitService.getRoom();
        room.on('participantConnected', handleParticipantConnected);
        room.on('participantDisconnected', handleParticipantDisconnected);
      } catch (err) {
        console.error('Error connecting to room:', err);
        setError('Failed to connect to the video room. Please check your permissions and try again.');
      }
    };

    connectToRoom();

    // Cleanup on unmount
    return () => {
      const cleanup = async () => {
        try {
          await livekitService.disconnect();

          // Stop all media tracks
          if (localVideoRef.current?.srcObject) {
            for (const track of localVideoRef.current.srcObject.getTracks()) {
              track.stop();
            }
          }

          if (screenShareRef.current?.srcObject) {
            for (const track of screenShareRef.current.srcObject.getTracks()) {
              track.stop();
            }
          }
        } catch (err) {
          console.error('Error during cleanup:', err);
        }
      };

      cleanup();
    };
  }, [roomName, identity]);

  const handleParticipantConnected = (participant) => {
    console.log('Participant connected:', participant.identity);
    updateParticipants();

    // Handle tracks from new participant
    for (const publication of participant.tracks.values()) {
      if (publication.track) {
        handleTrackPublished(publication.track, participant);
      }
    }

    participant.on('trackPublished', handleTrackPublished);
  };

  const handleParticipantDisconnected = (participant) => {
    console.log('Participant disconnected:', participant.identity);
    updateParticipants();

    // Clean up participant's video elements
    if (participantsRef.current[participant.identity]) {
      for (const element of participantsRef.current[participant.identity]) {
        if (element.parentNode) {
          element.parentNode.removeChild(element);
        }
      }
      delete participantsRef.current[participant.identity];
    }
  };

  const handleTrackPublished = (track, participant) => {
    if (!participantsRef.current[participant.identity]) {
      participantsRef.current[participant.identity] = [];
    }

    const elementId = `track-${participant.identity}-${track.kind}`;
    let element = document.getElementById(elementId);

    if (!element) {
      element = document.createElement(track.kind === 'video' ? 'video' : 'audio');
      element.id = elementId;
      element.autoplay = true;
      element.playsInline = true;

      if (track.kind === 'video') {
        element.width = 320;
        element.height = 180;
      }

      const container = document.getElementById('participants-container');
      if (container) {
        const wrapper = document.createElement('div');
        wrapper.className = 'participant';
        wrapper.id = `participant-${participant.identity}`;

        const nameLabel = document.createElement('div');
        nameLabel.className = 'participant-name';
        nameLabel.textContent = participant.identity;

        wrapper.appendChild(element);
        wrapper.appendChild(nameLabel);
        container.appendChild(wrapper);
      }

      participantsRef.current[participant.identity].push(element);
    }

    track.attach(element);
  };

  const updateParticipants = () => {
    const room = livekitService.getRoom();
    if (room) {
      setParticipants(Array.from(room.participants.values()));
    }
  };

  const toggleAudio = () => {
    const newState = livekitService.toggleAudio();
    setIsAudioMuted(!newState);
  };

  const toggleVideo = () => {
    const newState = livekitService.toggleVideo();
    setIsVideoMuted(!newState);
  };

  const toggleScreenShare = async () => {
    try {
      if (isScreenSharing) {
        await livekitService.stopScreenShare();
        if (screenShareRef.current) {
          screenShareRef.current.srcObject = null;
        }
      } else {
        const stream = await livekitService.startScreenShare();
        if (screenShareRef.current) {
          screenShareRef.current.srcObject = stream;
        }
      }
      setIsScreenSharing(!isScreenSharing);
    } catch (err) {
      console.error('Error toggling screen share:', err);
      setError('Failed to share screen. Please ensure you have the necessary permissions.');
    }
  };

  const handleLeave = async () => {
    try {
      await livekitService.disconnect();
      if (onLeave) {
        onLeave();
      }
    } catch (err) {
      console.error('Error leaving room:', err);
      setError('Error leaving the room. Please try again.');
    }
  };

  if (error) {
    return (
      <div className="video-room error">
        <div className="error-message">{error}</div>
        <button type="button" onClick={handleLeave} className="leave-button">
          Leave Room
        </button>
      </div>
    );
  }

  if (!isConnected) {
    return <div className="video-room loading">Connecting to room...</div>;
  }

  return (
    <div className="video-room">
      <div className="main-content">
        <div className="screen-share-container">
          <video
            ref={screenShareRef}
            autoPlay
            playsInline
            className="screen-share"
            style={{ display: isScreenSharing ? 'block' : 'none' }}
          >
            <track kind="captions" />
          </video>
        </div>

        <div id="participants-container" className="participants-grid">
          {/* Local video */}
          <div className="participant local">
            <video
              ref={localVideoRef}
              autoPlay
              playsInline
              muted
              className="local-video"
              style={{ opacity: isVideoMuted ? 0.5 : 1 }}
            />
            <div className="participant-name">
              {identity} (You)
              {isVideoMuted && <span className="muted-indicator"> (Video Muted)</span>}
            </div>
          </div>

          {/* Remote participants will be added here dynamically */}
        </div>
      </div>

      <div className="controls">
        <button
          type="button"
          onClick={toggleAudio}
          className={`control-button ${isAudioMuted ? 'muted' : ''}`}
          title={isAudioMuted ? 'Unmute' : 'Mute'}
        >
          {isAudioMuted ? '🔇' : '🔊'}
        </button>

        <button
          type="button"
          onClick={toggleVideo}
          className={`control-button ${isVideoMuted ? 'muted' : ''}`}
          title={isVideoMuted ? 'Start Video' : 'Stop Video'}
        >
          {isVideoMuted ? '📹' : '📷'}
        </button>

        <button
          type="button"
          onClick={toggleScreenShare}
          className={`control-button ${isScreenSharing ? 'active' : ''}`}
          title={isScreenSharing ? 'Stop Sharing' : 'Share Screen'}
        >
          📱
        </button>

        <button type="button" onClick={handleLeave} className="control-button leave" title="Leave Call">
          🚪 Leave
        </button>
      </div>
    </div>
  );
};

export default VideoRoom;
