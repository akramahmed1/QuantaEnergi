/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import LoginForm from '../../components/LoginForm';
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

describe('LoginForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  it('renders login form correctly', () => {
    renderWithProviders(<LoginForm />);
    
    expect(screen.getByText('Sign in to QuantaEnergi')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
  });

  it('updates form data when user types', () => {
    renderWithProviders(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText('Username');
    const passwordInput = screen.getByPlaceholderText('Password');
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    
    expect(usernameInput).toHaveValue('testuser');
    expect(passwordInput).toHaveValue('testpass');
  });

  it('shows loading state during login', async () => {
    // Mock a delayed response
    mockedAxios.post.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ data: { access_token: 'mock-token' } }), 100))
    );

    renderWithProviders(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText('Username');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });
    
    fireEvent.change(usernameInput, { target: { value: 'admin' } });
    fireEvent.change(passwordInput, { target: { value: 'secret' } });
    fireEvent.click(submitButton);
    
    expect(screen.getByText('Signing in...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  it('handles successful login', async () => {
    mockedAxios.post.mockResolvedValue({
      data: { access_token: 'mock-token', token_type: 'bearer' }
    });

    renderWithProviders(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText('Username');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });
    
    fireEvent.change(usernameInput, { target: { value: 'admin' } });
    fireEvent.change(passwordInput, { target: { value: 'secret' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', 'mock-token');
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('handles login error', async () => {
    mockedAxios.post.mockRejectedValue(new Error('Login failed'));

    renderWithProviders(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText('Username');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });
    
    fireEvent.change(usernameInput, { target: { value: 'admin' } });
    fireEvent.change(passwordInput, { target: { value: 'secret' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  it('calls login API with correct data', async () => {
    mockedAxios.post.mockResolvedValue({
      data: { access_token: 'mock-token', token_type: 'bearer' }
    });

    renderWithProviders(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText('Username');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });
    
    fireEvent.change(usernameInput, { target: { value: 'admin' } });
    fireEvent.change(passwordInput, { target: { value: 'secret' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/login',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
    });
  });

  it('prevents form submission with empty fields', () => {
    renderWithProviders(<LoginForm />);
    
    const submitButton = screen.getByRole('button', { name: 'Sign in' });
    fireEvent.click(submitButton);
    
    // Form should not submit with empty fields due to HTML5 validation
    expect(mockedAxios.post).not.toHaveBeenCalled();
  });
});
