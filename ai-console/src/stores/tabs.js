import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTabsStore = () => {
  const tabs = ref([])
  const active = ref('')
  // Per-tab navigation history: tab path -> array of previous paths
  const tabHistory = ref({})

  function addTab(tab) {
    const existing = tabs.value.find(t => t.path === tab.path)
    if (existing) {
      existing.label = tab.label
      active.value = tab.path
      return
    }
    if (tabs.value.length >= 10) {
      const oldest = tabs.value.shift()
      delete tabHistory.value[oldest.path]
      if (active.value === oldest.path) {
        active.value = tabs.value.length > 0 ? tabs.value[tabs.value.length - 1].path : ''
      }
    }
    tabs.value.push(tab)
    active.value = tab.path
    // Initialize history stack for this tab
    if (!tabHistory.value[tab.path]) {
      tabHistory.value[tab.path] = []
    }
  }

  function removeTab(path) {
    const idx = tabs.value.findIndex(t => t.path === path)
    if (idx === -1) return

    const hist = tabHistory.value[path] || []
    delete tabHistory.value[path]
    tabs.value.splice(idx, 1)

    if (active.value === path) {
      if (tabs.value.length > 0) {
        // Navigate to the last path in this tab's history (hierarchical fallback)
        const nextIdx = Math.min(idx, tabs.value.length - 1)
        const nextTab = tabs.value[nextIdx]
        const nextHist = tabHistory.value[nextTab.path] || []
        if (nextHist.length > 0) {
          // Pop the last visited path for this tab and navigate to it
          const prevPath = nextHist.pop()
          active.value = nextTab.path
          return { navigate: prevPath, activeTab: nextTab.path, activeHist: nextHist }
        } else {
          active.value = nextTab.path
          return { navigate: nextTab.path, activeTab: nextTab.path, activeHist: [] }
        }
      } else {
        active.value = ''
        return { navigate: '/', activeTab: '', activeHist: [] }
      }
    }
    return null
  }

  function setActive(path) {
    active.value = path
  }

  // Called when user navigates within a tab (router push)
  // Saves current path to the tab's history stack before navigating
  function pushHistory(path) {
    if (!tabHistory.value[path]) {
      tabHistory.value[path] = []
    }
  }

  // Called before switching away from current tab
  function saveCurrentToHistory(currentPath) {
    if (currentPath && tabHistory.value[currentPath]) {
      // Don't push duplicate
      const hist = tabHistory.value[currentPath]
      if (hist.length === 0 || hist[hist.length - 1] !== currentPath) {
        tabHistory.value[currentPath].push(currentPath)
      }
    }
  }

  function getValidTabs() {
    return tabs.value.filter(t => t.path)
  }

  return { tabs, active, tabHistory, addTab, removeTab, setActive, pushHistory, saveCurrentToHistory, getValidTabs }
}
