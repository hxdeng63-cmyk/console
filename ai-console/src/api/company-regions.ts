import request from '@/api/index'

export const getRegionsByCompany = (companyId: number | string) => request.get('/regions', { params: { company_id: companyId, page_size: 100 } })
