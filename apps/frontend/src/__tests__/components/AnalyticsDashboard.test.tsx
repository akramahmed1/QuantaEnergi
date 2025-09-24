/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import AnalyticsDashboard from '../../components/AnalyticsDashboard';
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

describe('AnalyticsDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue('mock-token');
  });

  it('renders analytics dashboard correctly', () => {
    renderWithProviders(<AnalyticsDashboard />);
    
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
    expect(screen.getByText('AI Price Forecasting')).toBeInTheDocument();
    expect(screen.getByText('Quantum Portfolio Optimization')).toBeInTheDocument();
    expect(screen.getByText('Blockchain & ESG')).toBeInTheDocument();
    expect(screen.getByText('Back to Dashboard')).toBeInTheDocument();
  });

  it('handles forecast generation', async () => {
    const mockForecastData = {
      forecast: [
        { ds: '2024-01-01', yhat: 50.0, yhat_lower: 45.0, yhat_upper: 55.0 },
        { ds: '2024-01-02', yhat: 52.0, yhat_lower: 47.0, yhat_upper: 57.0 }
      ],
      periods: 30,
      unit: 'USD/MWh'
    };

    const mockInsights = {
      sentiment: 'Bullish',
      risk_level: 'Low',
      recommendation: 'Consider Buying',
      price_change_percentage: '4.00%'
    };

    mockedAxios.post
      .mockResolvedValueOnce({ data: mockForecastData })
      .mockResolvedValueOnce({ data: mockInsights });

    renderWithProviders(<AnalyticsDashboard />);
    
    const generateButton = screen.getByText('Generate Forecast & Insights');
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText('Price Forecast')).toBeInTheDocument();
      expect(screen.getByText('Market Insights (Crude Oil)')).toBeInTheDocument();
      expect(screen.getByText('Sentiment: Bullish')).toBeInTheDocument();
      expect(screen.getByText('Risk Level: Low')).toBeInTheDocument();
    });
  });

  it('handles portfolio optimization', async () => {
    const mockOptimizationResult = {
      optimized_weights: [0.4, 0.3, 0.3],
      expected_return: 0.08,
      expected_volatility: 0.12,
      method: 'Quantum (QAOA)'
    };

    mockedAxios.post.mockResolvedValue({ data: mockOptimizationResult });

    renderWithProviders(<AnalyticsDashboard />);
    
    const returnsInput = screen.getByPlaceholderText('e.g., 0.1,0.05,0.08');
    const volatilitiesInput = screen.getByPlaceholderText('e.g., 0.2,0.1,0.15');
    const optimizeButton = screen.getByText('Optimize Portfolio');

    fireEvent.change(returnsInput, { target: { value: '0.1,0.05,0.08' } });
    fireEvent.change(volatilitiesInput, { target: { value: '0.2,0.1,0.15' } });
    fireEvent.click(optimizeButton);

    await waitFor(() => {
      expect(screen.getByText('Optimization Results (Quantum (QAOA))')).toBeInTheDocument();
      expect(screen.getByText('Expected Return: 8.00%')).toBeInTheDocument();
      expect(screen.getByText('Expected Volatility: 12.00%')).toBeInTheDocument();
    });
  });

  it('handles carbon trade creation', async () => {
    const mockCarbonTrade = {
      trade_id: 'carbon-trade-123',
      buyer_address: '0xBuyerMockAddress',
      seller_address: '0xSellerMockAddress',
      carbon_amount: 100,
      price: 25.5,
      status: 'pending'
    };

    mockedAxios.post.mockResolvedValue({ data: mockCarbonTrade });

    renderWithProviders(<AnalyticsDashboard />);
    
    const createTradeButton = screen.getByText('Create Carbon Trade');
    fireEvent.click(createTradeButton);

    await waitFor(() => {
      expect(screen.getByText('Trade ID: carbon-trade-123')).toBeInTheDocument();
    });
  });

  it('handles ESG score retrieval', async () => {
    const mockEsgScore = {
      score: 85,
      last_updated: '2024-01-01T00:00:00Z',
      details: 'Strong environmental policies'
    };

    mockedAxios.get.mockResolvedValue({ data: mockEsgScore });

    renderWithProviders(<AnalyticsDashboard />);
    
    const getEsgButton = screen.getByText('Get ESG Score');
    fireEvent.click(getEsgButton);

    await waitFor(() => {
      expect(screen.getByText('ESG Score: 85')).toBeInTheDocument();
      expect(screen.getByText('Details: Strong environmental policies')).toBeInTheDocument();
    });
  });

  it('validates portfolio optimization inputs', async () => {
    renderWithProviders(<AnalyticsDashboard />);
    
    const returnsInput = screen.getByPlaceholderText('e.g., 0.1,0.05,0.08');
    const volatilitiesInput = screen.getByPlaceholderText('e.g., 0.2,0.1,0.15');
    const optimizeButton = screen.getByText('Optimize Portfolio');

    // Test with mismatched array lengths
    fireEvent.change(returnsInput, { target: { value: '0.1,0.05' } });
    fireEvent.change(volatilitiesInput, { target: { value: '0.2,0.1,0.15' } });
    fireEvent.click(optimizeButton);

    await waitFor(() => {
      expect(screen.getByText('Please enter valid comma-separated numbers for returns and volatilities, and ensure they have the same length.')).toBeInTheDocument();
    });
  });

  it('handles forecast period changes', () => {
    renderWithProviders(<AnalyticsDashboard />);
    
    const periodInput = screen.getByDisplayValue('30');
    fireEvent.change(periodInput, { target: { value: '60' } });
    
    expect(periodInput).toHaveValue(60);
  });

  it('handles carbon trade form changes', () => {
    renderWithProviders(<AnalyticsDashboard />);
    
    const buyerInput = screen.getByPlaceholderText('Buyer Address');
    const sellerInput = screen.getByPlaceholderText('Seller Address');
    const amountInput = screen.getByPlaceholderText('Carbon Amount');
    const priceInput = screen.getByPlaceholderText('Price');

    fireEvent.change(buyerInput, { target: { value: '0xNewBuyer' } });
    fireEvent.change(sellerInput, { target: { value: '0xNewSeller' } });
    fireEvent.change(amountInput, { target: { value: '200' } });
    fireEvent.change(priceInput, { target: { value: '30.0' } });

    expect(buyerInput).toHaveValue('0xNewBuyer');
    expect(sellerInput).toHaveValue('0xNewSeller');
    expect(amountInput).toHaveValue(200);
    expect(priceInput).toHaveValue(30.0);
  });

  it('handles ESG company address changes', () => {
    renderWithProviders(<AnalyticsDashboard />);
    
    const companyInput = screen.getByDisplayValue('companyA_address');
    fireEvent.change(companyInput, { target: { value: 'companyB_address' } });
    
    expect(companyInput).toHaveValue('companyB_address');
  });

  it('navigates back to dashboard', () => {
    renderWithProviders(<AnalyticsDashboard />);
    
    const backButton = screen.getByText('Back to Dashboard');
    fireEvent.click(backButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('displays loading states correctly', async () => {
    mockedAxios.post.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderWithProviders(<AnalyticsDashboard />);
    
    const generateButton = screen.getByText('Generate Forecast & Insights');
    fireEvent.click(generateButton);
    
    expect(screen.getByText('Generating...')).toBeInTheDocument();
    expect(generateButton).toBeDisabled();
  });

  it('handles API errors gracefully', async () => {
    mockedAxios.post.mockRejectedValue(new Error('API Error'));

    renderWithProviders(<AnalyticsDashboard />);
    
    const generateButton = screen.getByText('Generate Forecast & Insights');
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText('Error: API Error')).toBeInTheDocument();
    });
  });
});
