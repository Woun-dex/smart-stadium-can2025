import React from 'react';

const Sidebar = ({
  stadiums,
  selectedStadium,
  onSelectStadium,
  fanPercentage,
  onFanPercentageChange,
  mlEnabled,
  onMlEnabledChange,
  onRunSimulation,
  isLoading
}) => {
  return (
    <aside className="sidebar">
      {/* Stadium Selector */}
      <div className="card">
        <h3 className="card-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <ellipse cx="12" cy="12" rx="10" ry="6"/>
            <path d="M2 12v4c0 3.31 4.48 6 10 6s10-2.69 10-6v-4"/>
            <path d="M2 8v4c0 3.31 4.48 6 10 6s10-2.69 10-6V8"/>
          </svg>
          Select Stadium
        </h3>
        <div className="stadium-list">
          {stadiums.map((stadium) => (
            <div
              key={stadium.id}
              className={`stadium-item ${selectedStadium?.id === stadium.id ? 'selected' : ''}`}
              onClick={() => onSelectStadium(stadium)}
            >
              <h4>{stadium.name}</h4>
              <p>{stadium.city}</p>
              <span className="capacity">Capacity: {stadium.capacity.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Simulation Controls */}
      <div className="card">
        <h3 className="card-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6M12 17v6M4.22 4.22l4.24 4.24M15.54 15.54l4.24 4.24M1 12h6M17 12h6M4.22 19.78l4.24-4.24M15.54 8.46l4.24-4.24"/>
          </svg>
          Simulation Settings
        </h3>

        <div className="control-group">
          <label>Fan Attendance: {fanPercentage}%</label>
          <input
            type="range"
            min="20"
            max="100"
            value={fanPercentage}
            onChange={(e) => onFanPercentageChange(Number(e.target.value))}
          />
          <div className="control-value">
            {selectedStadium 
              ? `${Math.round(selectedStadium.capacity * fanPercentage / 100).toLocaleString()} fans`
              : 'Select a stadium'}
          </div>
        </div>

        <div className="checkbox-group">
          <input
            type="checkbox"
            id="ml-control"
            checked={mlEnabled}
            onChange={(e) => onMlEnabledChange(e.target.checked)}
          />
          <label htmlFor="ml-control">Enable ML Crowd Control</label>
        </div>

        <button
          className="btn btn-primary"
          onClick={onRunSimulation}
          disabled={!selectedStadium || isLoading}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          {isLoading ? 'Running...' : 'Run Simulation'}
        </button>
      </div>

      {/* Selected Stadium Info */}
      {selectedStadium && (
        <div className="card">
          <h3 className="card-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
            Stadium Info
          </h3>
          <div style={{ fontSize: '0.85rem' }}>
            <p><strong>{selectedStadium.name}</strong></p>
            <p style={{ color: 'rgba(255,255,255,0.7)', marginTop: '0.5rem' }}>
              {selectedStadium.city}, Morocco
            </p>
            <p style={{ color: '#FFD700', marginTop: '0.5rem' }}>
              Capacity: {selectedStadium.capacity.toLocaleString()}
            </p>
            <p style={{ color: 'rgba(255,255,255,0.6)', marginTop: '0.5rem', fontSize: '0.8rem' }}>
              {selectedStadium.description}
            </p>
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
