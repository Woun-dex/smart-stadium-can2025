import React from 'react';

const MLActionsPanel = ({ actions, resources }) => {
  const lastAction = actions.length > 0 ? actions[actions.length - 1] : null;
  
  const currentResources = lastAction ? {
    security: lastAction.security,
    entry: lastAction.entry,
    exit: lastAction.exit,
    vendors: lastAction.vendors
  } : {
    security: resources?.initial?.securityGates || 30,
    entry: resources?.initial?.turnstiles || 20,
    exit: resources?.initial?.exitGates || 25,
    vendors: resources?.initial?.vendors || 40
  };

  const formatTime = (t) => {
    const hours = Math.floor(t / 60);
    const mins = t % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
  };

  return (
    <div className="ml-actions-panel">
      <div className="ml-header">
        <h4 className="card-title" style={{ margin: 0 }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/>
            <path d="M16 14v6a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-6"/>
            <circle cx="12" cy="14" r="4"/>
          </svg>
          ML Crowd Control Actions
        </h4>
        <div className="ml-status">
          <div className="status-dot"></div>
          <span style={{ fontSize: '0.8rem' }}>Active • {actions.length} actions taken</span>
        </div>
      </div>

      {/* Current Resource States */}
      <div className="resource-states">
        <div className="resource-state">
          <div className="label">Security Gates</div>
          <div className="value">{currentResources.security}</div>
          <div className="label" style={{ color: '#C1272D' }}>
            {resources?.initial?.securityGates && currentResources.security > resources.initial.securityGates 
              ? `+${currentResources.security - resources.initial.securityGates}` 
              : 'Initial'}
          </div>
        </div>
        <div className="resource-state">
          <div className="label">Entry Turnstiles</div>
          <div className="value">{currentResources.entry}</div>
          <div className="label">Initial</div>
        </div>
        <div className="resource-state">
          <div className="label">Exit Gates</div>
          <div className="value">{currentResources.exit}</div>
          <div className="label" style={{ color: '#006233' }}>
            {resources?.initial?.exitGates && currentResources.exit > resources.initial.exitGates 
              ? `+${currentResources.exit - resources.initial.exitGates}` 
              : 'Initial'}
          </div>
        </div>
        <div className="resource-state">
          <div className="label">Vendors</div>
          <div className="value">{currentResources.vendors}</div>
          <div className="label" style={{ color: '#FFD700' }}>
            {resources?.initial?.vendors && currentResources.vendors > resources.initial.vendors 
              ? `+${currentResources.vendors - resources.initial.vendors}` 
              : 'Initial'}
          </div>
        </div>
      </div>

      {/* Actions List */}
      <div className="actions-list">
        {actions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'rgba(255,255,255,0.5)' }}>
            No ML actions needed - crowd flow is optimal
          </div>
        ) : (
          actions.slice().reverse().map((action, idx) => (
            <div 
              key={idx} 
              className={`action-item ${action.riskType.toLowerCase()}`}
            >
              <span className="action-time">{formatTime(action.time)}</span>
              <span className={`action-type ${action.type.toLowerCase()}`}>
                {action.type}
              </span>
              <span style={{ 
                fontSize: '0.75rem', 
                padding: '0.2rem 0.5rem',
                background: action.riskType === 'EXIT' ? '#006233' : '#C1272D',
                borderRadius: '4px'
              }}>
                {action.riskType}
              </span>
              <span className="action-decision">{action.decision}</span>
              <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)' }}>
                Q: {action.queue?.toLocaleString()}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MLActionsPanel;
