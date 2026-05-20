/**
 * ECharts Tech/Cyberpunk 主题配置
 * 用于 AI Console 图表组件
 */

export const techTheme = {
  color: ['#00d4ff', '#1890ff', '#00ff88', '#ff6b6b', '#ffd93d', '#6bcfff', '#a66cff', '#ff9f43'],
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: 'Microsoft YaHei, sans-serif'
  },
  title: {
    textStyle: {
      color: '#ffffff',
      fontSize: 14,
      fontWeight: 'normal'
    },
    subtextStyle: {
      color: '#00d4ff'
    }
  },
  line: {
    itemStyle: {
      borderWidth: 2
    },
    lineStyle: {
      width: 2
    },
    symbolSize: 6,
    smooth: true
  },
  categoryAxis: {
    axisLine: {
      lineStyle: {
        color: 'rgba(0, 212, 255, 0.3)'
      }
    },
    axisTick: {
      lineStyle: {
        color: 'rgba(0, 212, 255, 0.3)'
      }
    },
    axisLabel: {
      color: 'rgba(255, 255, 255, 0.6)',
      fontSize: 11
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(0, 212, 255, 0.1)'
      }
    }
  },
  valueAxis: {
    axisLine: {
      lineStyle: {
        color: 'rgba(0, 212, 255, 0.3)'
      }
    },
    axisTick: {
      lineStyle: {
        color: 'rgba(0, 212, 255, 0.3)'
      }
    },
    axisLabel: {
      color: 'rgba(255, 255, 255, 0.6)',
      fontSize: 11
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(0, 212, 255, 0.1)'
      }
    }
  },
  tooltip: {
    backgroundColor: 'rgba(1, 35, 60, 0.95)',
    borderColor: '#00d4ff',
    borderWidth: 1,
    textStyle: {
      color: '#ffffff'
    }
  },
  legend: {
    textStyle: {
      color: 'rgba(255, 255, 255, 0.7)'
    }
  }
}

export default techTheme
