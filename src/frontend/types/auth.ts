/**
 * Authentication Types for QuantaEnergi Frontend
 * TypeScript interfaces for user authentication and authorization
 */

export interface User {
  user_id: string;
  username: string;
  email: string;
  full_name: string;
  company: string;
  roles: string[];
  permissions?: string[];
  is_active: boolean;
  created_at: string;
  last_login?: string;
  phone?: string;
  country?: string;
  timezone?: string;
  profile_image?: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  currency: string;
  notifications: NotificationSettings;
  trading: TradingPreferences;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  sms: boolean;
  trading_alerts: boolean;
  risk_alerts: boolean;
  system_updates: boolean;
}

export interface TradingPreferences {
  default_asset: string;
  risk_tolerance: 'low' | 'medium' | 'high';
  trading_hours: string;
  auto_execute: boolean;
  confirmation_required: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
  company: string;
  phone?: string;
  country?: string;
  timezone?: string;
  agree_to_terms: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface ProfileUpdateRequest {
  full_name?: string;
  email?: string;
  phone?: string;
  country?: string;
  timezone?: string;
  preferences?: Partial<UserPreferences>;
}

// Role and Permission constants
export const ROLES = {
  ADMIN: 'admin',
  TRADER: 'trader',
  COMPLIANCE: 'compliance',
  RISK_MANAGER: 'risk_manager',
  OPERATIONS: 'operations',
  VIEWER: 'viewer',
} as const;

export const PERMISSIONS = {
  // Trading permissions
  TRADE_EXECUTE: 'trade:execute',
  TRADE_VIEW: 'trade:view',
  TRADE_MODIFY: 'trade:modify',
  TRADE_CANCEL: 'trade:cancel',
  
  // Risk management permissions
  RISK_VIEW: 'risk:view',
  RISK_MODIFY: 'risk:modify',
  RISK_OVERRIDE: 'risk:override',
  
  // Compliance permissions
  COMPLIANCE_VIEW: 'compliance:view',
  COMPLIANCE_APPROVE: 'compliance:approve',
  COMPLIANCE_REJECT: 'compliance:reject',
  
  // User management permissions
  USER_VIEW: 'user:view',
  USER_CREATE: 'user:create',
  USER_MODIFY: 'user:modify',
  USER_DELETE: 'user:delete',
  
  // System permissions
  SYSTEM_VIEW: 'system:view',
  SYSTEM_MODIFY: 'system:modify',
  SYSTEM_ADMIN: 'system:admin',
  
  // Reports permissions
  REPORTS_VIEW: 'reports:view',
  REPORTS_EXPORT: 'reports:export',
  REPORTS_SCHEDULE: 'reports:schedule',
} as const;

// Role hierarchy and default permissions
export const ROLE_PERMISSIONS: Record<string, string[]> = {
  [ROLES.ADMIN]: [
    PERMISSIONS.TRADE_EXECUTE,
    PERMISSIONS.TRADE_VIEW,
    PERMISSIONS.TRADE_MODIFY,
    PERMISSIONS.TRADE_CANCEL,
    PERMISSIONS.RISK_VIEW,
    PERMISSIONS.RISK_MODIFY,
    PERMISSIONS.RISK_OVERRIDE,
    PERMISSIONS.COMPLIANCE_VIEW,
    PERMISSIONS.COMPLIANCE_APPROVE,
    PERMISSIONS.COMPLIANCE_REJECT,
    PERMISSIONS.USER_VIEW,
    PERMISSIONS.USER_CREATE,
    PERMISSIONS.USER_MODIFY,
    PERMISSIONS.USER_DELETE,
    PERMISSIONS.SYSTEM_VIEW,
    PERMISSIONS.SYSTEM_MODIFY,
    PERMISSIONS.SYSTEM_ADMIN,
    PERMISSIONS.REPORTS_VIEW,
    PERMISSIONS.REPORTS_EXPORT,
    PERMISSIONS.REPORTS_SCHEDULE,
  ],
  [ROLES.TRADER]: [
    PERMISSIONS.TRADE_EXECUTE,
    PERMISSIONS.TRADE_VIEW,
    PERMISSIONS.TRADE_MODIFY,
    PERMISSIONS.TRADE_CANCEL,
    PERMISSIONS.RISK_VIEW,
    PERMISSIONS.REPORTS_VIEW,
    PERMISSIONS.REPORTS_EXPORT,
  ],
  [ROLES.COMPLIANCE]: [
    PERMISSIONS.TRADE_VIEW,
    PERMISSIONS.RISK_VIEW,
    PERMISSIONS.COMPLIANCE_VIEW,
    PERMISSIONS.COMPLIANCE_APPROVE,
    PERMISSIONS.COMPLIANCE_REJECT,
    PERMISSIONS.REPORTS_VIEW,
    PERMISSIONS.REPORTS_EXPORT,
  ],
  [ROLES.RISK_MANAGER]: [
    PERMISSIONS.TRADE_VIEW,
    PERMISSIONS.RISK_VIEW,
    PERMISSIONS.RISK_MODIFY,
    PERMISSIONS.RISK_OVERRIDE,
    PERMISSIONS.REPORTS_VIEW,
    PERMISSIONS.REPORTS_EXPORT,
  ],
  [ROLES.OPERATIONS]: [
    PERMISSIONS.TRADE_VIEW,
    PERMISSIONS.RISK_VIEW,
    PERMISSIONS.REPORTS_VIEW,
    PERMISSIONS.REPORTS_EXPORT,
  ],
  [ROLES.VIEWER]: [
    PERMISSIONS.TRADE_VIEW,
    PERMISSIONS.RISK_VIEW,
    PERMISSIONS.REPORTS_VIEW,
  ],
};

// Authentication context type
export interface AuthContextType {
  authState: AuthState;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (profileData: Partial<User>) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  requestPasswordReset: (email: string) => Promise<void>;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  hasPermission: (permission: string) => boolean;
  refreshToken: () => Promise<void>;
}

// API response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
  timestamp: string;
}

// Form validation types
export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface FormState<T> {
  data: T;
  errors: ValidationError[];
  isSubmitting: boolean;
  isValid: boolean;
}
