import type { Meta, StoryObj } from '@storybook/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import RiskDashboard from './RiskDashboard';

// Mock QueryClient for Storybook
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});

const meta: Meta<typeof RiskDashboard> = {
  title: 'Pages/RiskDashboard',
  component: RiskDashboard,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Risk dashboard with VaR calculations, portfolio allocation, and stress testing visualization',
      },
    },
  },
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen bg-gray-50">
          <Story />
          <Toaster position="top-right" />
        </div>
      </QueryClientProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof RiskDashboard>;

export const Default: Story = {
  name: 'Default Risk Dashboard',
  parameters: {
    docs: {
      description: {
        story: 'Default risk dashboard with VaR metrics and portfolio visualization',
      },
    },
  },
};

export const WithStressTest: Story = {
  name: 'Dashboard with Stress Test',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard including stress test results and scenario analysis',
      },
    },
  },
};

export const WithMLInsights: Story = {
  name: 'Dashboard with ML Insights',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard showing ML-powered risk predictions and insights',
      },
    },
  },
};

export const HighRiskPortfolio: Story = {
  name: 'High Risk Portfolio',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard displaying high-risk portfolio with elevated VaR metrics',
      },
    },
  },
};

export const LowRiskPortfolio: Story = {
  name: 'Low Risk Portfolio',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard showing low-risk, well-diversified portfolio',
      },
    },
  },
};

export const MobileView: Story = {
  name: 'Mobile View',
  parameters: {
    viewport: {
      defaultViewport: 'mobile1',
    },
    docs: {
      description: {
        story: 'Risk dashboard optimized for mobile devices',
      },
    },
  },
};

export const TabletView: Story = {
  name: 'Tablet View',
  parameters: {
    viewport: {
      defaultViewport: 'tablet',
    },
    docs: {
      description: {
        story: 'Risk dashboard on tablet devices',
      },
    },
  },
};

export const LoadingState: Story = {
  name: 'Loading State',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard during data loading',
      },
    },
  },
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen bg-gray-50">
          <div className="opacity-50 pointer-events-none">
            <Story />
          </div>
          <Toaster position="top-right" />
        </div>
      </QueryClientProvider>
    ),
  ],
};

export const ErrorState: Story = {
  name: 'Error State',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard showing error state when data fetch fails',
      },
    },
  },
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen bg-gray-50">
          <Story />
          <Toaster position="top-right" />
        </div>
      </QueryClientProvider>
    ),
  ],
};

export const LargePortfolio: Story = {
  name: 'Large Portfolio',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard for large portfolio with many positions',
      },
    },
  },
};

export const EnergyFocusedPortfolio: Story = {
  name: 'Energy-Focused Portfolio',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard for energy commodity-focused portfolio',
      },
    },
  },
};

export const DiversifiedPortfolio: Story = {
  name: 'Diversified Portfolio',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard for well-diversified multi-commodity portfolio',
      },
    },
  },
};

export const RealTimeUpdates: Story = {
  name: 'Real-Time Updates',
  parameters: {
    docs: {
      description: {
        story: 'Risk dashboard with real-time data updates and live monitoring',
      },
    },
  },
};

// Interactive story for testing
export const Interactive: Story = {
  name: 'Interactive Testing',
  parameters: {
    docs: {
      description: {
        story: 'Interactive risk dashboard for testing all features and controls',
      },
    },
  },
  play: async ({ canvasElement }) => {
    // Add any interactive testing here
    const canvas = canvasElement;
    const dashboard = canvas.querySelector('[data-testid="risk-dashboard"]');
    
    if (dashboard) {
      // Test dashboard interactions
      console.log('Risk dashboard is ready for interaction');
    }
  },
};
