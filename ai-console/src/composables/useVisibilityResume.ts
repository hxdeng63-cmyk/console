import { onMounted, onUnmounted } from 'vue'
import { useDocumentVisibility } from '@vueuse/core'

export function useVisibilityResume(
  pauseFn: () => void,
  resumeFn: () => void,
) {
  const visibility = useDocumentVisibility()

  function onVisibilityChange() {
    if (visibility.value === 'hidden') {
      pauseFn()
    } else {
      resumeFn()
    }
  }

  onMounted(() => {
    document.addEventListener('visibilitychange', onVisibilityChange)
  })

  onUnmounted(() => {
    document.removeEventListener('visibilitychange', onVisibilityChange)
  })
}