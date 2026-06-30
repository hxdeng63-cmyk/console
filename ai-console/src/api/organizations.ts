import request from '@/api/index'

export const getOrganizationTree = () => request.get('/organizations/tree')
