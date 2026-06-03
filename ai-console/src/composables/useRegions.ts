import { ref, computed } from 'vue'
import { getFullRegionTree } from '@/api/regions'

export interface RegionNode {
  id: number
  name: string
  code?: string
  isCompany?: boolean
  isRegion?: boolean
  level?: number
  org_id?: number
  parent_id?: number
  children?: RegionNode[]
}

export const useRegions = () => {
  const treeData = ref<RegionNode[]>([])
  const loaded = ref(false)

  const loadRegions = async () => {
    if (loaded.value) return
    const res = await getFullRegionTree()
    treeData.value = res || []
    loaded.value = true
  }

  const companies = computed(() => treeData.value.filter(n => n.isCompany))

  const collectRegions = (nodes: RegionNode[], predicate: (n: RegionNode) => boolean): RegionNode[] => {
    const regions: RegionNode[] = []
    const walk = (items: RegionNode[]) => {
      for (const node of items) {
        if (predicate(node)) regions.push(node)
        if (node.children) walk(node.children)
      }
    }
    walk(nodes)
    return regions
  }

  const level1Regions = computed(() =>
    collectRegions(treeData.value, n => !!n.isRegion && n.level === 1)
  )

  const allRegions = computed(() =>
    collectRegions(treeData.value, n => !!n.isRegion)
  )

  const getRegionWithDescendants = (regionId: number): number[] => {
    const findNode = (nodes: RegionNode[]): RegionNode | null => {
      for (const node of nodes) {
        if (node.id === regionId) return node
        if (node.children) {
          const found = findNode(node.children)
          if (found) return found
        }
      }
      return null
    }
    const collectIds = (node: RegionNode): number[] => {
      const ids = [node.id]
      if (node.children) {
        for (const child of node.children) {
          ids.push(...collectIds(child))
        }
      }
      return ids
    }
    const target = findNode(treeData.value)
    return target ? collectIds(target) : []
  }

  return {
    treeData,
    companies,
    level1Regions,
    allRegions,
    loadRegions,
    loaded,
    getRegionWithDescendants
  }
}
