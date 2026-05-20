import request from './index'
import { resourceList } from '@/mock/super-admin/resource.js'

const MOCK_DELAY = 120

let mockSeed = JSON.parse(JSON.stringify(resourceList))

function delay(value) {
  return new Promise(resolve => setTimeout(() => resolve(value), MOCK_DELAY))
}

function paginate(list, pageNo = 1, pageSize = 10) {
  const start = (pageNo - 1) * pageSize
  return {
    list: list.slice(start, start + pageSize),
    total: list.length,
    pageNo,
    pageSize
  }
}

function filterList(list, params = {}) {
  const { resource, resourceGroup, serviceCode, method } = params
  return list.filter(item => {
    if (resource && !item.resource.toLowerCase().includes(resource.toLowerCase())) return false
    if (resourceGroup && !item.resourceGroup.toLowerCase().includes(resourceGroup.toLowerCase())) return false
    if (serviceCode && item.serviceCode !== serviceCode) return false
    if (method && item.method !== method) return false
    return true
  })
}

function buildTree(list) {
  const groups = new Map()
  list.forEach(item => {
    const key = `${item.serviceCode}-${item.resource}`
    if (!groups.has(key)) {
      groups.set(key, {
        id: key,
        resource: item.resource,
        serviceCode: item.serviceCode,
        resourceGroup: item.resourceGroup,
        isParent: true,
        children: []
      })
    }
    groups.get(key).children.push({ ...item, parentResource: item.resource })
  })
  return Array.from(groups.values())
}

export const getResources = (params = {}) => {
  const { pageNo = 1, pageSize = 10, ...filters } = params
  const filtered = filterList(mockSeed, filters)
  const treeList = buildTree(filtered)
  return delay({ code: 0, data: paginate(treeList, pageNo, pageSize), msg: '操作成功' })
}

export const getResource = (id) => {
  const item = mockSeed.find(m => m.id === id)
  return delay({ code: 0, data: item ?? null, msg: '操作成功' })
}

export const createResource = (data) => {
  const record = {
    id: crypto.randomUUID().replace(/-/g, ''),
    resource: data.resource ?? '',
    resourceGroup: data.group ?? data.resourceGroup ?? '',
    method: data.method ?? 'GET',
    serviceCode: data.service ?? data.serviceCode ?? '',
    description: data.description ?? '',
    hidden: data.hidden ?? false,
    createdAt: new Date().toISOString().replace('T', ' ').slice(0, 19),
    updatedAt: new Date().toISOString().replace('T', ' ').slice(0, 19)
  }
  mockSeed.push(record)
  return delay({ code: 0, data: record, msg: '操作成功' })
}

export const updateResource = (id, data) => {
  const idx = mockSeed.findIndex(m => m.id === id)
  if (idx === -1) return delay({ code: 1, msg: '资源不存在' })
  mockSeed[idx] = {
    ...mockSeed[idx],
    resource: data.resource ?? mockSeed[idx].resource,
    resourceGroup: data.group ?? data.resourceGroup ?? mockSeed[idx].resourceGroup,
    method: data.method ?? mockSeed[idx].method,
    serviceCode: data.service ?? data.serviceCode ?? mockSeed[idx].serviceCode,
    description: data.description ?? mockSeed[idx].description,
    hidden: data.hidden ?? mockSeed[idx].hidden,
    updatedAt: new Date().toISOString().replace('T', ' ').slice(0, 19)
  }
  return delay({ code: 0, data: mockSeed[idx], msg: '操作成功' })
}

export const deleteResource = (id) => {
  const idx = mockSeed.findIndex(m => m.id === id)
  if (idx !== -1) mockSeed.splice(idx, 1)
  return delay({ code: 0, msg: '删除成功' })
}

export const getResourceTree = () => delay({ code: 0, data: [], msg: '操作成功' })
export const getResourceButtons = (id) => request.get(`/resources/${id}/buttons`)
export const updateResourceButtons = (id, data) => request.put(`/resources/${id}/buttons`, data)
