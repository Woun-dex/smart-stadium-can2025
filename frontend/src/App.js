import React, { useState, useCallback } from 'react';
import { STADIUMS, getStadiumResources, THEME } from './data/stadiums';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import LoadingOverlay from './components/LoadingOverlay';
import './App.css';

function App() {
  const [selectedStadium, setSelectedStadium] = useState(null);
  const [simulationData, setSimulationData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [mlEnabled, setMlEnabled] = useState(true);
  const [fanPercentage, setFanPercentage] = useState(80);

  const runSimulation = useCallback(async () => {
    if (!selectedStadium) return;

    setIsLoading(true);
    setLoadingMessage(`Running simulation for ${selectedStadium.name}...`);

    const resources = getStadiumResources(selectedStadium.capacity);
    const numFans = Math.round(selectedStadium.capacity * (fanPercentage / 100));

    try {
      const response = await fetch('http://localhost:5000/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stadium: selectedStadium,
          fans: numFans,
          resources: resources,
          mlEnabled: mlEnabled
        })
      });

      if (!response.ok) throw new Error('Simulation failed');
      
      const data = await response.json();
      setSimulationData(data);
    } catch (error) {
      console.error('Simulation error:', error);
      // Generate mock data for demo if API unavailable
      setSimulationData(generateMockData(selectedStadium, numFans, resources, mlEnabled));
    } finally {
      setIsLoading(false);
    }
  }, [selectedStadium, fanPercentage, mlEnabled]);

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Sidebar
          stadiums={STADIUMS}
          selectedStadium={selectedStadium}
          onSelectStadium={setSelectedStadium}
          fanPercentage={fanPercentage}
          onFanPercentageChange={setFanPercentage}
          mlEnabled={mlEnabled}
          onMlEnabledChange={setMlEnabled}
          onRunSimulation={runSimulation}
          isLoading={isLoading}
        />
        <Dashboard
          stadium={selectedStadium}
          data={simulationData}
          mlEnabled={mlEnabled}
        />
      </main>
      {isLoading && <LoadingOverlay message={loadingMessage} />}
    </div>
  );
}

// Generate mock simulation data for demo purposes
function generateMockData(stadium, numFans, resources, mlEnabled) {
  const data = [];
  const kickoffTime = 180;
  const matchEnd = 300;
  const totalTime = 360;

  for (let t = 0; t <= totalTime; t++) {
    // Arrival pattern: peak at t=120-180
    let arrivalRate = 0;
    if (t < kickoffTime) {
      arrivalRate = Math.exp(-Math.pow((t - 120) / 40, 2)) * (numFans / 180);
    }

    // Exit pattern: after match
    let exitRate = 0;
    if (t > matchEnd - 5) {
      exitRate = Math.exp(-Math.pow((t - (matchEnd + 30)) / 20, 2)) * (numFans / 60);
    }

    const entryQueue = Math.max(0, Math.round(arrivalRate * 50 * (1 + Math.random() * 0.3)));
    const exitQueue = Math.max(0, Math.round(exitRate * 30 * (1 + Math.random() * 0.3)));
    const insideStadium = Math.min(numFans, Math.round(numFans * Math.min(1, t / matchEnd)));

    data.push({
      time: t,
      security_queue: Math.round(entryQueue * 0.6),
      turnstile_queue: Math.round(entryQueue * 0.4),
      exit_queue: exitQueue,
      vendor_queue: Math.round(insideStadium * 0.02),
      avg_security_wait: Math.max(0, entryQueue * 0.05 + Math.random() * 2),
      avg_turnstile_wait: Math.max(0, entryQueue * 0.08 + Math.random() * 3),
      avg_exit_wait: Math.max(0, exitQueue * 0.03 + Math.random()),
      avg_vendor_wait: Math.random() * 5,
      inside_stadium: insideStadium,
      total_entered: Math.round(numFans * Math.min(1, t / kickoffTime)),
      total_exited: t > matchEnd ? Math.round(numFans * Math.min(1, (t - matchEnd) / 60)) : 0
    });
  }

  // Generate ML actions
  const actions = [];
  let securityGates = resources.securityGates;
  let entryGates = resources.turnstiles;
  let exitGates = resources.exitGates;
  let vendors = resources.vendors;

  if (mlEnabled) {
    data.forEach((row, idx) => {
      if (idx % 10 !== 0) return;
      
      const entryQueue = row.security_queue + row.turnstile_queue;
      const exitQueue = row.exit_queue;
      const entryRisk = Math.min(entryQueue / 5000, 1) * 0.4 + Math.min(row.avg_security_wait / 15, 1) * 0.5;
      const exitRisk = Math.min(exitQueue / 2000, 1) * 0.4 + Math.min(row.avg_exit_wait / 10, 1) * 0.5;

      if (exitQueue > 500 && exitRisk > 0.4) {
        const oldExit = exitGates;
        exitGates = Math.min(exitGates + (exitRisk > 0.6 ? 10 : 5), 80);
        actions.push({
          time: row.time,
          type: exitRisk > 0.6 ? 'STRONG' : 'MODERATE',
          riskType: 'EXIT',
          risk: exitRisk,
          queue: exitQueue,
          decision: `+${exitGates - oldExit} exit gates (${oldExit}→${exitGates})`,
          security: securityGates,
          entry: entryGates,
          exit: exitGates,
          vendors: vendors
        });
      } else if (entryQueue > 500 && entryRisk > 0.5) {
        const oldSec = securityGates;
        const oldVend = vendors;
        securityGates = Math.min(securityGates + (entryRisk > 0.7 ? 5 : 3), 80);
        vendors = Math.min(vendors + (entryRisk > 0.7 ? 10 : 5), 150);
        actions.push({
          time: row.time,
          type: entryRisk > 0.7 ? 'STRONG' : 'MODERATE',
          riskType: 'ENTRY',
          risk: entryRisk,
          queue: entryQueue,
          decision: `Security ${oldSec}→${securityGates}, Vendors ${oldVend}→${vendors}`,
          security: securityGates,
          entry: entryGates,
          exit: exitGates,
          vendors: vendors
        });
      }
    });
  }

  // Calculate summary stats
  const avgSecurityWait = data.reduce((sum, d) => sum + d.avg_security_wait, 0) / data.length;
  const avgTurnstileWait = data.reduce((sum, d) => sum + d.avg_turnstile_wait, 0) / data.length;
  const avgExitWait = data.filter(d => d.exit_queue > 0).reduce((sum, d) => sum + d.avg_exit_wait, 0) / 
                      Math.max(1, data.filter(d => d.exit_queue > 0).length);
  const maxQueue = Math.max(...data.map(d => d.security_queue + d.turnstile_queue));

  return {
    timeseries: data,
    actions: actions,
    summary: {
      totalFans: numFans,
      avgSecurityWait: avgSecurityWait.toFixed(1),
      avgTurnstileWait: avgTurnstileWait.toFixed(1),
      avgExitWait: avgExitWait.toFixed(1),
      maxEntryQueue: maxQueue,
      maxExitQueue: Math.max(...data.map(d => d.exit_queue)),
      totalActions: actions.length
    },
    resources: {
      initial: resources,
      final: { securityGates, turnstiles: entryGates, exitGates, vendors }
    }
  };
}

export default App;
