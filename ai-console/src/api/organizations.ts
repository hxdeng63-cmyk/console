import request from './index'

export const getOrganizationTree = () => request.get('/organizations/tree')
