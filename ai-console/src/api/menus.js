import request from './index'
import { menuList } from '@/mock/super-admin/menu.js'

// ---- Mock 数据适配（远程对接前的桥接层） ----

const MOCK_DELAY = 120

let mockSeed = JSON.parse(JSON.stringify(menuList)).map(mapMockToApi)

function mapMockToApi(item) {
  return {
    id: item.id,
    name: item.routeName ?? item.name ?? '',
    path: item.routePath ?? item.path ?? '',
    hidden: item.isHidden === '隐藏' || item.hidden === true,
    parentId: item.parentId ?? 0,
    sort: item.sort ?? 0,
    component: item.filePath ?? item.component ?? '',
    title: item.name ?? item.title ?? '',
    icon: item.icon ?? '',
    keepAlive: item.keepAlive ?? false
  }
}

function buildTree(list) {
  const map = new Map()
  const roots = []
  list.forEach(item => map.set(item.id, { ...item, children: [] }))
  map.forEach(node => {
    if (node.parentId && map.has(node.parentId)) {
      map.get(node.parentId).children.push(node)
    } else {
      roots.push(node)
    }
  })
  const sortRecursive = (nodes) => {
    nodes.sort((a, b) => (a.sort ?? 0) - (b.sort ?? 0))
    nodes.forEach(n => n.children?.length && sortRecursive(n.children))
  }
  sortRecursive(roots)
  return roots
}

function delay(value) {
  return new Promise(resolve => setTimeout(() => resolve(value), MOCK_DELAY))
}

// ---- 对外 API ----

export const getMenus = () => delay(buildTree(mockSeed))

export const getMenu = (id) => {
  const item = mockSeed.find(m => m.id === id)
  return delay(item ?? null)
}

export const createMenu = (data) => {
  const nextId = Math.max(0, ...mockSeed.map(m => m.id)) + 1
  const record = mapMockToApi({
    ...data,
    id: nextId,
    routeName: data.name,
    routePath: data.path,
    filePath: data.component,
    isHidden: data.hidden ? '隐藏' : '显示',
    parentId: data.parent_id ?? data.parentId ?? 0,
    keepAlive: data.keep_alive ?? data.keepAlive ?? false
  })
  mockSeed.push(record)
  return delay(record)
}

export const updateMenu = (id, data) => {
  const idx = mockSeed.findIndex(m => m.id === id)
  if (idx === -1) return delay(null)
  mockSeed[idx] = {
    ...mockSeed[idx],
    name: data.name ?? mockSeed[idx].name,
    path: data.path ?? mockSeed[idx].path,
    hidden: data.hidden ?? mockSeed[idx].hidden,
    parentId: data.parent_id ?? data.parentId ?? mockSeed[idx].parentId,
    sort: data.sort ?? mockSeed[idx].sort,
    component: data.component ?? mockSeed[idx].component,
    title: data.title ?? mockSeed[idx].title,
    icon: data.icon ?? mockSeed[idx].icon,
    keepAlive: data.keep_alive ?? data.keepAlive ?? mockSeed[idx].keepAlive
  }
  return delay(mockSeed[idx])
}

export const deleteMenu = (id) => {
  const idx = mockSeed.findIndex(m => m.id === id)
  if (idx !== -1) mockSeed.splice(idx, 1)
  // 级联删除子节点
  const collectDescendants = (parentId) => {
    const directChildren = mockSeed.filter(m => m.parentId === parentId)
    directChildren.forEach(c => {
      collectDescendants(c.id)
      const i = mockSeed.findIndex(m => m.id === c.id)
      if (i !== -1) mockSeed.splice(i, 1)
    })
  }
  collectDescendants(id)
  return delay(true)
}

export const getMenuTree = () => delay(buildTree(mockSeed))
export const getMenuButtons = (id) => request.get(`/menus/${id}/buttons`)
export const updateMenuButtons = (id, data) => request.put(`/menus/${id}/buttons`, data)
