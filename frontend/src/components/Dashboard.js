import React from 'react';
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import MLActionsPanel from './MLActionsPanel';

const THEME = {
  primary: '#C1272D',
  secondary: '#006233',
  accent: '#FFD700',
  warning: '#f59e0b',
  info: '#3b82f6'
};

const Dashboard = ({ stadium, data, mlEnabled }) => {
  if (!stadium) {
    return (
      <div className="dashboard">
        <div className="welcome-screen">
          <svg width="80" height="80" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#C1272D" strokeWidth="3"/>
            <ellipse cx="50" cy="50" rx="35" ry="20" fill="none" stroke="#006233" strokeWidth="2"/>
            <circle cx="50" cy="50" r="10" fill="#FFD700"/>
          </svg>
          <h2>Welcome to AFCON 2025 Stadium Simulator</h2>
          <p>
            Select a stadium from the list and configure your simulation settings 
            to analyze crowd flow patterns with AI-powered management.
          </p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="dashboard">
        <div className="welcome-screen">
          <h2>{stadium.name}</h2>
          <p>
            Configure your simulation settings and click "Run Simulation" to 
            see crowd flow analysis for this venue.
          </p>
        </div>
      </div>
    );
  }

  const { timeseries, actions, summary, resources } = data;

  return (
    <div className="dashboard">
      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card entry">
          <div className="stat-value" style={{ color: THEME.primary }}>
            {summary.avgSecurityWait}m
          </div>
          <div className="stat-label">Avg Security Wait</div>
          <div className="stat-detail">Peak queue: {summary.maxEntryQueue?.toLocaleString()}</div>
        </div>
        <div className="stat-card entry">
          <div className="stat-value" style={{ color: THEME.primary }}>
            {summary.avgTurnstileWait}m
          </div>
          <div className="stat-label">Avg Turnstile Wait</div>
          <div className="stat-detail">Entry gates: {resources.initial.turnstiles}</div>
        </div>
        <div className="stat-card exit">
          <div className="stat-value" style={{ color: THEME.secondary }}>
            {summary.avgExitWait}m
          </div>
          <div className="stat-label">Avg Exit Wait</div>
          <div className="stat-detail">Peak queue: {summary.maxExitQueue?.toLocaleString()}</div>
        </div>
        <div className="stat-card risk">
          <div className="stat-value" style={{ color: THEME.accent }}>
            {summary.totalFans?.toLocaleString()}
          </div>
          <div className="stat-label">Total Fans</div>
          <div className="stat-detail">ML Actions: {summary.totalActions}</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Queue Over Time */}
        <div className="chart-card">
          <h4 className="chart-title">Queue Sizes Over Time</h4>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={timeseries}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="time" 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
              />
              <YAxis 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
              />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(26, 26, 46, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="security_queue" 
                name="Security" 
                stackId="1"
                stroke={THEME.primary} 
                fill={THEME.primary}
                fillOpacity={0.6}
              />
              <Area 
                type="monotone" 
                dataKey="turnstile_queue" 
                name="Turnstile" 
                stackId="1"
                stroke={THEME.warning} 
                fill={THEME.warning}
                fillOpacity={0.6}
              />
              <Area 
                type="monotone" 
                dataKey="exit_queue" 
                name="Exit" 
                stackId="2"
                stroke={THEME.secondary} 
                fill={THEME.secondary}
                fillOpacity={0.6}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Wait Times */}
        <div className="chart-card">
          <h4 className="chart-title">Average Wait Times (minutes)</h4>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={timeseries}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="time" 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
              />
              <YAxis 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
              />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(26, 26, 46, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="avg_security_wait" 
                name="Security Wait"
                stroke={THEME.primary} 
                strokeWidth={2}
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="avg_turnstile_wait" 
                name="Turnstile Wait"
                stroke={THEME.warning} 
                strokeWidth={2}
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="avg_exit_wait" 
                name="Exit Wait"
                stroke={THEME.secondary} 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Crowd Flow */}
        <div className="chart-card">
          <h4 className="chart-title">Crowd Flow - Entry & Exit</h4>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={timeseries}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="time" 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
              />
              <YAxis 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
              />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(26, 26, 46, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="inside_stadium" 
                name="Inside Stadium"
                stroke={THEME.info} 
                fill={THEME.info}
                fillOpacity={0.3}
              />
              <Area 
                type="monotone" 
                dataKey="total_entered" 
                name="Total Entered"
                stroke={THEME.secondary} 
                fill={THEME.secondary}
                fillOpacity={0.2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Vendor Queue */}
        <div className="chart-card">
          <h4 className="chart-title">Vendor & Concession Activity</h4>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={timeseries}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="time" 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
              />
              <YAxis 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
              />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(26, 26, 46, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="vendor_queue" 
                name="Vendor Queue"
                stroke={THEME.accent} 
                strokeWidth={2}
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="avg_vendor_wait" 
                name="Vendor Wait (min)"
                stroke="#ff6b9d" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ML Actions Panel */}
      {mlEnabled && (
        <MLActionsPanel 
          actions={actions} 
          resources={resources}
        />
      )}
    </div>
  );
};

export default Dashboard;
