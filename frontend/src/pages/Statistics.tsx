import React from 'react';

interface StatisticsProps {
  statistics: any;
  systemStats: any;
  noteEvents: any[];
}

const Statistics: React.FC<StatisticsProps> = ({
  statistics,
  systemStats,
  noteEvents,
}) => {
  return (
    <>
      {statistics && (
        <div className="statistics-panel">
          <h3>📈 Your Personal Statistics</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Current Notes</span>
              <span className="stat-value">{statistics.total_notes}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Created</span>
              <span className="stat-value">{statistics.total_notes_created}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Updated</span>
              <span className="stat-value">{statistics.total_notes_updated}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Deleted</span>
              <span className="stat-value">{statistics.total_notes_deleted}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Login Count</span>
              <span className="stat-value">{statistics.total_logins}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Member Since</span>
              <span className="stat-value stat-date">
                {statistics.registered_at
                  ? new Date(statistics.registered_at).toLocaleDateString()
                  : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      )}

      {systemStats && (
        <div className="statistics-panel system-stats">
          <h3>🌍 System-Wide Statistics</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Total Users</span>
              <span className="stat-value system-value">{systemStats.total_users}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">All Notes Created</span>
              <span className="stat-value system-value">{systemStats.total_notes_created}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">All Notes Updated</span>
              <span className="stat-value system-value">{systemStats.total_notes_updated}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">All Notes Deleted</span>
              <span className="stat-value system-value">{systemStats.total_notes_deleted}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Logins</span>
              <span className="stat-value system-value">{systemStats.total_logins}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Active Today</span>
              <span className="stat-value system-value">{systemStats.active_users_today}</span>
            </div>
          </div>
        </div>
      )}

      {noteEvents.length > 0 && (
        <div className="statistics-panel events-panel">
          <h3>📜 Recent Activity</h3>
          <div className="events-list">
            {noteEvents.map((event, index) => (
              <div key={index} className="event-item">
                <span className={`event-type ${event.event_type.replace('.', '-')}`}>
                  {event.event_type === 'note.created' && '➕ Created'}
                  {event.event_type === 'note.updated' && '✏️ Updated'}
                  {event.event_type === 'note.deleted' && '🗑️ Deleted'}
                </span>
                <span className="event-title">{event.title || 'Untitled'}</span>
                <span className="event-time">
                  {new Date(event.timestamp).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {!statistics && !systemStats && noteEvents.length === 0 && (
        <div className="no-stats">
          <p>No statistics available yet. Start creating notes!</p>
        </div>
      )}
    </>
  );
};

export default Statistics;
