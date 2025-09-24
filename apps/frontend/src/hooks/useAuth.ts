import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authAPI } from '../services/api';

export const useLogin = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      authAPI.login(username, password),
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
};

export const useMe = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: authAPI.getMe,
    enabled: !!localStorage.getItem('access_token'),
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  
  return () => {
    localStorage.removeItem('access_token');
    queryClient.clear();
  };
};
