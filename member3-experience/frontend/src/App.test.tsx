import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { CabHeader } from './components/layout/CabHeader';
import { ConsequenceGraph } from './components/trajectory/ConsequenceGraph';
import { BrowserRouter } from 'react-router-dom';

describe('CabHeader Component', () => {
  it('renders brand and balanced cockpit mode', () => {
    render(
      <BrowserRouter>
        <CabHeader attentionMode="NORMAL" operatorId="OP1001" machineId="EXC-CAT-349D" />
      </BrowserRouter>
    );
    expect(screen.getByText('CAT')).toBeTruthy();
    expect(screen.getByText(/operator shift twin/i)).toBeTruthy();
    expect(screen.getByText('BALANCED COCKPIT')).toBeTruthy();
  });

  it('renders DECISION_FOCUS badge correctly', () => {
    render(
      <BrowserRouter>
        <CabHeader attentionMode="DECISION_FOCUS" operatorId="OP1001" machineId="EXC-CAT-349D" />
      </BrowserRouter>
    );
    expect(screen.getByText('DECISION FOCUS')).toBeTruthy();
  });
});

describe('ConsequenceGraph Component', () => {
  it('renders consequence graph nodes with causal flow', () => {
    const mockGraph = {
      graph_id: 'DAG-SCEN-02',
      scenario_id: 'SCEN-02-RESEQUENCE',
      root_action: 'Resequence to Upper Bench 3',
      summary: 'Resequencing avoids 17-min crusher wait and saves fuel.',
      nodes: [
        {
          node_id: 'NODE-01',
          type: 'TASK_EFFECT' as const,
          title: 'Hauler Queue Increase',
          value: '+3 Trucks Waiting',
          unit: 'trucks',
          severity: 'WARNING' as const,
          explanation: 'Truck arrival rate outpaced loading pace at primary crusher.',
        },
        {
          node_id: 'NODE-02',
          type: 'IDLE_EFFECT' as const,
          title: 'Projected Idle Elevation',
          value: '55 min low idle',
          unit: 'mins',
          severity: 'CRITICAL' as const,
          explanation: 'Operator forced to idle while waiting for switchovers.',
        },
      ],
      edges: [
        {
          source: 'NODE-01',
          target: 'NODE-02',
          relationship: 'INDUCED_WAIT',
          explanation: 'Crusher backup triggers immediate excavator idling.',
        },
      ],
    };

    render(<ConsequenceGraph graph={mockGraph} />);
    expect(screen.getByText('Operational Consequence Chain')).toBeTruthy();
    expect(screen.getByText('Resequencing avoids 17-min crusher wait and saves fuel.')).toBeTruthy();
    expect(screen.getByText('Hauler Queue Increase')).toBeTruthy();
    expect(screen.getByText('+3 Trucks Waiting')).toBeTruthy();
    expect(screen.getByText('Projected Idle Elevation')).toBeTruthy();
  });
});

