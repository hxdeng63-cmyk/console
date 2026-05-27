declare module '@/api/roles.js' {
  export function getRoles(params?: any): Promise<any>
  export function getRole(id: string | number): Promise<any>
  export function createRole(data: any): Promise<any>
  export function updateRole(id: string | number, data: any): Promise<any>
  export function deleteRole(id: string | number): Promise<any>
  export function getRoleUsers(id: string | number, params?: any): Promise<any[]>
  export function getRoleMenus(id: string | number): Promise<any>
  export function setRoleMenus(id: string | number, data: any[]): Promise<any>
  export function getRoleResources(id: string | number): Promise<any>
  export function setRoleResources(id: string | number, data: any[]): Promise<any>
}
