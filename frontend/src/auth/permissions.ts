import { Role } from '../types/user';

export const PERMISSIONS = {
  CAN_CREATE_EXECUTION: [Role.ADMIN, Role.ANALISTA],
  CAN_APPROVE_CANDIDATE: [Role.ADMIN, Role.ANALISTA],
  CAN_VIEW_DASHBOARD: [Role.ADMIN, Role.ANALISTA, Role.AUDITOR],
  CAN_VIEW_AUDIT: [Role.ADMIN, Role.ANALISTA, Role.AUDITOR],
};

export const hasPermission = (userRole: Role, allowedRoles: Role[]) => {
  return allowedRoles.includes(userRole);
};
