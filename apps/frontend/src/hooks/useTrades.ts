import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { tradeAPI } from '../services/api';

export const useTrades = () => {
  return useQuery({
    queryKey: ['trades'],
    queryFn: tradeAPI.getTrades,
  });
};

export const useTrade = (tradeId: string) => {
  return useQuery({
    queryKey: ['trades', tradeId],
    queryFn: () => tradeAPI.getTrade(tradeId),
    enabled: !!tradeId,
  });
};

export const useCaptureTrade = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: tradeAPI.captureTrade,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trades'] });
    },
  });
};

export const useValidateTrade = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: tradeAPI.validateTrade,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trades'] });
    },
  });
};

export const useSettleTrade = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: tradeAPI.settleTrade,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trades'] });
    },
  });
};
