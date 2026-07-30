export enum Role {
  ADMIN = "ADMIN",
  ANALISTA = "ANALISTA",
  AUDITOR = "AUDITOR"
}

export interface User {
  id: string;
  email: string;
  nome: string;
  role: Role;
}
