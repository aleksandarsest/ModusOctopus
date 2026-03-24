/**
 * 临时存储待上传的文件和需求
 * 用于首页点击启动引擎后立即跳转，在Process页面再进行API调用
 */
import { reactive } from 'vue'

const state = reactive({
  files: [],
  simulationRequirement: '',
  graphBackend: 'local',
  llmConfig: null,
  llmApiKey: '',
  meta: null,
  isPending: false
})

export function setPendingUpload(
  files,
  requirement,
  graphBackend = 'local',
  llmConfig = null,
  llmApiKey = '',
  meta = null
) {
  state.files = files
  state.simulationRequirement = requirement
  state.graphBackend = graphBackend
  state.llmConfig = llmConfig
  state.llmApiKey = llmApiKey
  state.meta = meta
  state.isPending = true
}

export function getPendingUpload() {
  return {
    files: state.files,
    simulationRequirement: state.simulationRequirement,
    graphBackend: state.graphBackend,
    llmConfig: state.llmConfig,
    llmApiKey: state.llmApiKey,
    meta: state.meta,
    isPending: state.isPending
  }
}

export function clearPendingUpload() {
  state.files = []
  state.simulationRequirement = ''
  state.graphBackend = 'local'
  state.llmConfig = null
  state.llmApiKey = ''
  state.meta = null
  state.isPending = false
}

export default state
