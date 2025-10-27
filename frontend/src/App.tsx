import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import './App.css';
import Login from './components/Login';
import Register from './components/Register';
import Notes from './pages/Notes';
import Statistics from './pages/Statistics';

export interface Note {
  id: number;
  title: string;
  content: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
}

const USERS_API_URL = import.meta.env.VITE_USERS_API_URL || 'http://localhost:8002';
const NOTES_API_URL = import.meta.env.VITE_NOTES_API_URL || 'http://localhost:8001';
const ANALYTICS_API_URL = import.meta.env.VITE_ANALYTICS_API_URL || 'http://localhost:8003';

function App() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<User | null>(null);
  const [showRegister, setShowRegister] = useState(false);
  const [statistics, setStatistics] = useState<any>(null);
  const [systemStats, setSystemStats] = useState<any>(null);
  const [noteEvents, setNoteEvents] = useState<any[]>([]);

  // Fetch current user
  const fetchUser = async (authToken: string) => {
    try {
      const response = await fetch(`${USERS_API_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch user');
      const data = await response.json();
      setUser(data);
    } catch (err) {
      console.error('Error fetching user:', err);
      handleLogout();
    }
  };

  // Fetch notes
  const fetchNotes = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${NOTES_API_URL}/notes/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch notes');
      const data = await response.json();
      setNotes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Fetch user statistics
  const fetchStatistics = async () => {
    if (!token) return;

    try {
      const response = await fetch(`${ANALYTICS_API_URL}/analytics/users/me/statistics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setStatistics(data);
      }
    } catch (err) {
      console.error('Error fetching statistics:', err);
    }
  };

  // Fetch system-wide statistics
  const fetchSystemStats = async () => {
    try {
      const response = await fetch(`${ANALYTICS_API_URL}/analytics/system/statistics`);
      if (response.ok) {
        const data = await response.json();
        setSystemStats(data);
      }
    } catch (err) {
      console.error('Error fetching system statistics:', err);
    }
  };

  // Fetch note events
  const fetchNoteEvents = async () => {
    if (!token || !user) return;

    try {
      const response = await fetch(`${ANALYTICS_API_URL}/analytics/users/${user.id}/events/notes?limit=10`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setNoteEvents(data);
      }
    } catch (err) {
      console.error('Error fetching note events:', err);
    }
  };

  useEffect(() => {
    if (token) {
      fetchUser(token);
      fetchNotes();
      fetchStatistics();
      fetchSystemStats();
    }
  }, [token]);

  useEffect(() => {
    if (user && token) {
      fetchNoteEvents();
    }
  }, [user, token]);

  const handleLogin = async (username: string, password: string) => {
    try {
      setError(null);
      const response = await fetch(`${USERS_API_URL}/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
      if (!response.ok) throw new Error('Login failed');
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    }
  };

  const handleRegister = async (username: string, email: string, password: string) => {
    try {
      setError(null);
      const response = await fetch(`${USERS_API_URL}/users/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });
      if (!response.ok) throw new Error('Registration failed');
      // Auto-login after registration
      await handleLogin(username, password);
      setShowRegister(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
      throw err;
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setNotes([]);
    setStatistics(null);
  };

  const handleCreateNote = async (title: string, content: string) => {
    if (!token) return;

    try {
      setError(null);
      const response = await fetch(`${NOTES_API_URL}/notes/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ title, content }),
      });
      if (!response.ok) throw new Error('Failed to create note');
      await fetchNotes();
      await fetchStatistics();
      await fetchNoteEvents();
      await fetchSystemStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleUpdateNote = async (id: number, title: string, content: string) => {
    if (!token) return;

    try {
      setError(null);
      const response = await fetch(`${NOTES_API_URL}/notes/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ title, content }),
      });
      if (!response.ok) throw new Error('Failed to update note');
      setEditingNote(null);
      await fetchNotes();
      await fetchStatistics();
      await fetchNoteEvents();
      await fetchSystemStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleDeleteNote = async (id: number) => {
    if (!token) return;
    if (!window.confirm('Are you sure you want to delete this note?')) return;

    try {
      setError(null);
      const response = await fetch(`${NOTES_API_URL}/notes/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to delete note');
      await fetchNotes();
      await fetchStatistics();
      await fetchNoteEvents();
      await fetchSystemStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  // If not logged in, show login/register
  if (!token) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Notes Management System</h1>
          <p>Microservices Architecture Demo</p>
        </header>
        <main className="App-main">
          {error && <div className="error-message">{error}</div>}
          {showRegister ? (
            <Register
              onRegister={handleRegister}
              onSwitchToLogin={() => setShowRegister(false)}
            />
          ) : (
            <Login
              onLogin={handleLogin}
              onSwitchToRegister={() => setShowRegister(true)}
            />
          )}
        </main>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="App">
        <header className="App-header">
          <div className="header-left">
            <h1>Notes Management System</h1>
          </div>
          <nav className="header-nav">
            <Link to="/" className="nav-link">Notes</Link>
            <Link to="/statistics" className="nav-link">Statistics</Link>
          </nav>
          <div className="user-info">
            <span>Welcome, {user?.username}!</span>
            <button onClick={handleLogout} className="logout-button">Logout</button>
          </div>
        </header>
        <main className="App-main">
          {error && <div className="error-message">{error}</div>}

          <Routes>
            <Route
              path="/"
              element={
                <Notes
                  notes={notes}
                  editingNote={editingNote}
                  loading={loading}
                  onCreateNote={handleCreateNote}
                  onUpdateNote={handleUpdateNote}
                  onDeleteNote={handleDeleteNote}
                  setEditingNote={setEditingNote}
                />
              }
            />
            <Route
              path="/statistics"
              element={
                <Statistics
                  statistics={statistics}
                  systemStats={systemStats}
                  noteEvents={noteEvents}
                />
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
