import { ref, computed, watch } from 'vue'

export interface DeviceNode {
  id: string
  name: string
  type: 'org' | 'road' | 'device' | 'organization' | 'group' | 'camera'
  parentId?: string
  online?: boolean
  status?: 'online' | 'offline'
  children?: DeviceNode[]
  [key: string]: any
}

export interface UseDeviceTreeOptions {
  data: DeviceNode[]
  mode?: 'radio' | 'checkbox'
  sessionStorageKey?: string
  defaultCheckedKeys?: string[]
}

export function useDeviceTree(options: UseDeviceTreeOptions) {
  const searchQuery = ref('')
  const expandedKeys = ref<Set<string>>(new Set())
  const selectedKeys = ref<Set<string>>(new Set())
  const checkedKeys = ref<Set<string>>(new Set(options.defaultCheckedKeys || []))
  const dataRef = ref<DeviceNode[]>(options.data)

  watch(
    () => options.data,
    (newData) => {
      dataRef.value = newData
    },
    { immediate: true }
  )

  watch(
    () => options.defaultCheckedKeys,
    (newKeys) => {
      checkedKeys.value = new Set(newKeys || [])
    },
    { deep: true }
  )

  const sessionKey = options.sessionStorageKey ?? 'device-tree-state'

  function loadExpandedState() {
    try {
      const saved = sessionStorage.getItem(sessionKey)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed)) {
          expandedKeys.value = new Set(parsed)
        }
      }
    } catch {
      // ignore parse errors
    }
  }

  function saveExpandedState() {
    try {
      sessionStorage.setItem(sessionKey, JSON.stringify([...expandedKeys.value]))
    } catch {
      // ignore storage errors
    }
  }

  function toggleExpand(key: string) {
    if (expandedKeys.value.has(key)) {
      expandedKeys.value.delete(key)
    } else {
      expandedKeys.value.add(key)
    }
    expandedKeys.value = new Set(expandedKeys.value)
    saveExpandedState()
  }

  function expandAll() {
    const keys = new Set<string>()
    function collectKeys(nodes: DeviceNode[]) {
      for (const node of nodes) {
        if (node.children?.length) {
          keys.add(node.id)
          collectKeys(node.children)
        }
      }
    }
    collectKeys(dataRef.value)
    expandedKeys.value = keys
    saveExpandedState()
  }

  function collapseAll() {
    expandedKeys.value = new Set()
    saveExpandedState()
  }

  function handleNodeClick(node: DeviceNode) {
    if (options.mode === 'radio') {
      selectedKeys.value = new Set([node.id])
    }
  }

  function handleNodeCheck(node: DeviceNode, checked: boolean) {
    if (options.mode === 'checkbox') {
      if (checked) {
        checkedKeys.value.add(node.id)
      } else {
        checkedKeys.value.delete(node.id)
      }
      checkedKeys.value = new Set(checkedKeys.value)
    }
  }

  function search(query: string) {
    searchQuery.value = query
  }

  const filteredData = computed(() => {
    if (!searchQuery.value) {
      return dataRef.value
    }

    const query = searchQuery.value.toLowerCase()

    function filterNodes(nodes: DeviceNode[]): DeviceNode[] {
      const result: DeviceNode[] = []
      for (const node of nodes) {
        const matches = node.name.toLowerCase().includes(query)
        const children = node.children ? filterNodes(node.children) : []
        if (matches || children.length > 0) {
          result.push({
            ...node,
            children: children.length > 0 ? children : node.children,
          })
          if (matches && !expandedKeys.value.has(node.id)) {
            expandedKeys.value.add(node.id)
          }
        }
      }
      return result
    }

    return filterNodes(dataRef.value)
  })

  watch(
    () => options.data,
    () => {
      loadExpandedState()
    },
    { immediate: true }
  )

  return {
    searchQuery,
    expandedKeys,
    selectedKeys,
    checkedKeys,
    filteredData,
    toggleExpand,
    expandAll,
    collapseAll,
    handleNodeClick,
    handleNodeCheck,
    search,
    loadExpandedState,
  }
}
