import request from './index'

export const getMicroservices = (params = {}) => {
  const { pageNo = 1, pageSize = 10, keyword } = params
  return request.get('/microservices', {
    params: {
      page: pageNo,
      page_size: pageSize,
      keyword: keyword || undefined
    }
  })
}

export const getMicroservice = (id) => request.get(`/microservices/${id}`)

export const createMicroservice = (data) => request.post('/microservices', data)

export const updateMicroservice = (id, data) => request.put(`/microservices/${id}`, data)

export const deleteMicroservice = (id) => request.delete(`/microservices/${id}`)
