/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../../components/Dashboard';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Dashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue('mock-token');
  });

  it('renders dashboard correctly', () => {
    mockedAxios.get.mockResolvedValue({ data: [] });
    
    renderWithProviders(<Dashboard />);
    
    expect(screen.getByText('QuantaEnergi Dashboard')).toBeInTheDocument();
    expect(screen.getByText('New Trade')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
    expect(screen.getByText('Compliance')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  it('displays loading state while fetching trades', () => {
    mockedAxios.get.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderWithProviders(<Dashboard />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('displays error state when trades fetch fails', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Failed to fetch trades'));
    
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading trades')).toBeInTheDocument();
    });
  });

  it('displays trades when data is loaded', async () => {
    const mockTrades = [
      {
        id: 'trade-1',
        trade_id: 'T001',
        commodity: 'electricity',
        quantity: 100,
        price: 50.0,
        status: 'captured'
      },
      {
        id: 'trade-2',
        trade_id: 'T002',
        commodity: 'solar_energy',
        quantity: 200,
        price: 45.0,
        status: 'validated'
      }
    ];
    
    mockedAxios.get.mockResolvedValue({ data: mockTrades });
    
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Recent Trades')).toBeInTheDocument();
      expect(screen.getByText('T001')).toBeInTheDocument();
      expect(screen.getByText('T002')).toBeInTheDocument();
      expect(screen.getByText('electricity')).toBeInTheDocument();
      expect(screen.getByText('solar_energy')).toBeInTheDocument();
    });
  });

  it('displays empty state when no trades', async () => {
    mockedAxios.get.mockResolvedValue({ data: [] });
    
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('No trades found. Create your first trade!')).toBeInTheDocument();
      expect(screen.getByText('Create Trade')).toBeInTheDocument();
    });
  });

  it('navigates to trade form when New Trade button is clicked', () => {
    mockedAxios.get.mockResolvedValue({ data: [] });
    
    renderWithProviders(<Dashboard />);
    
    const newTradeButton = screen.getByText('New Trade');
    fireEvent.click(newTradeButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/trade');
  });

  it('navigates to analytics when Analytics button is clicked', () => {
    mockedAxios.get.mockResolvedValue({ data: [] });
    
    renderWithProviders(<Dashboard />);
    
    const analyticsButton = screen.getByText('Analytics');
    fireEvent.click(analyticsButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/analytics');
  });

  it('navigates to compliance when Compliance button is clicked', () => {
    mockedAxios.get.mockResolvedValue({ data: [] });
    
    renderWithProviders(<Dashboard />);
    
    const complianceButton = screen.getByText('Compliance');
    fireEvent.click(complianceButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/compliance');
  });

  it('handles logout correctly', () => {
    mockedAxios.get.mockResolvedValue({ data: [] });
    
    renderWithProviders(<Dashboard />);
    
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);
    
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('calls trades API with correct headers', async () => {
    mockedAxios.get.mockResolvedValue({ data: [] });
    
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/trades',
        {
          headers: {
            'Authorization': 'Bearer mock-token'
          }
        }
      );
    });
  });

  it('navigates to trade form from empty state', async () => {
    mockedAxios.get.mockResolvedValue({ data: [] });
    
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      const createTradeButton = screen.getByText('Create Trade');
      fireEvent.click(createTradeButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/trade');
    });
  });
});
