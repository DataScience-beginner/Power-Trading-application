import React, { useState } from 'react';
import axios from 'axios';

const Profile: React.FC = () => {
  const [username, setUsername] = useState('');
  const [profile, setProfile] = useState<any>(null);
  const [message, setMessage] = useState('');

  const handleFetchProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.get('http://localhost:8000/profile', {
        params: { username },
      });
      setProfile(response.data);
      setMessage('');
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Failed to fetch profile');
      setProfile(null);
    }
  };

  return (
    <div>
      <h2>Profile</h2>
      <form onSubmit={handleFetchProfile}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <button type="submit">Fetch Profile</button>
      </form>
      {message && <p>{message}</p>}
      {profile && (
        <div>
          <h3>Profile Details:</h3>
          <p>Username: {profile.username}</p>
          <p>Email: {profile.email}</p>
        </div>
      )}
    </div>
  );
};

export default Profile;