import { Room, RoomEvent } from 'livekit-client';

class LiveKitService {
  constructor() {
    this.room = new Room({
      // Automatically manage video/audio tracks
      adaptiveStream: true,
      // Optimize bandwidth usage
      dynacast: true,
      // Automatically publish tracks
      autoSubscribe: true,
    });

    // Bind event handlers
    this.room
      .on(RoomEvent.TrackSubscribed, this.handleTrackSubscribed)
      .on(RoomEvent.TrackUnsubscribed, this.handleTrackUnsubscribed)
      .on(RoomEvent.ParticipantConnected, this.handleParticipantConnected)
      .on(RoomEvent.ParticipantDisconnected, this.handleParticipantDisconnected)
      .on(RoomEvent.Disconnected, this.handleDisconnected);
  }

  // Connect to a LiveKit room
  async connect(roomName, identity, token) {
    try {
      // Connect to the room
      await this.room.connect(
        process.env.REACT_APP_LIVEKIT_WS_URL,
        token || this.generateToken(roomName, identity),
        {
          autoSubscribe: true,
        }
      );
      
      console.log('Connected to room', this.room.name);
      return this.room;
    } catch (error) {
      console.error('Failed to connect to LiveKit room:', error);
      throw error;
    }
  }

  // Generate a token for development (in production, this should be generated server-side)
  generateToken(roomName, identity) {
    // In a real app, this should be an API call to your backend
    return `${process.env.REACT_APP_LIVEKIT_API_KEY}:${process.env.REACT_APP_LIVEKIT_API_SECRET}`;
  }

  // Disconnect from the current room
  async disconnect() {
    if (this.room) {
      this.room.disconnect();
    }
  }

  // Publish local media tracks (camera, microphone, screen share)
  async publishTracks() {
    try {
      // Request camera and microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      });

      // Publish tracks to the room
      for (const track of stream.getTracks()) {
        await this.room.localParticipant.publishTrack(track);
      }
      
      return stream;
    } catch (error) {
      console.error('Error publishing tracks:', error);
      throw error;
    }
  }

  // Event handlers
  handleTrackSubscribed(track, publication, participant) {
    console.log('Track subscribed:', track.kind, 'from', participant.identity);
    // Attach the track to a video/audio element
    const element = document.getElementById(`track-${participant.identity}-${track.kind}`);
    if (element) {
      track.attach(element);
    }
  }

  handleTrackUnsubscribed(track, publication, participant) {
    console.log('Track unsubscribed:', track.kind, 'from', participant.identity);
    // Detach the track from the DOM
    track.detach();
  }

  handleParticipantConnected(participant) {
    console.log('Participant connected:', participant.identity);
    // Handle new participant
  }

  handleParticipantDisconnected(participant) {
    console.log('Participant disconnected:', participant.identity);
    // Handle participant leaving
  }

  handleDisconnected() {
    console.log('Disconnected from room');
    // Handle disconnection
  }

  // Get the current room
  getRoom() {
    return this.room;
  }

  // Get a list of participants (excluding local participant)
  getParticipants() {
    return Array.from(this.room.participants.values());
  }

  // Toggle local audio mute state
  toggleAudio() {
    const audioTrack = this.room.localParticipant.audioTracks.values().next().value;
    if (audioTrack) {
      audioTrack.track.setMuted(!audioTrack.isMuted);
      return !audioTrack.isMuted;
    }
    return false;
  }

  // Toggle local video mute state
  toggleVideo() {
    const videoTrack = this.room.localParticipant.videoTracks.values().next().value;
    if (videoTrack) {
      videoTrack.track.setMuted(!videoTrack.isMuted);
      return !videoTrack.isMuted;
    }
    return false;
  }

  // Start screen sharing
  async startScreenShare() {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          cursor: 'always',
        },
        audio: false,
      });

      const track = stream.getVideoTracks()[0];
      await this.room.localParticipant.publishTrack(track, { name: 'screen' });
      
      return stream;
    } catch (error) {
      console.error('Error sharing screen:', error);
      throw error;
    }
  }

  // Stop screen sharing
  async stopScreenShare() {
    const publications = this.room.localParticipant.tracks.values();
    for (const pub of publications) {
      if (pub.trackName === 'screen') {
        await this.room.localParticipant.unpublishTrack(pub.track);
        pub.track.stop();
      }
    }
  }
}

// Create a singleton instance
export const livekitService = new LiveKitService();
export default livekitService;
