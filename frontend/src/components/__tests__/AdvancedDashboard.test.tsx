import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProductionDashboard from '../ProductionDashboard';

// Mock Recharts components
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  RadarChart: ({ children }: any) => <div data-testid="radar-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  Area: () => <div data-testid="area" />,
  Bar: () => <div data-testid="bar" />,
  Pie: () => <div data-testid="pie" />,
  Radar: () => <div data-testid="radar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  Cell: () => <div data-testid="cell" />,
  PolarGrid: () => <div data-testid="polar-grid" />,
  PolarAngleAxis: () => <div data-testid="polar-angle-axis" />,
  PolarRadiusAxis: () => <div data-testid="polar-radius-axis" />
}));

describe('ProductionDashboard', () => {
  beforeEach(() => {
    // Mock console methods to avoid test output noise
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders the dashboard header correctly', () => {
    render(<ProductionDashboard />);
    
    expect(screen.getByText('QuantaEnergi Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Welcome back, Trader')).toBeInTheDocument();
  });

  it('renders all navigation tabs', () => {
    render(<ProductionDashboard />);
    
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Trading')).toBeInTheDocument();
    expect(screen.getByText('Risk Analytics')).toBeInTheDocument();
    expect(screen.getByText('Quantum')).toBeInTheDocument();
    expect(screen.getByText('Blockchain')).toBeInTheDocument();
    expect(screen.getByText('Compliance')).toBeInTheDocument();
    expect(screen.getByText('ESG')).toBeInTheDocument();
  });

  it('switches between tabs correctly', async () => {
    render(<ProductionDashboard />);
    
    // Click on Quantum tab
    fireEvent.click(screen.getByText('Quantum'));
    
    await waitFor(() => {
      expect(screen.getByText('Quantum Optimization Comparison')).toBeInTheDocument();
    });
  });

  it('displays key metrics in overview tab', () => {
    render(<ProductionDashboard />);
    
    expect(screen.getByText('VaR 95%')).toBeInTheDocument();
    expect(screen.getByText('VaR 99%')).toBeInTheDocument();
    expect(screen.getByText('Max Drawdown')).toBeInTheDocument();
    expect(screen.getByText('Sharpe Ratio')).toBeInTheDocument();
  });

  it('renders charts in overview tab', () => {
    render(<ProductionDashboard />);
    
    expect(screen.getByTestId('area-chart')).toBeInTheDocument();
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });

  it('displays quantum optimization content when quantum tab is selected', async () => {
    render(<ProductionDashboard />);
    
    fireEvent.click(screen.getByText('Quantum'));
    
    await waitFor(() => {
      expect(screen.getByText('Quantum Optimization Comparison')).toBeInTheDocument();
      expect(screen.getByText('Quantum Advantage')).toBeInTheDocument();
      expect(screen.getByText('Optimization Status')).toBeInTheDocument();
    });
  });

  it('displays blockchain content when blockchain tab is selected', async () => {
    render(<ProductionDashboard />);
    
    fireEvent.click(screen.getByText('Blockchain'));
    
    await waitFor(() => {
      expect(screen.getByText('Carbon NFTs')).toBeInTheDocument();
      expect(screen.getByText('Carbon Offset (tons)')).toBeInTheDocument();
      expect(screen.getByText('Total Value')).toBeInTheDocument();
    });
  });

  it('displays compliance content when compliance tab is selected', async () => {
    render(<ProductionDashboard />);
    
    fireEvent.click(screen.getByText('Compliance'));
    
    await waitFor(() => {
      expect(screen.getByText('REMIT')).toBeInTheDocument();
      expect(screen.getByText('FERC')).toBeInTheDocument();
      expect(screen.getByText('CFTC')).toBeInTheDocument();
      expect(screen.getByText('Islamic Finance')).toBeInTheDocument();
    });
  });

  it('displays ESG content when ESG tab is selected', async () => {
    render(<ProductionDashboard />);
    
    fireEvent.click(screen.getByText('ESG'));
    
    await waitFor(() => {
      expect(screen.getByText('ESG Performance')).toBeInTheDocument();
      expect(screen.getByText('Environmental Impact')).toBeInTheDocument();
      expect(screen.getByText('Social Impact')).toBeInTheDocument();
    });
  });

  it('shows portfolio performance chart', () => {
    render(<ProductionDashboard />);
    
    expect(screen.getByText('Portfolio Performance')).toBeInTheDocument();
    expect(screen.getByTestId('area-chart')).toBeInTheDocument();
  });

  it('shows asset allocation chart', () => {
    render(<ProductionDashboard />);
    
    expect(screen.getByText('Asset Allocation')).toBeInTheDocument();
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
  });

  it('shows market data chart', () => {
    render(<ProductionDashboard />);
    
    expect(screen.getByText('Market Data')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });
});
