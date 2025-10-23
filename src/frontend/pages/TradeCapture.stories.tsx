import type { Meta, StoryObj } from '@storybook/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import TradeCapture from './TradeCapture';

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

const meta: Meta<typeof TradeCapture> = {
  title: 'Pages/TradeCapture',
  component: TradeCapture,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Trade capture form for energy trading with forecast validation',
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
type Story = StoryObj<typeof TradeCapture>;

export const Default: Story = {
  name: 'Default Trade Capture Form',
  parameters: {
    docs: {
      description: {
        story: 'Default trade capture form with all fields empty',
      },
    },
  },
};

export const WithOilTrade: Story = {
  name: 'Oil Trade Example',
  parameters: {
    docs: {
      description: {
        story: 'Trade capture form pre-filled with oil trade data',
      },
    },
  },
  args: {
    // Note: This would need to be handled in the component if we want to pre-fill
  },
};

export const WithGasTrade: Story = {
  name: 'Gas Trade Example',
  parameters: {
    docs: {
      description: {
        story: 'Trade capture form for natural gas trading',
      },
    },
  },
};

export const WithAmendments: Story = {
  name: 'Trade with Amendments',
  parameters: {
    docs: {
      description: {
        story: 'Trade capture form showing amendments section',
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
        story: 'Trade capture form optimized for mobile devices',
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
        story: 'Trade capture form on tablet devices',
      },
    },
  },
};

export const LoadingState: Story = {
  name: 'Loading State',
  parameters: {
    docs: {
      description: {
        story: 'Trade capture form during submission',
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
        story: 'Trade capture form showing error state',
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

export const SuccessState: Story = {
  name: 'Success State',
  parameters: {
    docs: {
      description: {
        story: 'Trade capture form after successful submission',
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

// Interactive story for testing
export const Interactive: Story = {
  name: 'Interactive Testing',
  parameters: {
    docs: {
      description: {
        story: 'Interactive trade capture form for testing all features',
      },
    },
  },
  play: async ({ canvasElement }) => {
    // Add any interactive testing here
    const canvas = canvasElement;
    const form = canvas.querySelector('form');
    
    if (form) {
      // Test form interactions
      console.log('Trade capture form is ready for interaction');
    }
  },
};
