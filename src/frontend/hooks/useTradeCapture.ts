/**
 * Trade Capture Hook - TanStack Query integration
 * Custom hook for trade capture API calls
 */

import { useMutation } from '@tanstack/react-query';

interface TradeCaptureData {
  asset: string;
  volume: number;
  price: number;
  region: string;
  amendments?: Array<{ type: string; value: number }>;
}

interface TradeCaptureResponse {
  trade_id: string;
  status: string;
  message: string;
  timestamp: string;
}

const captureTrade = async (data: TradeCaptureData): Promise<TradeCaptureResponse> => {
  const response = await fetch('/api/v1/trade/capture', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Trade capture failed: ${response.status}`);
  }

  return response.json();
};

export const useCaptureTrade = () => {
  return useMutation({
    mutationFn: captureTrade,
    onSuccess: (data) => {
      console.log('Trade captured successfully:', data);
    },
    onError: (error) => {
      console.error('Trade capture failed:', error);
    },
  });
};
