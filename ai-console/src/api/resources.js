import request from './index'

export const getResources = (params = {}) => {
  const { pageNo = 1, pageSize = 10, resource, resourceGroup, serviceCode, method } = params
  return request.get('/resources', {
    params: {
      page: pageNo,
      page_size: pageSize,
      keyword: resource || undefined,
      resource_group: resourceGroup || undefined,
      method: method || undefined
    }
  })
}

export const getResource = (id) => request.get(`/resources/${id}`)

export const createResource = (data) => request.post('/resources', {
  resource: data.resource,
  resource_group: data.group ?? data.resourceGroup ?? '',
  method: data.method ?? 'GET',
  service_code: data.service ?? data.serviceCode ?? '',
  description: data.description ?? '',
  hidden: data.hidden ?? false
})

export const updateResource = (id, data) => request.put(`/resources/${id}`, {
  resource: data.resource,
  resource_group: data.group ?? data.resourceGroup ?? '',
  method: data.method,
  service_code: data.service ?? data.serviceCode ?? '',
  description: data.description,
  hidden: data.hidden
})

export const deleteResource = (id) => request.delete(`/resources/${id}`)

export const getResourceTree = () => request.get('/resources/tree')
export const getResourceButtons = (id) => request.get(`/resources/${id}/buttons`)
export const updateResourceButtons = (id, data) => request.put(`/resources/${id}/buttons`, data)
